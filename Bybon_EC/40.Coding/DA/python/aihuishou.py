# -*- coding:utf-8 -*-
import urllib
from bs4 import BeautifulSoup
import pymysql
import time
import sys

# print(sys.getdefaultencoding())
# exit()
reload(sys)
sys.setdefaultencoding('utf-8')

# 创建连接
conn = pymysql.connect(host='192.168.59.129', port=3306, user='root', passwd='root', db='test', charset='utf8')
# 创建游标
cursor = conn.cursor()

def getHtml(url):
    page=urllib.urlopen(url)
    html=page.read()
    return html


for page in range(1, 17):
    url = 'http://liangpin.aihuishou.com/search/index?k=&id_category=7&id_manufacturer=&id_product_level=&id_product=&properties=&sort=&page=' + str(page)
    html_doc = getHtml(url)
    soup = BeautifulSoup(html_doc)
    goods_li = soup.select('#container .section-prods ul li')

    for index in range(len(goods_li)):
        goods_dom = goods_li[index].select('a')
        goods_name_dom = goods_li[index].select('.prod .prod-name')
        goods_price_dom = goods_li[index].select('.price span')

        if len(goods_name_dom) > 0 and len(goods_price_dom) > 0:
            goods_name = goods_name_dom[0].get_text()
            goods_price_i = goods_price_dom[0].select('i')
            goods_price_i[0].extract()
            goods_price = goods_price_dom[0].get_text()
            goods_link = goods_dom[0]['href']

            goods_name = goods_name.decode("utf-8").replace("\n", "").replace(" ", "")
            goods_price = str(goods_price).replace("\n", "").replace(" ", "")

            cur_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            sql ="INSERT INTO `aihuishou_mobile`(title,price,add_time,href) VALUES('" + goods_name + "'," + goods_price + ",'" + cur_datetime + "','" + goods_link + "')"
            effect_row = cursor.execute(sql)
            print(sql)

    conn.commit()

# 关闭游标
cursor.close()
# 关闭连接
conn.close()