import os
import json

# 1. 读取人工标注结果
#这是给定的2000条AI新闻的人工标注结果，标注结果是是否与AI风险相关
current_dir = os.path.dirname(os.path.abspath(__file__))
label_result_path = os.path.join(current_dir, "../../data/standard_incidents_classification.json")
with open(label_result_path , 'r', encoding='utf-8') as f:
    human_data = json.load(f)

# name -> 是否相关
human_labels = {
    item['name']: item['sentiment'] == '有关' for item in human_data
}

# 2. 从筛选目录读取模型判断为“相关”的 name（去除 .txt 后缀）
# 注意：这里的 filtered_dirs 需要替换为实际的目录列表 这里的目录列表实际上是指使用已经被llm过滤为AI风险相关新闻的目录 相关代码在Data_Processing/data_filter/CommonCrawlNews/llm_filter中

month_1=os.path.join(current_dir, "../../download_dir/CCN-AI-news/2023/1")
month_2=os.path.join(current_dir, "../../download_dir/CCN-AI-news/2023/2")
# 这里假设给定的2000条AI风险新闻是2023年1月和2月的，那么计算指标可以这样完成。如果你的数据集包含其他月份的AI风险新闻，请相应地调整目录。
# 这里假设2023年1月和2月的AI风险新闻存放在这两个目录中
filtered_dirs = [month_1, month_2]

model_predicted_relevant = set()

for folder in filtered_dirs:
    for filename in os.listdir(folder):
        if filename.endswith('.txt'):
            #name = filename.replace('.txt', '')
            model_predicted_relevant.add(filename)

# 3. 评估指标
true_positives = 0
false_positives = 0
false_negatives = 0

for name, is_relevant in human_labels.items():
    if name in model_predicted_relevant:
        if is_relevant:
            true_positives += 1
        else:
            false_positives += 1
    else:
        if is_relevant:
            false_negatives += 1

# 4. 计算指标
precision = true_positives / (true_positives + false_positives + 1e-8)
recall = true_positives / (true_positives + false_negatives + 1e-8)
print(f"TP: {true_positives}, FP: {false_positives}, FN: {false_negatives}")
print(f"准确率（Precision）: {precision:.4f}")
print(f"召回率（Recall）: {recall:.4f}")
