import os
import time
import json
import logging
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import configparser
import threading  # 用于线程安全的计数器
from callmodel import call_model, detect_ai_risk_batches  # 豆包API调用模块
# 注意根据实际调用的API修改导入路径和函数名
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "../../../config/Identification_Method-CommonCrawlNews-llm_filter-config.ini")
# 初始化配置
config = configparser.ConfigParser()

config.read(config_path)
CCN_config = config["CommonCrawlNews"]
year = CCN_config.get("year", "2024")
months_str = CCN_config.get("months", "1,2,3,4,5,6,7,8,9,10,11,12")
months = [int(m.strip()) for m in months_str.split(",")]

SELECTED_YM = [os.path.join(year,m) for m in months] 

BASE_INPUT_DIR = os.path.join(current_dir,CCN_config.get("BASE_INPUT_DIR"))
BASE_OUTPUT_DIR = os.path.join(current_dir,CCN_config.get("BASE_OUTPUT_DIR"))  # 输出目录
LOG_FILE = os.path.join(current_dir,CCN_config.get("LOG_FILE"))
CONTENT_LIMIT = CCN_config.getint("CONTENT_LIMIT", 10000)  # 默认内容限制为10000字符
MAX_THREADS = CCN_config.getint("MAX_THREADS", 5)  # 默认线程数为5
BATCH_SIZE = CCN_config.getint("BATCH_SIZE", 5)  # 每批处理5个文件


# 日志配置
def setup_logger():
    logger = logging.getLogger("batch_logger")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    # 文件和控制台日志
    file_handler = logging.FileHandler(LOG_FILE, mode='w')
    console_handler = logging.StreamHandler()
    error_handler = logging.FileHandler(ERROR_LOG_FILE, mode='w')

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(processName)s - %(message)s')
    for handler in [file_handler, console_handler, error_handler]:
        handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)

    return logger

logger = setup_logger()


# 构建目标文件路径
prompt_path = os.path.join(current_dir, "../../../prompt/Identification_Method-CommonCrawlNews-llm_filter-prompt.ini")
with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_content = f.read()
# 提示词
PROMPT = str(prompt_content)
def prepare_input_for_model(batch_data):
    """格式化输入为5条文章的JSON列表"""
    input_data = [{"title": title, "content": content} for _, title, content in batch_data]
    return json.dumps(input_data, ensure_ascii=False)

async def process_single_batch(batch_data, output_root):
    """处理单个批次，输出路径不含texts文件夹"""
    try:
        texts = prepare_input_for_model(batch_data)
        results_and_tokens = await detect_ai_risk_batches([texts], PROMPT)
        relevant_count = 0
        results, total_tokens = results_and_tokens[0]

        if len(results) != len(batch_data):
            logger.warning(f"结果长度不匹配，预期{len(batch_data)}，实际{len(results)}")
            return 0, total_tokens

        for (fpath, title, original_txt), result in zip(batch_data, results):
            if result == 'AIGCrisk_relevant':
                try:

                    parent_dir = fpath.parent  # 得到"BASE_INPUT_DIR/2022/5/texts"
                    year_month_dir = parent_dir.parent  # 得到"BASE_INPUT_DIR/2022/5"
                    rel_path = year_month_dir.relative_to(BASE_INPUT_DIR)  # 得到"2022/5"
                    output_dir = Path(output_root) / rel_path  # 输出目录：BASE_OUTPUT_DIR/2022/5
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    out_path = output_dir / f"{fpath.stem}.txt"
                    if not out_path.exists():
                        combined = f"{title}\n{original_txt}"[:CONTENT_LIMIT]
                        out_path.write_text(combined, encoding="utf-8", errors="ignore")
                        relevant_count += 1
                except Exception as e:
                    logger.error(f"保存文件失败 {fpath}: {e}")

        return relevant_count, total_tokens
    except Exception as e:
        logger.error(f"批次处理失败: {e}")
        return 0, 0

