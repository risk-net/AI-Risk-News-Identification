#这个文件是用来筛选OpenNewsArchive中AI相关的新闻的
#通过调用关键词过滤器来筛选新闻内容
#注意修改关键词文件路径，日志文件路径，和输入输出目录
import os
import json
from functools import partial
from multiprocessing import Pool
# 初始化NLTK（这里假设你已经安装并配置好NLTK）
import nltk
current_dir = os.path.dirname(os.path.abspath(__file__))
keywords_file= os.path.join(current_dir, "../../../keyword/Identification_Method-OpenNewsArchive-keyword_filter-keywords.txt")# 关键词文件路径

# 关键词处理
class KeywordProcessor:
    def __init__(self):
        self.keywords = self._load_keywords()
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.en_stopwords = set(nltk.corpus.stopwords.words('english'))

    def _load_keywords(self):
        try:
            with open(keywords_file, 'r', encoding='utf-8') as f:
                return set(line.strip().lower() for line in f if line.strip())
        except Exception as e:
            logger.error(f"Failed to load keywords: {e}")
            return set()

    def extract_keywords(self, text, lang, top_n=10):
        if lang == 'zh':
            import jieba.analyse
            return set(jieba.analyse.extract_tags(text, topK=top_n, withWeight=False))
        elif lang == 'en':
            tokens = [self.lemmatizer.lemmatize(t.lower())
                      for t in nltk.word_tokenize(text)
                      if t.isalpha() and t.lower() not in self.en_stopwords]
            return set(w for w, _ in nltk.FreqDist(tokens).most_common(top_n))
        return set()

keyword_processor = KeywordProcessor()

def process_jsonl_file(file_path):
    ai_related_news = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                content = data.get('content', '')
                lang = data.get('language', 'unknown')

                keywords = keyword_processor.extract_keywords(content, lang)
                if keyword_processor.keywords.intersection(keywords):
                    ai_related_news.append(data)
                    logger.info(f"Found AI-related news with ID: {data.get('id', 'unknown')} from file {file_path}")
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
    return ai_related_news

def main(input_dir):
    jsonl_files = [os.path.join(root, f)
                   for root, _, files in os.walk(input_dir)
                   for f in files if f.endswith(".jsonl")]

    logger.info(f"Processing {len(jsonl_files)} JSONL files")

    num_workers = min(8, os.cpu_count())
    with Pool(num_workers) as pool:
        results = pool.map(process_jsonl_file, jsonl_files)

    all_ai_news = [news for sublist in results for news in sublist]

    logger.info(f"Found {len(all_ai_news)} AI-related news in total")

    # 可以在这里将筛选出的新闻保存到文件中
    output_file = os.path.join(current_dir, "../../../data/OpenNewsArchive-ai_related_news.jsonl")
    with open(output_file, 'w', encoding='utf-8') as f:
        for news in all_ai_news:
            f.write(json.dumps(news, ensure_ascii=False) + "\n")
    # 假设jsonl文件名为data.jsonl，你可以根据实际情况修改

    save_folder_path = os.path.join(current_dir, "../../../data/OpenNewsArchive-AI_news")

    # 读取jsonl文件
    with open(output_file, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line.strip())
            file_name = data["id"] + ".txt"
            text_content = data["title"] +"\n" +data["content"] if data["title"] else data["content"]
            save_file_path = os.path.join(save_folder_path, file_name)
            with open(save_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(text_content)
if __name__ == "__main__":
    input_directory = os.path.join(current_dir,"../../../download_dir/OpenNewsArchive/OpenDataLab___OpenNewsArchive/zh") 
    # 替换为你的下载输入目录
    # 这里假设下载目录为OpenNewsArchive/zh   具体根据实际情况修改
    main(input_directory)
    