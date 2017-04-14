# encoding: utf-8
import sys
from common import *
from bs4 import BeautifulSoup
import time
import json
import random
import re

reload(sys)
sys.setdefaultencoding('utf-8')

for page in range(1, 2):
    url = 'https://list.jd.com/list.html?cat=13765,13767&page=' + str(page)
    html_doc = getHtml(url)
    soup = BeautifulSoup(html_doc)
    goods_li = soup.select('#plist .gl-warp.clearfix .gl-item')
    # goods_li = soup.select('#plist')
    goods_list = []

    # print(goods_li)
    for index in range(len(goods_li)):
        #print(goods_li[index])
        goods_dom = goods_li[index].select('.gl-i-wrap')
        goods_title_dom = goods_dom[0].select('.p-name')
        # goods_price_dom = goods_dom[0].select('.p-price i')


        #京东自营图标
        jd_img = goods_dom[0].select('.p-icons img')
        is_jd = 0
        if len(jd_img) > 0 and jd_img[0].attrs.get('data-tips').find(u'京东自营') >= 0:
            is_jd = 1

        #当前商品sku
        sku = str(goods_dom[0].attrs.get('data-sku'))

        if len(goods_title_dom) > 0:
            goods_title = goods_title_dom[0].get_text()
            goods_a = goods_title_dom[0].select('a')
            goods_link = goods_a[0]['href']

            goods_title = goods_title.decode("utf-8").replace("\n", "")
            is_jd = str(is_jd)

            cur_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cur_date = time.strftime("%Y-%m-%d", time.localtime())

            # 根据商品链接抓取商品详情 --start
            goods_info_html = getHtml('http:' + goods_link)
            goods_info_dom = BeautifulSoup(goods_info_html)
            # print(goods_info_dom)
            # 商品所属店铺
            shop_dom = goods_info_dom.select('#crumb-wrap .contact.fr.clearfix .J-hove-wrap .item .name')
            shop_a = shop_dom[0].select('a')
            shop_name = ''
            if len(shop_a):
                shop_name = shop_a[0].get_text()

            shop_jd_dom = shop_dom[0].select('.u-jd span')
            is_jd = 0
            if len(shop_jd_dom) > 0 and shop_jd_dom[0].get_text() == 'JD':
                is_jd = 1

            # 颜色、尺码、成色、在保
            warranty_expired = 1
            color = ''
            rom = ''

            item_info_doms = goods_info_dom.select('#choose-attrs .li.p-choose')
            for item_info_dom in item_info_doms:
                item_cur_dom = item_info_dom.select('.dd .item.selected')
                item_type = item_info_dom.attrs.get('data-type')
                if item_type == u'颜色':
                    color = item_cur_dom[0].attrs.get('data-value')
                elif item_type == u'尺码':
                    size = item_cur_dom[0].attrs.get('data-value')
                    if size.find('G') >= 0:
                        before_str_size = size[0: (size.find('G'))]
                        after_str_size = size[(size.find('G') + 1)]
                        after_rom = after_str_size[(after_str_size.find('G'))]
                        rom = size[0: (size.find('G'))]
                        # 去掉容量中“GB”
                        # rom = re.sub('G', '', rom, re.IGNORECASE)
                        # rom = re.sub('B', '', rom, re.IGNORECASE)
                    if size.find(u'在保') >= 0:
                        warranty_expired = 0
                elif item_type.find(u'成色') >= 0:
                    value = item_cur_dom[0].attrs.get('data-value')
                    # new_old = size[0: size.find(u'新') + 1]
                    if value.find(u'在保') >= 0:
                        warranty_expired = 0

            info_dom = goods_info_dom.select('.Ptable .Ptable-item dl')
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
                    elif color == '' and key_text.find(u'颜色') >= 0:
                        color = dom.find_next_sibling('dd').get_text()
            # 去掉容量中“GB”
            # rom = rom.replace('G', '').replace('B', '')
            rom = re.sub('G', '', rom, re.IGNORECASE)
            rom = re.sub('B', '', rom, re.IGNORECASE)
            # 去掉颜色中“色”字及空格
            color = color.replace(u'色', '').replace(' ', '')

            # 商品名称
            goods_name = ''
            goods_dom = goods_info_dom.select('.parameter2.p-parameter-list li')
            for dom in goods_dom:
                if dom.get_text().find(u'商品名称：') >= 0:
                    goods_name = dom['title']
                elif model == '' and dom.get_text().find(u'型号：') >= 0:
                    model = dom['title']

            #统一品牌名称、机型未取到时的处理
            original_brand = brand #原始品牌名称
            brand_pos_start = brand.find(u'（')
            if brand_pos_start < 0:
                brand_pos_start = brand.find('(')

            brand_pos_end = brand.find(u'）')
            if brand_pos_end < 0:
                brand_pos_end = brand.find(')')
            if brand_pos_start > 0:
                brand = brand[0: brand_pos_start]

            # 机型未取到时，根据商品名称处理 --start
            if model == '' or model.find(u'其他') >= 0:
                if brand_pos_start >0:
                    model = goods_name.replace(original_brand[0: brand_pos_start], '').replace(original_brand[(brand_pos_start + 1) : brand_pos_end], '')
                else:
                    model = goods_name.replace(brand, '')
            model = model.replace(brand, '')
            model = re.sub(u'[\s\(\)（）]', '', model)
            # 统一品牌名称、机型未取到时的处理 --end

            # 根据商品链接抓取商品详情 --end

            # 抓取商品价格 --start
            # pduid会过期，不清楚规则是怎样的
            # sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            pduid = '149'
            pduid = pduid + str(random.sample('0123456789', 10)) + str(random.sample('0123456789', 9))
            price_url = "https://p.3.cn/prices/mgets?type=1&area=1_72_2840_0&pdtk=&pduid=" + pduid + "&pdpin=&pdbp=0&skuIds=J_" + sku
            json_price = getHtml(price_url).decode("utf-8")
            price_info = json.loads(json_price)
            price = str(price_info[0]['p'])
            # 抓取商品价格 --end

            data = {'title': goods_title, 'is_jd': is_jd, 'add_time': cur_datetime, 'sku': sku, 'href': goods_link,
                    'shop_name': shop_name, 'price': price, 'color': color, 'is_fetch': 0,
                    'brand': brand, 'model': model, 'purchase_channel': purchase_channel, 'new_old': new_old, 'rom': rom,
                    'goods_name': goods_name, 'warranty_expired': warranty_expired,
                    'add_date': cur_date
                    }
            # print(data)
            result = db_conn.insert(table='da_jd_2_mobile', data=data)
            print('insert into da_jd_2_mobile:' + str(result))

            #插入数据到价格对比表
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


# 更新价格对比表 京东价格
sql = """UPDATE `da_mobile_compare` AS c LEFT JOIN
(SELECT brand,model,color,rom,purchase_channel,new_old,warranty_expired,""" + which_price + """(price) AS price,add_date FROM `da_jd_2_mobile`
GROUP BY brand,model,color,rom,purchase_channel,new_old,warranty_expired,add_date
HAVING add_date=MAX(add_date) ORDER BY brand,model,color,rom,purchase_channel,new_old,warranty_expired) AS p
 ON c.brand=p.brand AND c.model=p.model AND c.color=p.color AND c.rom=p.rom AND c.purchase_channel=p.purchase_channel AND c.warranty_expired=p.warranty_expired AND c.add_date=p.add_date
SET c.jd_price=p.price"""
result = db_conn.execute(sql)
print('da_mobile_compare affected rows:' + str(result))