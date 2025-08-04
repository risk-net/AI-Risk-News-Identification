#这个文件定义了一个函数，用于统一处理日期时间字符串的格式转换
#它尝试多种日期时间格式，并使用dateutil库作为最后的手段

from datetime import datetime
from dateutil.parser import parse

def convert_date_format(date_str):
    """
    将输入的日期时间字符串转换为指定的日期格式（年-月-日）字符串

    参数:
    date_str (str): 输入的日期时间字符串，格式需符合 '%Y-%m-%d %H:%M:%S'

    返回:
    str: 转换后的日期格式字符串，格式为 '%Y-%m-%d'
    """
    try_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y/%m/%d %H:%M:%S',
        '%Y/%m/%d %H:%M',
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%Y年%m月%d日 %H:%M',
        '%Y年%m月%d日%H:%M'
    ]
    for fmt in try_formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            continue
    # 如果所有格式都试过了，还是失败，就用dateutil
    try:
        date_obj = parse(date_str)
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        print("时间格式不符合要求")
        return date_str

