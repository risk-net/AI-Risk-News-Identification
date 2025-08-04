# 用于从 AIAAIC 数据集中抓取新闻并提取风险案例信息的脚本
import json
import asyncio
from typing import Dict, List
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from case_model import RiskCaseCreate



current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建目标文件路径
prompt_path = os.path.join(current_dir, "../../../prompt/Data_Sources-AIAAIC-prompt.md")
with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_content = f.read()
# 提示词
PROMPT = str(prompt_content)
# 大模型配置
llmextraction_strategy = LLMExtractionStrategy(

    llm_config=LLMConfig(provider="model_provider", base_url="model_url", api_token='your_api_token'),
    # 模型名称,模型地址和模型API密钥需要替换为实际的值
    schema=RiskCaseCreate.model_json_schema(),
    extraction_type="schema",
    instruction=PROMPT,
    chunk_token_threshold=2000,
    overlap_rate=0.1,
    apply_chunking=True,
    input_format="markdown",
)
# 浏览器配置
browser_config = BrowserConfig(headless=True, verbose=True, user_agent_mode="random")

# 爬虫配置
crawler_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    word_count_threshold=15,
    page_timeout=10000,
    scan_full_page=True,
    extraction_strategy=llmextraction_strategy,
    stream=True  # Enable streaming mode
)

async def async_crawl(out_put_file,error_file,urls):
    async with AsyncWebCrawler(config=browser_config) as crawler:
        async for result in await crawler.arun_many(urls, config=crawler_config):
            if result.success:
                try:
                    data = json.loads(result.extracted_content)
                    print("[ok]抽取成功:\n", data)
                    with open(out_put_file, "a", encoding="utf-8") as f:
                        data[0].update({"from_url": result.url})
                        json.dump(data[0], f, ensure_ascii=False)  # 写入 JSON 数据
                        f.write("\n")  # 每条数据后换行
                    print(f"[OK] {result.url}, 数据已保存.")
                except json.JSONDecodeError as e:
                    print(f"[抽取时 JSON 解析错误]{result.url}: {str(e)}")
                    print(f"Extracted content: {result.extracted_content}")
                    with open(error_file, "a") as f2:
                        f2.write(result.url)
                        f2.write("\n")
                except Exception as e:
                    # 修正异常信息打印
                    print(f"[抽取时出错]{result.url}: {str(e)}")
                    with open(error_file, "a") as f2:
                        f2.write(result.url)
                        f2.write("\n")
            else:
                with open(error_file, "a") as f2:
                    f2.write(result.url)
                    f2.write("\n")
                print(f"[ERROR] {result.url} => {result.error_message}")
    return async_crawl()
def read_jsonl_to_dict(file_path):
        result_dict = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    try:
                        json_obj = json.loads(line)
                        # 将解析出的键值对更新到结果字典中
                        result_dict.update(json_obj)
                    except json.JSONDecodeError:
                        print(f"解析 JSON 时出错，行内容: {line}")
        except FileNotFoundError:
            print(f"错误: 文件 {file_path} 未找到，请检查文件路径。")
        except Exception as e:
            print(f"发生未知错误: {e}")
        return result_dict
if __name__ == "__main__":

    urls=[]
    urls1=[]
    urls2=[]
    urls3=[]
    aiaaic_data_path = os.path.join(current_dir, "aiaaic_processed_data.jsonl")
    aiaaic_dict = read_jsonl_to_dict(aiaaic_data_path)   
    # 输出读取到的数据
    for id, detail in aiaaic_dict.items():
        urls.extend(detail.get("parsed_links"))
    
    # 构建目标文件路径
    AIAAIC_output_path = os.path.join(current_dir, "../../../data/AIAAIC_output.jsonl")
    AIAAIC_error_path = os.path.join(current_dir, "../../../error/AIAAIC_error.jsonl")
    # 注意修改输出文件路径
    asyncio.run(async_crawl(out_put_file=AIAAIC_output_path,urls=urls,error_file=AIAAIC_error_path))





