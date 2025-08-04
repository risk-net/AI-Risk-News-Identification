import pandas as pd
import pandas as pd
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建目标文件路径
AIID_reports_path = os.path.join(current_dir, "../../../data/AIID_reports.csv")
AIID_incidents_path = os.path.join(current_dir, "../../../data/AIID_incidents.csv")
AIID_incidents_jsonl = os.path.join(current_dir, "../../../data/AIID_incidents.jsonl")
AIID_cases_jsonl = os.path.join(current_dir, "../../../data/AIID_cases.jsonl")
df=pd.read_csv(AIID_reports_path)

# 遍历 DataFrame，将内容反向映射到 aiid_data_db
cases = {}
for index, row in df.iterrows():
    obj= {
        "aiid_id":row["report_number"],
        "title":row['title'] ,
        'text':row['text'],
        "release_date": row['date_published'],
        "case_link" :  row['url'],
    }
        # 合并后的数据
    cases[row['url']]=obj
    # 将 unique_result 转换为列表
cases = list(cases.values())
cases.sort(key=lambda x: x['aiid_id'])
# Use a raw string to avoid escape character issues

df2 = pd.read_csv(AIID_incidents_path)
df2.head()
incidents = {}
for index, row in df2.iterrows():
    incident_id = row['incident_id']
    related_cases = row['reports']

    incident_description = row['description']
    incident_title = row['title']
    obj = {
        "incident_id": incident_id,
        "cases": [case.strip() for case in related_cases.replace("[","").replace("]","").split(",")],
        "incident_description": incident_description,
        "incident_title": incident_title
    }
    incidents[incident_id] = obj
incidents = list(incidents.values())
incidents.sort(key=lambda x: x['incident_id'])



# 将 incidents 写入 JSONL 文件
with open(AIID_incidents_jsonl, 'w', encoding='utf-8') as f:
    for incident in incidents:
        f.write(json.dumps(incident, ensure_ascii=False) + '\n')

# 将 cases 写入 JSONL 文件
with open(AIID_cases_jsonl, 'w', encoding='utf-8') as f:
    for case in cases:
        f.write(json.dumps(case, ensure_ascii=False) + '\n')

print("数据已成功导出为 JSONL 文件！")