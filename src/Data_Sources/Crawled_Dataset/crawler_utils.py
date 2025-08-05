#这个文件定义了一些通用的爬虫工具函数
#包括加载配置文件、清理旧文件、保存结果和上传结果等功能

import configparser
import logging
import os
import json
import requests
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def load_config():
    """加载并标准化配置文件"""
    config = configparser.ConfigParser(allow_no_value=True)
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建目标文件路径
        config_path = os.path.join(current_dir, "../../../../config/Data_Sources-Crawled_Dataset-config.ini")
        config.read(config_path, encoding='utf-8')
        
        # 标准化配置值
        for section in config.sections():
            for key in config[section]:
                if config[section][key]:
                    config[section][key] = config[section][key].strip()
                    
    except Exception as e:
        logging.error(f"加载配置文件失败: {e}")
        raise
    return config

def clean_old_files(results_dir='results', keep_weeks=4):
    """清理超过指定周数的旧文件"""
    try:
        if not os.path.exists(results_dir):
            return
            
        current_date = datetime.now()
        cutoff_date = current_date - timedelta(weeks=keep_weeks)
        
        for filename in os.listdir(results_dir):
            try:
                # 从文件名中提取日期
                date_str = filename.split('_')[-1].split('.')[0]  # 获取YYYY-MM-DD部分
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                # 如果文件超过保留期限，删除它
                if file_date < cutoff_date:
                    file_path = os.path.join(results_dir, filename)
                    os.remove(file_path)
                    logging.info(f"已删除过期文件: {filename}")
            except (ValueError, IndexError):
                continue
    except Exception as e:
        logging.error(f"清理旧文件时出错: {e}")

def save_results(results, other_results, site_name):
    """保存爬取结果到指定文件"""
    os.makedirs('results', exist_ok=True)
    
    # 获取当前日期
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # 保存AIGC相关结果

    airisk_filename = os.path.join(current_dir,f'../../../download_dir/Crawled_Dataset-AI_risk_news-{site_name}_{current_date}.json')
    with open(aigc_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    # 保存所有结果
    all_filename = os.path.join(current_dir,f'../../../download_dir/Crawled_Dataset-all_news-{site_name}_{current_date}.json')
    with open(all_filename, 'w', encoding='utf-8') as f:
        json.dump(other_results, f, ensure_ascii=False, indent=4)
        
    logging.info(f"结果已保存到 {airisk_filename} 和 {all_filename}")
    return airisk_filename, all_filename

def upload_results(site_name, aigc_file, all_file):
    """上传爬取结果到API"""
    # 请修改为实际的API URL和本地fallback配置
    config = load_config()
    api_url = config.get('API', 'base_url', fallback='fallback').strip()
    
    try:
        # 上传AIGC相关结果
        with open(aigc_file, 'r', encoding='utf-8') as f:
            aigc_data = json.load(f)
            response = requests.post(f"{api_url}/risks", json=aigc_data)
            response.raise_for_status()
            logging.info(f"AIGC结果上传成功: {site_name}")

        # 上传所有新闻结果
        with open(all_file, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
            response = requests.post(f"{api_url}/api/news", json=all_data)
            response.raise_for_status()
            logging.info(f"所有新闻结果上传成功: {site_name}")

        return True
    except Exception as e:
        logging.error(f"上传结果失败 {site_name}: {e}")
        return False 