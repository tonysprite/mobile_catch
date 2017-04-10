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


for page in range(1, 201):
    url = 'https://search.jd.com/s_new.php?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&wq=%E6%89%8B%E6%9C%BA&cid2=653&cid3=655&scrolling=y&page=' + str(page)
    html_doc = getHtml(url)
    soup = BeautifulSoup(html_doc)
    # goods_li = soup.select('.gl-warp.clearfix .gl-item')
    goods_li = soup.select('.gl-item')
    goods_list = []

    i = 1
    # print(goods_li)
    for index in range(len(goods_li)):
        #print(goods_li[index])
        goods_dom = goods_li[index].select('.gl-i-wrap')
        goods_name_dom = goods_dom[0].select('.p-name')
        # goods_price_dom = goods_dom[0].select('.p-price strong')
        goods_price_dom = goods_dom[0].select('.p-price i')

        # goods_price = goods_price_dom[0].attrs.get('data-price')
        # print(goods_price_dom)

        #京东自营图标
        jd_img = goods_dom[0].select('.p-icons img')
        is_jd = 0
        if len(jd_img) > 0 and jd_img[0].attrs.get('data-tips').find(u'京东自营') >= 0:
            is_jd = 1

        #当前商品颜色
        cur_color_dom = goods_dom[0].select('.p-scroll .ps-wrap .ps-main .ps-item a.curr')
        # print(cur_color_dom)
        cur_color = ''
        if len(cur_color_dom) > 0:
            # print(cur_color_dom)
            cur_color = cur_color_dom[0]['title']

        #当前商品所属店铺
        shop_dom = goods_dom[0].select('.p-shop')
        shop_name_dom = goods_dom[0].select('.p-shop span a')
        shop_name = ''
        shop_id = 0
        if len(shop_dom) > 0:
            if len(shop_name_dom) > 0:
                shop_name = shop_name_dom[0]['title']
            shop_id = shop_dom[0].attrs.get('data-shopid')

        #当前商品sku
        sku = str(goods_li[index].attrs.get('data-sku'))

        if len(goods_name_dom) > 0 and len(goods_price_dom) > 0:
            goods_name = goods_name_dom[0].get_text()
            goods_price = goods_price_dom[0].get_text()
            goods_a = goods_name_dom[0].select('a')
            goods_link = goods_a[0]['href']

            goods_name = goods_name.decode("utf-8").replace("\n", "")
            cur_color = cur_color.decode("utf-8").replace("\n", "")
            goods_price = str(goods_price)
            is_jd = str(is_jd)
            shop_name = shop_name.decode("utf-8").replace("\n", "")
            shop_id = str(shop_id)

            cur_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            sql ="INSERT INTO `jd_mobile`(title,price,color,is_jd,add_time,shop_name,shop_id,sku,href) VALUES('" + goods_name + "'," + goods_price + ",'" + cur_color + "'," + is_jd + ",'" + cur_datetime + "','" + shop_name + "','" + shop_id + "','" + sku + "','" + goods_link + "')"
            effect_row = cursor.execute(sql)
            print(sql)
            # print(effect_row)
            # print(goods_name)
            # print(shop_dom)
    conn.commit()

# 关闭游标
cursor.close()
# 关闭连接
conn.close()