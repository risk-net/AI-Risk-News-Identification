#该文件是为了获取OpenNewsArchive的新闻数据 文件为wrac格式，下载至指定文件夹
#注意根据实际情况 输入对应的AK/SK，并修改响应的保存地址
import openxlab
from openxlab.dataset import info
from openxlab.dataset import get
from openxlab.dataset import download
import os

openxlab.login(ak="<Access Key>", sk="<Secret Key>") #进行登录，输入对应的AK/SK
info(dataset_repo='OpenDataLab/OpenNewsArchive') #数据集信息及文件列表查看
get(dataset_repo='OpenDataLab/OpenNewsArchive', target_path='/path/to/local/folder/')  # 数据集下载
current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建目标文件路径
target_path = os.path.join(current_dir, "../../../download_dir")
download(dataset_repo='OpenDataLab/OpenNewsArchive',source_path='/README.md', target_path=target_path) #数据集文件下载