def worker_thread(batch, output_root, counter_lock, global_counter):
    """线程工作函数（替代原worker_process）"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        relevant_count, tokens = loop.run_until_complete(
            process_single_batch(batch, output_root)
        )
        loop.close()
        
        # 线程安全更新计数器（用threading.Lock）
        with counter_lock:
            global_counter[0] += 1  # 用列表存储计数器，实现可变对象共享
            current = global_counter[0]
            if current % 100 == 0:  # 每100批次输出一次进度（更频繁监控）
                logger.info(f"全局已处理 {current} 批次")
            if current % 1000 == 0:
                logger.info(f"全局已处理 {current} 批次，休眠120秒...")
                time.sleep(120)
                
        return relevant_count, len(batch), tokens
    except Exception as e:
        logger.error(f"线程处理失败: {e}")
        return 0, len(batch), 0

def main():
    start = time.time()
    
    # 1. 收集文件（逻辑不变）
    all_files = []
    for ym in SELECTED_YM:
        ym_dir = Path(BASE_INPUT_DIR) / ym
        if not ym_dir.is_dir():
            logger.warning(f"年月目录不存在：{ym_dir}")
            continue
        
        texts_dir = ym_dir / "texts"
        if not texts_dir.exists() or not texts_dir.is_dir():
            logger.info(f"无texts文件夹，跳过：{ym_dir}")
            continue
        
        txt_files = list(texts_dir.rglob("*.txt"))  # 递归查找
        all_files.extend(txt_files)
        logger.info(f"从 {texts_dir} 收集到 {len(txt_files)} 个文件")
    
    if not all_files:
        logger.info("未找到任何txt文件，退出")
        return
    
    logger.info(f"共收集 {len(all_files)} 个文件，使用 {MAX_THREADS} 线程处理")
    
    # 2. 创建输出目录（不变）
    output_root = Path(BASE_OUTPUT_DIR)
    output_root.mkdir(parents=True, exist_ok=True)
    
    # 3. 划分批次（不变）
    batches = []
    for i in range(0, len(all_files), BATCH_SIZE):
        batch_files = all_files[i:i+BATCH_SIZE]
        batch_data = []
        for fpath in batch_files:
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    title = f.readline().strip()
                    content = f.read().strip()
                batch_data.append((fpath, title, content))
            except Exception as e:
                logger.error(f"读取文件失败 {fpath}: {e}")
        if batch_data:
            batches.append(batch_data)
    
    logger.info(f"文件已分为 {len(batches)} 个批次（每批最多{5}个）")
    
    # 4. 多线程处理（核心修改）
    global_counter = [0]  # 用列表实现线程间共享的计数器（可变对象）
    counter_lock = threading.Lock()  # 线程安全的锁
    
    # 用ThreadPoolExecutor替代Pool
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # 构建线程任务参数（传递锁和计数器）
        worker_args = [
            (batch, output_root, counter_lock, global_counter) 
            for batch in batches
        ]
        # 提交所有任务并获取结果
        results = list(executor.map(
            lambda x: worker_thread(x[0], x[1], x[2], x[3]), 
            worker_args
        ))
    
    # 5. 汇总结果（不变）
    total_relevant = 0
    total_processed = 0
    total_tokens = 0
    for rel, processed, tokens in results:
        total_relevant += rel
        total_processed += processed
        total_tokens += tokens
    
    # 输出统计（不变）
    duration = time.time() - start
    logger.info(f"\n===== 处理完成 =====")
    logger.info(f"总耗时: {duration:.2f}秒")
    logger.info(f"总处理文件: {total_processed}")
    logger.info(f"风险相关文件: {total_relevant}")
    if total_processed > 0:
        logger.info(f"相关比例: {100 * total_relevant / total_processed:.2f}%")
    logger.info(f"总Token消耗: {total_tokens}")

if __name__ == "__main__":
    main()