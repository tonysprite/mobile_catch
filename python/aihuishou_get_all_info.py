# -*- coding:utf-8 -*-
import urllib
from bs4 import BeautifulSoup
import pymysql
import time
import sys
import json
import random

# print(sys.getdefaultencoding())
# exit()
reload(sys)
sys.setdefaultencoding('utf-8')

# 创建连接
conn = pymysql.connect(host='192.168.59.129', port=3306, user='root', passwd='root', db='test', charset='utf8')
# 创建游标
cursor = conn.cursor(pymysql.cursors.DictCursor)

def getHtml(url):
    page=urllib.urlopen(url)
    html=page.read()
    return html

sql = "SELECT id,href FROM `aihuishou_mobile` WHERE is_fetch=0 ORDER BY id ASC"
row_count = cursor.execute(sql)
list = cursor.fetchall()
# print(list)

for index in range(len(list)):
    # time.sleep(random.random() * 2)
    if list[index]['href'] == None or list[index]['href'] == '':
        continue
    html_doc = getHtml(list[index]['href'])
    soup = BeautifulSoup(html_doc)

    #品牌
    brand = ''
    td_dom = soup.select('.prod_content .content td')
    for td in td_dom:
        span = td.select('span')
        for val in span:
            if val.get_text() == u'品牌':
                brand_td = td.find_next_sibling('td')
                brand_span = brand_td.select('span')
                brand = brand_span[0].get_text()

    sku = list[index]['href'].split('/')[-1]
    json_info = getHtml("http://liangpin.aihuishou.com/product/ajaxSkuPropertyList?id_sku=" + sku).decode("utf-8")
    goods_info = json.loads(json_info)
    data  = goods_info['data']
    level_list = data['level']
    property_list = data['property']
    sku_info = data['sku']
    # print(goods_info)

    # 颜色、成色、在保、渠道
    new_old = ''
    for level in level_list:
        if level['selected'] == True:
            if level['name'].find(u'成') >= 0 or level['name'] == u'全新' or level['name'] == u'未激活':
                new_old = level['name']
            else:
                pos = level['name'].find(u'新')
                new_old = level['name'][0: pos] + u"成" + level['name'][pos]

            break
    color = ''
    rom = ''
    purchase_channel = ''
    warranty_expired = 1
    for property in property_list:
        for val in property['values']:
            if property['name'] == u'颜色' and val['selected'] == True:
                color = val['value']
            if property['name'] == u'容量' and val['selected'] == True:
                rom = val['value']
            if property['name'] == u'渠道' and val['selected'] == True:
                purchase_channel = val['value']
            if property['name'] == u'保修情况' and val['selected'] == True and val['value'] == u'在保':
                warranty_expired = 0

    model = sku_info['product_name']
    price = str(sku_info['price'])
    warranty_expired = str(warranty_expired)

    # 商品名称
    goods_name = model

    update_sql = "UPDATE `aihuishou_mobile` SET is_fetch=1,price=" + price + ",color='" + color + "',brand='" + brand + "',model='" + model + "',purchase_channel='" + purchase_channel + "',new_old='" + new_old + "',ROM='" + rom + "',goods_name='" + goods_name + "',warranty_expired=" + warranty_expired + " WHERE id=" + str(list[index]['id'])
    print(update_sql)
    effect_row = cursor.execute(update_sql)
    conn.commit()

# 关闭游标
cursor.close()
# 关闭连接
conn.close()