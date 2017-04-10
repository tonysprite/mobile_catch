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

sql = "SELECT id,href,sku FROM `jd_2_mobile` WHERE is_fetch=0 ORDER BY id ASC"
row_count = cursor.execute(sql)
list = cursor.fetchall()
# print(list)

for index in range(len(list)):
    # time.sleep(random.random() * 2)
    if list[index]['href'] == None or list[index]['href'] == '':
        continue
    html_doc = getHtml('http:' + list[index]['href'])
    soup = BeautifulSoup(html_doc)

    #商品所属店铺
    shop_dom = soup.select('#crumb-wrap .contact.fr.clearfix .J-hove-wrap .item .name')
    shop_a = shop_dom[0].select('a')
    shop_name = ''
    if len(shop_a):
        shop_name = shop_a[0].get_text()

    shop_jd_dom = shop_dom[0].select('.u-jd span')
    is_jd = 0
    if len(shop_jd_dom) > 0 and shop_jd_dom[0].get_text() == 'JD':
        is_jd = 1

    #颜色、尺码、成色、在保
    warranty_expired = 1
    color = ''
    rom = ''

    item_info_doms = soup.select('#choose-attrs .li.p-choose')
    for item_info_dom in item_info_doms:
        item_cur_dom = item_info_dom.select('.dd .item.selected')
        item_type = item_info_dom.attrs.get('data-type')
        if item_type == u'颜色':
            color = item_cur_dom[0].attrs.get('data-value')
        elif item_type == u'尺码':
            size = item_cur_dom[0].attrs.get('data-value')
            rom = size[0: (size.find('G') + 1)] + 'B'
            if size.find(u'在保') >= 0:
                warranty_expired = 0
        elif item_type.find(u'成色') >= 0:
            value = item_cur_dom[0].attrs.get('data-value')
            # new_old = size[0: size.find(u'新') + 1]
            if value.find(u'在保') >= 0:
                warranty_expired = 0


    info_dom = soup.select('.Ptable .Ptable-item dl')
    # key_dom = info_dom[0].select('dt')
    new_old = ''
    purchase_channel = ''
    brand = ''
    model = ''

    for dl_dom in info_dom:
        key_dom = dl_dom.select('dt')
        for dom in key_dom:
            key_text = dom.get_text()
            # print(dom)
            if key_text == u'成色':
                new_old = dom.find_next_sibling('dd').get_text()
            elif key_text == u'购买渠道':
                purchase_channel = dom.find_next_sibling('dd').get_text()
            elif key_text == u'品牌' >= 0:
                brand = dom.find_next_sibling('dd').get_text()
            elif key_text.find(u'机型') >= 0:
                model = dom.find_next_sibling('dd').get_text()
            elif rom == '' and (key_text.find(u'机身内存') >= 0 or key_text.find('ROM') >= 0):
                rom = dom.find_next_sibling('dd').get_text()

    # 商品名称
    goods_name = ''
    goods_dom = soup.select('.parameter2.p-parameter-list li')
    for dom in goods_dom:
        if dom.get_text().find(u'商品名称：') >= 0:
            goods_name = dom['title']
        elif model == '' and dom.get_text().find(u'型号：') >= 0:
            model = dom['title']

    price_url = "https://p.3.cn/prices/mgets?type=1&area=1_72_2840_0&pdtk=&pduid=14915347282971073442324&pdpin=&pdbp=0&skuIds=J_" + list[index]['sku']
    json_price = getHtml(price_url).decode("utf-8")
    price_info = json.loads(json_price)
    price = str(price_info[0]['p'])

    is_jd = str(is_jd)
    warranty_expired = str(warranty_expired)

    update_sql = "UPDATE `jd_2_mobile` SET is_fetch=1,price=" + price + ",is_jd=" + is_jd + ",color='" + color + "',shop_name='" + shop_name + "',brand='" + brand + "',model='" + model + "',purchase_channel='" + purchase_channel + "',new_old='" + new_old + "',ROM='" + rom + "',goods_name='" + goods_name + "',warranty_expired=" + warranty_expired + " WHERE id=" + str(list[index]['id'])
    print(update_sql)
    effect_row = cursor.execute(update_sql)
    conn.commit()

# 关闭游标
cursor.close()
# 关闭连接
conn.close()