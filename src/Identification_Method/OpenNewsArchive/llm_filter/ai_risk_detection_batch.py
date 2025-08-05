import os
import time
import json
import logging
import asyncio
import random
from pathlib import Path
from bs4 import BeautifulSoup
import numpy as np
from callmodel import call_model
import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import configparser

current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "../../../../config/Identification_Method-OpenNewsArchive-llm_filter-config.ini")
# 初始化配置
config = configparser.ConfigParser()

config.read(config_path)
ONA_config = config["OpenNewsArchive"]
BASE_INPUT_DIR = os.path.join(current_dir,ONA_config.get("BASE_INPUT_DIR"))
BASE_OUTPUT_DIR = os.path.join(current_dir,ONA_config.get("BASE_OUTPUT_DIR"))  # 输出目录
LOG_FILE = os.path.join(current_dir,ONA_config.get("LOG_FILE"))
#BATCH_SIZE = 10
CONTENT_LIMIT = ONA_config.getint("CONTENT_LIMIT", 10000)  # 默认内容限制为10000字符

# === 全局推理计数器 ===
global_inference_counter = 0

prompt_path= os.path.join(current_dir, "../../../../prompt/Identification_Method-OpenNewsArchive_Datasets-llm_filter-prompt.md")
with open(prompt_path, 'r', encoding='utf-8') as f:
    md_content = f.read()
# 提示词
PROMPT = str(md_content)


async def detect_ai_risk_batches(text_batches, system_prompt=PROMPT):
    def fetch_model_response(texts):
        global global_inference_counter
        try:
            formatted_input = texts  # 这里是 JSON 格式的文本
            response,tokens= call_model(system_prompt, formatted_input)
            # 计数推理次数
            global_inference_counter += 1
            if global_inference_counter % 1000 == 0:
                logger.info(f"🚦 已推理 {global_inference_counter} 次，休眠 120 秒以防止堵塞...")
                time.sleep(120)  # 用 time.sleep 这里就够了，因为是在同步部分
            return response,tokens
        except Exception as e:
            logger.error(f"🛑 本地模型请求失败: {e}")
            return (["AIGCrisk_Irrelevant"] * len(texts), 0)

    async def fetch(texts):
        for attempt in range(3):
            try:
                start=time.time()
                response_str,tokens= fetch_model_response(texts)
                end=time.time()
                logger.info(f"[Model] 批次推理完成,用时{end-start:.2f}秒")
                #print(f"response_str: 1{response_str}2")
                if not response_str:
                    logger.warning(f"⚠️ 响应为空或缺少 'response' 字段:")
                    return (["AIGCrisk_Irrelevant"] * len(texts), 0)

                if isinstance(response_str, str):
                    try:
                        start_idx = response_str.find('[')
                        end_idx = response_str.rfind(']')
                        if start_idx != -1 and end_idx != -1:
                            list_str = response_str[start_idx:end_idx + 1]
                            if list_str.startswith('"') and list_str.endswith('"'):
                                list_str = list_str[1:-1]
                            response_list = json.loads(list_str)
                            return response_list,tokens
                        else:
                            logger.warning(f"⚠️ 响应中缺少中括号: {response_str[:]}")
                    except Exception as e:
                        logger.warning(f"⚠️ 响应解析失败: {e}\n原始 response 字符串: {response_str[:]}")
            except TimeoutError as e:
                logger.error(f"⏱️ API 请求超时（第 {attempt+1} 次）: {e}")
            except Exception as e:
                logger.error(f"🛑 未知错误（第 {attempt+1} 次）: {type(e).__name__}: {e}")
            await asyncio.sleep(1)
        return (["AIGCrisk_Irrelevant"] * len(texts), 0)
    tasks = [fetch(batch) for batch in text_batches]
    return await asyncio.gather(*tasks)
# 将输入格式转换为 JSON，结构化的发送给模型
def prepare_input_for_model(batch_data):
    # 格式化输入为 JSON，每个新闻为一个对象，包括标题和正文
    input_data = [{"title": title, "content": content} for _, title, content in batch_data]
    return json.dumps(input_data, ensure_ascii=False)

