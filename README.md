# AI-Risk-News-Identification
Identify general news to AI risk news


> 📖 Read this in [中文](./README_zh-CN.md)
# Project structure
For detailed project structure, see structure.txt

# Source code section

The source code is mainly divided into three parts, one is data acquisition, the other is data filtering, and the third is method verification in standard datasets. Among them, the data acquisition part is the acquisition code of all data sources in this database, and the data filtering part is the filtering code that needs to filter from all data to AI risk news data. Method verification mainly consists of two parts. 1) It is keyword screening, a method effect test that filters general news into AI-related news, and 2) It is llm screening, a method effect test that filters AI-related news into AI-dedicated news.

## Data source acquisition

There are six main data sources, namely AIID, AIAAIC, CommonCrawlNews, OpenNewsArchive, Crawled_Dataset and Hot-list-word_Dataset.
Among them, AIID and AIAAIC are small datasets formed by previous similar work, CommonCrawlNews, OpenNewsArchive are large general news datasets, Crawled_Dataset are datasets crawled on news websites according to keywords, and Hot-list-word_Dataset are datasets of hot-list words obtained from various social media hot-list words.

### AIDS
Process incident and case data in the AIID database for download
### AIAAIC
Process the event link in the AIAAIC database, get the case link corresponding to the event through the crawler, and then use the llm crawl page to get the news content through crawl4ai
### CommonCrawlNews
Download CommonCrawlNews in commoncrawl, download it as a warc file format, and you need to process the wacr file later.
### OpenNewsArchive
Download the OpenNewsArchive dataset in jsonl format.
### Crawl_Dataset
Relevant datasets crawled on 5 Chinese news websites through AI risk keywords
### Hot-list - word_Dataset
Get the hot words of Douyin, Toutiao, v2ex, Weibo and Zhihu through the douyin-hot-hub project

## recognition method

### CommonCrawlNews
First extract the news content from the WARC file, perform AI keyword filtering, and save the valid content
Text processing using multi-process and NLTK
Get AI-related news

Secondly, call qwen2.5 to screen AI news for risk news
Then use qwen3 for risk news second-round screening

### Other datasets

The processing flow, similar, is also to use keywords to form AI news first, and then perform two rounds of screening through large models

## Keyword filtering method verification
Verify the effectiveness of the "keyword filtering AI-related news" step using the cases.jsonl standard dataset in the data project

Since the standard dataset is derived from two datasets, AIID and AIAAIC, both of which have passed manual tests, it is considered to be true news related to AI.
### specific method

The specific method is to use nltk and jieba to word the article, and then intersect with AI keywords. If there is an intersection, it means that the news is AI-related news. It should be noted that during the word segmentation process, it is necessary to determine some fixed phrases, such as Artificial Intelligence. When encountering this word, it needs to be regarded as a whole, and additional operations are performed in the code to ensure that it is not divided into two words.

### test result

After testing, a total of 9,131 AI-related news were found using this method, and 430 non-AI-related news were found, accounting for 95.50% of AI-related news.
In other words, the recall rate for AI-related news has reached 95%.
This confirms the rationality of first performing AI-related news filtering on subsequent full news datasets

## llm filter method verification

Verify the effectiveness of the "LLM filtering AI risk related news" step using the label_news_result_final standard dataset in the data project

### test result

After testing, among 2000 randomly selected AI news, the LLM filtering method recalled 606 AI risk news, of which 473 were correct AI risk news, with an accuracy rate of 78.05%. In fact, there were 618 AI risk news among the two thousand, with a recall rate of 76.54%
TP: 473, FPA: 133, FN: 145
Accuracy: 0.7805
Recall Rate (Recall): 0.7654

## Other folder introduction

The config folder is mainly used to store the configuration files in each step
The data folder is mainly used to store evaluation datasets and standard datasets. There are independent readme files in the data dataset
download_dir folder is mainly used to store the downloaded data sets and intermediate data sets, the project is empty, if you need to get it, you need to run the download yourself
The keywords folder is mainly used to store the keyword files in each step
The logs folder is mainly used to store the log files in each step
The prompt folder is mainly used to store the prompt word files in each step