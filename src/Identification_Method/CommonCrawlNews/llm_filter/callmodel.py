import time
import os
import json
import asyncio
from typing import Tuple, Optional
from openai import OpenAI


def call_model(
    system_prompt: str, 
    user_prompt: str,
    model_name: str = "doubao-1-5-pro-32k-250115",
    temperature: float = 0.7,
    max_retries: int = 3
) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """
    调用豆包API进行AI风险关键词筛选
    
    参数:
        system_prompt: 系统提示词，定义模型角色和任务
        user_prompt: 用户输入的待处理内容
        model_name: 模型名称
        temperature: 生成温度，控制输出随机性
        max_retries: 最大重试次数
    
    返回:
        thinking_part: 模型思考过程
        answer_part: 模型正式回答
        tokens: 消耗的token数量
    """
    # 从环境变量获取配置或使用默认值
    llm_url = os.getenv("LLM_URL", "LLM_URL") # 替换为实际的LLM服务地址
    api_key = os.getenv("API_KEY", "API_KEY")

    # 配置检查
    if api_key == "API_KEY":
        logger.warning("使用默认API密钥，可能无法正常工作，请替换为实际密钥")
    
    client = OpenAI(
        base_url=llm_url,
        api_key=api_key
    )

    for attempt in range(max_retries):
        try:
            start_time = time.time()
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                top_p=0.8,
                max_tokens=4096
            )
            
            response_time = time.time() - start_time
            tokens_used = completion.usage.total_tokens if completion.usage else 0
            logger.info(
                f"豆包API调用成功 (尝试 {attempt+1}/{max_retries}) "
                f"| 耗时: {response_time:.2f}秒 "
                f"| Token消耗: {tokens_used}"
            )

            content = completion.choices[0].message.content
            
            # 豆包模型可能不使用特定思考标记，因此将所有内容视为回答
            return None, content.strip(), tokens_used

        except Exception as err:
            logger.error(
                f"豆包API调用失败 (尝试 {attempt+1}/{max_retries}) "
                f"| 错误类型: {type(err).__name__} "
                f"| 错误信息: {str(err)}"
            )
            
            # 重试前等待，指数退避策略
            if attempt < max_retries - 1:
                sleep_time = (attempt + 1) * 2  # 1st: 2s, 2nd: 4s
                logger.info(f"将在 {sleep_time} 秒后重试...")
                time.sleep(sleep_time)

    # 所有重试都失败
    logger.error(f"达到最大重试次数 ({max_retries})，调用失败")
    return None, None, None

# 批量处理函数，适配主程序
async def detect_ai_risk_batches(text_batches, system_prompt):
    """处理批量文本，调用豆包API进行AI风险检测"""
    def fetch_model_response(texts):
        try:
            # 调用豆包模型
            thinking, response_str, tokens = call_model(system_prompt, texts)
            return thinking, response_str, tokens
        except Exception as e:
            logger.error(f"模型请求失败: {e}")
            return (["AIGCrisk_Irrelevant"] * len(json.loads(texts)), 0)

    async def fetch(texts):
        for attempt in range(3):
            try:
                start = time.time()
                thinking, response_str, tokens = fetch_model_response(texts)
                end = time.time()
                logger.info(f"[豆包模型] 批次推理完成,用时{end-start:.2f}秒")

                if not response_str:
                    logger.warning(f"响应为空: {response_str}")
                    return (["AIGCrisk_Irrelevant"] * len(json.loads(texts)), 0)

                # 解析豆包返回的JSON结果
                try:
                    # 查找JSON数组的开始和结束位置
                    start_idx = response_str.find('[')
                    end_idx = response_str.rfind(']')
                    if start_idx != -1 and end_idx != -1:
                        list_str = response_str[start_idx:end_idx + 1]
                        response_list = json.loads(list_str)
                        return response_list, tokens
                    else:
                        logger.warning(f"响应中缺少有效的JSON数组: {response_str[:100]}...")
                except Exception as e:
                    logger.warning(f"响应解析失败: {e}\n原始响应: {response_str[:100]}...")
            except Exception as e:
                logger.error(f"处理失败（第 {attempt+1} 次）: {e}")
            await asyncio.sleep(1)
        # 如果所有尝试都失败，返回默认结果
        return (["AIGCrisk_Irrelevant"] * len(json.loads(texts)), 0)

    tasks = [fetch(batch) for batch in text_batches]
    return await asyncio.gather(*tasks)