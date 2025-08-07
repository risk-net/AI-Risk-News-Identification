#这个文件是用来筛选OpenNewsArchive中AI相关的新闻的
#通过调用关键词过滤器来筛选新闻内容
#注意修改关键词文件路径，日志文件路径，和输入输出目录
import os
import json
from functools import partial
from multiprocessing import Pool
# 初始化NLTK（这里假设你已经安装并配置好NLTK）
import nltk
import configparser
import ahocorasick
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "../../../../config/Identification_Method-OpenNewsArchive-keyword_filter-config.ini")
# 初始化配置
config = configparser.ConfigParser()

config.read(config_path)
ONA_config = config["OpenNewsArchive"]
BASE_INPUT_DIR = os.path.join(current_dir,ONA_config.get("BASE_INPUT_DIR"))
BASE_OUTPUT_DIR = os.path.join(current_dir,ONA_config.get("BASE_OUTPUT_DIR"))  # 输出目录
JSONL_FILE = os.path.join(current_dir,ONA_config.get("JSONL_FILE"))
KEYWORDS_FILE = os.path.join(current_dir, ONA_config.get("KEYWORDS_FILE"))
PHRASES_FILE = os.path.join(current_dir, ONA_config.get("PHRASES_FILE"))

class PhraseMatcher:
    def __init__(self, phrase_file):
        self.automaton = ahocorasick.Automaton()
        self._load_phrases(phrase_file)

    def _load_phrases(self, phrase_file):
        with open(phrase_file, 'r', encoding='utf-8') as f:
            for line in f:
                phrase = line.strip()
                if phrase:
                    self.automaton.add_word(phrase.lower(), phrase.lower())
        self.automaton.make_automaton()

    def find_matches(self, text):
        text = text.lower()
        return {match for _, match in self.automaton.iter(text)}


class KeywordProcessor:
    def __init__(self):
        self.keywords = self._load_keywords()
        self.lemmatizer = WordNetLemmatizer()
        self.en_stopwords = set(stopwords.words('english'))
        self.phrase_matcher = PhraseMatcher(PHRASES_FILE)

    def _load_keywords(self):
        try:
            with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
                return set(line.strip().lower() for line in f if line.strip())
        except Exception as e:
            logger.error(f"Failed to load keywords: {e}")
            return set()

    def extract_keywords(self, text, lang, top_n=10):
        lower_text = text.lower()
        phrase_matches = self.phrase_matcher.find_matches(lower_text)

        phrase_tokens = set()
        for phrase in phrase_matches:
            if lang == 'en':
                phrase_tokens.update(word_tokenize(phrase))
            elif lang == 'zh':
                phrase_tokens.update(jieba.lcut(phrase))

        residual_keywords = set()

        if lang == 'en':
            tokens = [
                self.lemmatizer.lemmatize(t.lower())
                for t in word_tokenize(lower_text)
                if t.isalpha() and t.lower() not in self.en_stopwords and t.lower() not in phrase_tokens
            ]
            residual_keywords = {w for w, _ in nltk.FreqDist(tokens).most_common(top_n)}

        elif lang == 'zh':
            tokens = [t for t in jieba.lcut(text) if t not in phrase_tokens]
            freq = {}
            for token in tokens:
                if len(token) > 1:
                    freq[token] = freq.get(token, 0) + 1
            residual_keywords = set(sorted(freq, key=freq.get, reverse=True)[:top_n])

        return phrase_matches.union(residual_keywords)

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
    output_file = JSONL_FILE # 输出文件路径
    with open(output_file, 'w', encoding='utf-8') as f:
        for news in all_ai_news:
            f.write(json.dumps(news, ensure_ascii=False) + "\n")
    # 假设jsonl文件名为data.jsonl，你可以根据实际情况修改

    save_folder_path = BASE_OUTPUT_DIR

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
    input_directory = BASE_INPUT_DIR
    # 替换为你的下载输入目录
    # 这里假设下载目录为OpenNewsArchive/zh   具体根据实际情况修改
    # 输入目录应该包含多个jsonl文件
    # 如果输入的数据结构不一致，请根据实际情况调整主函数，具体处理函数不用调整
    main(input_directory)
    