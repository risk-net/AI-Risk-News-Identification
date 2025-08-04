# AI-Risk-News-Identification
Identify general news to AI risk news> 

📖 View this in [English](./README.md)
# 项目结构
详细项目结构见structure.txt
# 源代码部分

源代码主要分为三个部分，一是数据获取，二是数据过滤，三是在标准数据集的方法校验。这其中，数据获取部分是本数据库所有数据源的获取代码，数据过滤部分是需要从全部数据过滤到AI风险新闻数据的过滤代码，方法校验主要是两个，1）是关键词筛选，将一般新闻筛选为AI相关新闻的方法效果测试，2）是llm筛选，将AI相关新闻筛选为AI奉献新闻的方法效果测验。

## 数据源获取

数据源主要有六个，分别是AIID,AIAAIC,CommonCrawlNews,OpenNewsArchive,Crawled_Dataset和Hot-list-word_Dataset。
这其中AIID和AIAAIC是先前类似工作形成的小型数据集，CommonCrawlNews,OpenNewsArchive是大型的普通新闻数据集，Crawled_Dataset是自行根据关键词在新闻网站上爬取的数据集，Hot-list-word_Dataset是根据各社交媒体热榜词获取的热榜词数据集。

### AIID
处理AIID数据库中供下载的事件与案例数据
### AIAAIC 
处理AIAAIC数据库中的事件链接，通过爬虫获取事件对应的案例链接，再通过crawl4ai使用llm爬取页面获取新闻内容
### CommonCrawlNews
下载commoncrawl中的CommonCrawlNews，下载为warc文件格式，后续需要处理wacr文件
### OpenNewsArchive
下载OpenNewsArchive数据集，下载格式为jsonl
### Crawl_Dataset
通过AI风险关键词在中国5个新闻网站上爬取的相关数据集
### Hot-list-word_Dataset
通过douyin-hot-hub项目获取抖音，头条，v2ex，微博和知乎的热榜词

## 识别方法

### CommonCrawlNews
首先从WARC文件中提取新闻内容，进行AI关键词过滤，并保存有效内容
使用了多进程和NLTK进行文本处理  
得到AI相关新闻

其次调用qwen2.5对AI新闻进行风险新闻一轮筛
然后用qwen3进行风险新闻二轮筛

### 其他数据集

处理流程 类似 也是先用关键词形成AI新闻，在通过大模型进行两轮筛

## 关键词过滤方法校验
使用data项目中的cases.jsonl标准数据集验证  “关键词过滤AI相关新闻”  这一步的具体效果

由于标准数据集来自AIID和AIAAIC两个数据集，这两个数据集都通过了人工测验，因此认为其均是AI相关的真实新闻。
### 具体方法

具体方法为，使用nltk和jieba对文章进行分词，然后和AI关键词取交集，如果存在交集，说明该新闻是AI相关新闻，需要注意的是，在分词过程中，需要确定一些固定短语，比如Artificial Intelligence，遇到这种词需将其看为一个整体，在代码中进行额外操作使其不分为两个词。

### 测试结果

经过测试，使用该方法总计发现AI相关新闻：9131条，非AI相关新闻：430条，AI相关新闻占比95.50%  
也就是说，对AI相关新闻的召回率达到了95%
这证实了在后续全量新闻数据集上首先进行AI相关新闻过滤的合理性

## llm过滤方法校验

使用data项目中的label_news_result_final.json标准数据集验证 “LLM过滤AI风险相关新闻”  这一步的具体效果

### 测试结果

经过测试 在2000条随机抽取的AI新闻中，LLM过滤方法召回AI风险新闻606条，其中正确的AI风险新闻473条，准确率78.05%。实际上这两千条中有AI风险新闻618条，召回率76.54%
TP: 473, FP: 133, FN: 145
准确率（Precision）: 0.7805
召回率（Recall）: 0.7654

## 其他文件夹介绍

config文件夹主要用于存放各步骤中的配置文件
data文件夹主要用于存放评测数据集和标准数据集，data数据集中有独立readme文件
download_dir文件夹主要用于存放下载的数据集和中间处理的数据集，项目中是空的，如需获取需自行运行下载
keywords文件夹主要用于存放各步骤中的关键词文件
logs文件夹主要用于存放各步骤中的日志文件
prompt文件夹主要用于存放各步骤中的提示词文件