async def handle_batch(batch_data, output_dir):
    #批次推理与文件处理
    texts = prepare_input_for_model(batch_data)
    results_and_tokens = await detect_ai_risk_batches([texts])
    relevant_count = 0
    results, total_tokens = results_and_tokens[0]
    for (fpath, title, original_txt), result in zip(batch_data, results):
        logger.info(f"文件已处理: {fpath.stem}.txt | 结果: {result}")
    # 记录本批次的 tokens
    logger.info(f"本批次使用tokens: {total_tokens}")
    for (fpath, title, original_txt), result in zip(batch_data, results):
        if result == 'AIGCrisk_relevant':
            try:
                combined = f"{title}\n{original_txt}"[:CONTENT_LIMIT]
                out_path = output_dir / f"{fpath.stem}.txt"
                if out_path.exists():
                    logger.warning(f"文件已存在，拒绝覆盖: {out_path}")
                    continue
                else:
                    out_path.write_text(combined, encoding="utf-8", errors="ignore")

                logger.info(f"✅ 保存风险文本: {fpath.stem}.txt ")
                relevant_count += 1
            except Exception as e:
                logger.error(f"❌ 保存失败: {e}")
    return relevant_count,total_tokens

async def main():
    start = time.time()
    total_files = 0
    relevant_files = 0
    total_tokens_per_batch = {3: []}  # 用于存储不同批次的tokens数量

    ym_dirs=[Path(BASE_INPUT_DIR)]#与月份无关
    for ym_dir in ym_dirs:
        txt_files = list(ym_dir.glob("*.txt"))
        if not txt_files:
            
            continue

        #html_files = random.sample(html_files, min(len(html_files), 1500))
        
        logger.info(f"处理目录: {ym_dir} 随机抽取 {len(txt_files)} 个文件")

        rel_path = ym_dir.relative_to(BASE_INPUT_DIR)
        print(f"rel_path: {rel_path}")
        output_dir = Path(BASE_OUTPUT_DIR) / rel_path
        print(f"output_dir: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

        batch_data = []
        for batch_size in [3]:  # 依次测试批次大小为5, 10, 15的情况
            logger.info(f"开始处理批次大小: {batch_size}")
            for txt_path in txt_files:
                try:
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        title = f.readline().strip()
                        content = f.read().strip()


                    batch_data.append((txt_path, title, content))
                    logger.info(f"添加到批次: {txt_path.name} | 批次大小: {len(batch_data)}")
                    if len(batch_data) >= batch_size:
                        relevant_count, batch_tokens = await handle_batch(batch_data, output_dir)
                        relevant_files += relevant_count
                        total_files += len(batch_data)
                        total_tokens_per_batch[batch_size].append(batch_tokens)  # 记录每个批次的tokens数量
                        batch_data.clear()  # 清空batch_data，准备下一个批次

                except Exception as e:
                    logger.error(f"处理文件失败 {html_path}: {e}")

            # 处理剩余的文件
            if batch_data:
                relevant_count, batch_tokens = await handle_batch(batch_data, output_dir)
                relevant_files += relevant_count
                total_files += len(batch_data)
                total_tokens_per_batch[batch_size].append(batch_tokens)  
    # 计算每种批次大小的平均tokens
    for batch_size, tokens_list in total_tokens_per_batch.items():
        avg_tokens = np.mean(tokens_list) if tokens_list else 0
        logger.info(f"批次大小 {batch_size}: 平均使用 {avg_tokens:.2f} tokens")
    logger.info(f"🕒 总耗时：{time.time() - start:.2f}s")
    if total_files > 0:
        rate = 100 * relevant_files / total_files
        logger.info(f"📊 总共处理 {total_files} 篇新闻，风险相关 {relevant_files} 篇，比例 {rate:.2f}%")
    else:
        logger.info("📭 未处理任何文件")

if __name__ == "__main__":

    asyncio.run(main())
