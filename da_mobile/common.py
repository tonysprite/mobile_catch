# encoding: utf-8
import urllib
from libmysql import MYSQL

def getHtml(url):
    page=urllib.urlopen(url)
    html=page.read()
    return html

# mysql数据库配置
db_config = {
    'host': '192.168.1.252',
    'port': '3306',
    'user': 'bybon',
    'pwd': 'bybontest',
    'db': 'test_new',
    'charset': 'utf8',
}
db_conn = MYSQL(
        dbhost = db_config['host'],
        dbport = db_config['port'],
        dbuser = db_config['user'],
        dbpwd = db_config['pwd'],
        dbname = db_config['db'],
        dbcharset = db_config['charset']
)

# 配置平台取相同商品 最低价、最高价、平均价中的哪一个
which_price = "MIN"