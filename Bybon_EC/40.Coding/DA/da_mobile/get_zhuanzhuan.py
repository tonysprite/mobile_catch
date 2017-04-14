# encoding: utf-8
import sys
from libmysql import MYSQL
import urllib
from bs4 import BeautifulSoup
import time
import json

reload(sys)
sys.setdefaultencoding('utf-8')

def getHtml(url):
    page=urllib.urlopen(url)
    html=page.read()
    return html

dbconn = MYSQL(
        dbhost = '192.168.59.130',
        dbport = '3306',
        dbuser = 'root',
        dbpwd = 'root',
        dbname = 'test',
        dbcharset = 'utf8')

for page in range(1, 6):
    url = 'http://bj.58.com/shouji/1/pn' + str(page)
    html_doc = getHtml(url)
    soup = BeautifulSoup(html_doc)
    goods_tr = soup.select('#infolist .tbimg tr')
    goods_list = []

    for goods_dom in goods_tr:
        goods_title_a = goods_dom.select('.t a')
        goods_price_b = goods_dom.select('.tc b')
        print(goods_price_b, '--------')
        if len(goods_price_b) > 0:
            goods_title = goods_title_a[0].get_text()
            goods_price = goods_price_b[0].get_text()

            cur_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            data = {
                'title': goods_title,
                'price': goods_price,
                'add_time': cur_datetime
            }
            result = dbconn.insert('da_mobile_zhuanzhuan', data)
            print(result)

