#这个文件使用使用大模型来筛选标题是否与AIGC风险相关
#注意修改csv文件名称，路径

import pandas as pd
import requests
import logging # 引入日志模块
from callmodel import call_model
import os
# 读取CSV文件
current_dir = os.path.dirname(os.path.abspath(__file__))
filter_dataset_file= os.path.join(current_dir, "../../../../download_dir/filtered_douyin_hotlist.csv")# 关键词文件路径
#注意修改csv文件名称，路径
# 这里注意修改为对应的过滤后热搜词csv文件路径
df = pd.read_csv(filter_dataset_file)
prompt_path = os.path.join(current_dir, "../../../../prompt/Identification_Method-Hot_list_word_Datasets-llm_filter-prompt.md")
with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_content = f.read()
# 提示词
system_prompt= str(prompt_content)

# 筛选包含关键词的行
filtered_titles = []

for i in range(0, len(df), 5):
    batch = df.iloc[i:i+5]
    titles = str(batch['title'].tolist())
    response = call_model(system_prompt,titles)
    results = eval(response)  # 将字符串转换为列表
    print(f"第 {i} 到 {i+5} 条已完成")
    for j, result in enumerate(results):
        if result == 1:
            filtered_titles.append(batch.iloc[j])

# 将筛选后的数据保存到新的CSV文件
filtered_df = pd.DataFrame(filtered_titles)
filter_dataset_csv_path = os.path.join(current_dir, "../../../../download_dir/filtered_llm_dataset.csv")
#注意修改csv文件名称，路径
filtered_df.to_csv(filter_dataset_csv_path, index=False)