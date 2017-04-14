# -*- coding:utf-8 -*-
import sys
from common import *
from bs4 import BeautifulSoup
import time
import json
import random
import re

reload(sys)
sys.setdefaultencoding('utf-8')

for page in range(1, 17):
    url = 'http://liangpin.aihuishou.com/search/index?k=&id_category=7&id_manufacturer=&id_product_level=&id_product=&properties=&sort=&page=' + str(page)
    html_doc = getHtml(url)
    soup = BeautifulSoup(html_doc)
    goods_li = soup.select('#container .section-prods ul li')

    for index in range(len(goods_li)):
        goods_dom = goods_li[index].select('a')
        goods_title_dom = goods_li[index].select('.prod .prod-name')
        goods_price_dom = goods_li[index].select('.price span')

        if len(goods_title_dom) > 0 and len(goods_price_dom) > 0:
            goods_title = goods_title_dom[0].get_text()
            goods_price_i = goods_price_dom[0].select('i')
            goods_price_i[0].extract()
            goods_price = goods_price_dom[0].get_text()
            goods_link = goods_dom[0]['href']

            goods_title = goods_title.decode("utf-8").replace("\n", "").replace(" ", "")
            goods_price = str(goods_price).replace("\n", "").replace(" ", "")

            cur_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cur_date = time.strftime("%Y-%m-%d", time.localtime())

            # 抓取商品详情
            # print(goods_link)
            # continue
            goods_info_html = getHtml(goods_link)
            # print(goods_info_html)
            # continue
            goods_info_dom = BeautifulSoup(goods_info_html)

            # 品牌
            brand = ''
            td_dom = goods_info_dom.select('.prod_content .content td')
            for td in td_dom:
                span = td.select('span')
                for val in span:
                    if val.get_text() == u'品牌':
                        brand_td = td.find_next_sibling('td')
                        brand_span = brand_td.select('span')
                        brand = brand_span[0].get_text()

            sku = goods_link.split('/')[-1]
            json_info = getHtml("http://liangpin.aihuishou.com/product/ajaxSkuPropertyList?id_sku=" + sku).decode(
                "utf-8")
            goods_info = json.loads(json_info)
            data = goods_info['data']
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

            # 去掉容量中“GB”
            # rom = rom.replace('G', '').replace('B', '')
            rom = re.sub('G', '', rom, re.IGNORECASE)
            rom = re.sub('B', '', rom, re.IGNORECASE)
            # 去掉颜色中“色”字及空格
            color = color.replace(u'色', '').replace(' ', '')

            model = sku_info['product_name']
            model = re.sub(u'[\s\(\)（）]', '', model)
            price = str(sku_info['price'])
            warranty_expired = str(warranty_expired)

            # 商品名称
            goods_name = model

            data = {
                'title': goods_title,
                'price': price,
                'color': color,
                'add_time': cur_datetime,
                'add_date': cur_date,
                'href': goods_link,
                'brand': brand,
                'model': model,
                'purchase_channel': purchase_channel,
                'new_old': new_old,
                'rom': rom,
                'goods_name': goods_name,
                'warranty_expired': warranty_expired,
            }

            result = db_conn.insert('da_aihuishou_mobile', data)
            print('insert into da_aihuishou_mobile:' + str(result))

            # 插入数据到价格对比表
            sql = "SELECT * FROM `da_mobile_compare` WHERE brand=%s AND REPLACE(model,' ','')=%s AND color=%s AND rom=%s AND purchase_channel=%s AND new_old=%s AND warranty_expired=%s AND add_date='" + cur_date + "' LIMIT 1"
            where = (brand, model.replace(' ', ''), color, rom, purchase_channel, new_old, warranty_expired)
            rows = db_conn.query(sql, where, True)
            if rows:
                # print('record++++++++++')
                # print(sql % where)
                continue
                # else:
                # print('no---------')
                # print(sql % where)
            data = {'add_time': cur_datetime, 'color': color,
                    'brand': brand, 'model': model, 'purchase_channel': purchase_channel, 'new_old': new_old,
                    'rom': rom, 'warranty_expired': warranty_expired,
                    'add_date': cur_date
                    }
            result_compare = db_conn.insert(table='da_mobile_compare', data=data)

            print('insert into da_mobile_compare:' + str(result_compare))

# 更新价格对比表 爱回收价格
sql = """UPDATE `da_mobile_compare` AS c LEFT JOIN
(SELECT brand,model,color,rom,purchase_channel,new_old,warranty_expired,""" + which_price + """(price) AS price,add_date FROM `da_aihuishou_mobile`
GROUP BY brand,model,color,rom,purchase_channel,new_old,warranty_expired,add_date
HAVING add_date=MAX(add_date) ORDER BY brand,model,color,rom,purchase_channel,new_old,warranty_expired) AS p
 ON c.brand=p.brand AND c.model=p.model AND c.color=p.color AND c.rom=p.rom AND c.purchase_channel=p.purchase_channel AND c.warranty_expired=p.warranty_expired AND c.add_date=p.add_date
SET c.aihuishou_price=p.price"""
result = db_conn.execute(sql)
print('da_mobile_compare affected rows:' + str(result))