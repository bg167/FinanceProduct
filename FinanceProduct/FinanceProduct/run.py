import ssl
from requests_toolbelt import MultipartEncoder
import requests
import urllib.request
import urllib.parse
import json
import sys
import os
import datetime
import pandas as pd

# curPath = os.path.abspath(os.path.dirname(__file__))
# rootPath = os.path.split(curPath)[0]
# sys.path.append(rootPath)
sys.path.append('..')
from scrapy import cmdline
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from FinanceProduct.spiders import ccb, icbc, spdb, abc

# 定义参数
PATH = '/Users/Tracy/Development/Finance/Product/FinanceProduct/FinanceProduct'

print(datetime.datetime.now())

process = CrawlerProcess(get_project_settings())
process.crawl(ccb.CcbSpider)
process.crawl(icbc.IcbcSpider)
process.crawl(spdb.SpdbSpider)
process.crawl(abc.AbcSpider)
process.start()

print("爬取数据结束。")

# print(os.getcwd())
# 合并文件
file_dir = './result'
# 构建新的表格名称
new_filename = file_dir + '/gather.xls'

if os.path.exists(new_filename):
    os.remove(new_filename)

# 找到文件路径下的所有表格名称，返回列表
file_list = os.listdir(file_dir)
df_list = []

for file in file_list:
    # 重构文件路径
    file_path = os.path.join(file_dir, file)
    # 将excel转换成DataFrame
    single_df = pd.read_csv(file_path)
    # 保存到新列表中
    df_list.append(single_df)

# 多个DataFrame合并为一个
df = pd.concat(df_list)
# 写入到一个新excel表中
header = ['', '银行', '产品编号', '产品名称', '申购开始日期', '申购结束日期', '利率', '期限_天', '产品类型', '起购金额_元',
          '币种', '风险级别', '风险类型', '发售区域', '产品链接']
df.to_excel(new_filename, index=False, header=header)

print('全部完成。')
