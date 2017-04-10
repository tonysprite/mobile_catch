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


for page in range(1, 44):
    url = 'https://list.jd.com/list.html?cat=13765,13767&page=' + str(page)
    html_doc = getHtml(url)
    soup = BeautifulSoup(html_doc)
    goods_li = soup.select('#plist .gl-warp.clearfix .gl-item')
    goods_list = []

    i = 1
    # print(goods_li)
    for index in range(len(goods_li)):
        #print(goods_li[index])
        goods_dom = goods_li[index].select('.gl-i-wrap')
        goods_name_dom = goods_dom[0].select('.p-name')
        # goods_price_dom = goods_dom[0].select('.p-price i')


        #京东自营图标
        jd_img = goods_dom[0].select('.p-icons img')
        is_jd = 0
        if len(jd_img) > 0 and jd_img[0].attrs.get('data-tips').find(u'京东自营') >= 0:
            is_jd = 1

        #当前商品sku
        sku = str(goods_dom[0].attrs.get('data-sku'))

        if len(goods_name_dom) > 0:
            goods_name = goods_name_dom[0].get_text()
            goods_a = goods_name_dom[0].select('a')
            goods_link = goods_a[0]['href']

            goods_name = goods_name.decode("utf-8").replace("\n", "")
            is_jd = str(is_jd)

            cur_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            sql ="INSERT INTO `jd_2_mobile`(title,is_jd,add_time,sku,href) VALUES('" + goods_name + "'," + is_jd + ",'" + cur_datetime + "','" + sku + "','" + goods_link + "')"
            effect_row = cursor.execute(sql)
            print(sql)

    conn.commit()

# 关闭游标
cursor.close()
# 关闭连接
conn.close()