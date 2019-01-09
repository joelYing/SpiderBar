#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 18-6-5

import re
import pymysql
import requests


class JingDong(object):
    def __init__(self):
        self.d_page_url = 'https://search.jd.com/s_new.php?keyword=%E5%8D%95%E5%8F%8D%E7%9B%B8%E6%9C%BA&' \
                          'enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E5%8D%95%E5%8F%8D%E7%9B%B8%E6%9C%BA&' \
                          'psort=3&page={}&s={}&click=0'
        self.s_page_url = 'https://search.jd.com/s_new.php?keyword=%E5%8D%95%E5%8F%8D%E7%9B%B8%E6%9C%BA&' \
                          'enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E5%8D%95%E5%8F%8D%E7%9B%B8%E6%9C%BA&' \
                          'psort=3&page={}&s={}&scrolling=y&log_id=1540033458.62631&tpl=1_M&' \
                          'show_items=5702614,11730040239,5965562,11737034514,27202398608,7224814,' \
                          '1999420937,24147732475,5965560,28036624898,24147741523,2210972,14119142596,' \
                          '28408109185,10813323008,17745467926,2548547,1468055269,11767683839,10871675399,' \
                          '4449736,28833827828,2283116,5867083,3740987,1989427889,26364191659,27866101100,' \
                          '15242101927,31911299547'
        self.referer = 'https://search.jd.com/Search?keyword=%E5%8D%95%E5%8F%8D%E7%9B%B8%E6%9C%BA&enc=utf-8&' \
                       'qrst=1&rt=1&stop=1&vt=2&wq=%E5%8D%95%E5%8F%8D%E7%9B%B8%E6%9C%BA&psort=3&page={}&s={}&click=0'
        self.good_url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}' \
                        '&callback=jQuery5661745&_=1540019538438'

    @staticmethod
    def price_tool(prices):
        price = re.findall(r'<i>(.*?)</i>', prices, re.S)[0]
        if 'data-price' in prices:
            price = re.findall(r'data-price="(.*?)">', prices, re.S)[0]
        return price

    @staticmethod
    def name_tool(name):
        name = re.sub(r'<.*?>', '', name)
        # new_name = name.replace('（', '').replace('）', '')
        return name

    @staticmethod
    def shop_tool(shop):
        df_type = ''
        if '自营' in shop and '旗舰' in shop:
            df_type = '自营'
        if '专营' in shop:
            df_type = '专营'
        if '自营' not in shop and '旗舰' in shop:
            df_type = '旗舰'
        return df_type

    def gethtml1(self, s, page, r):
        print(page)
        info_list = re.findall(r'<li data-sku="(.*?)" class="gl-item">.*?<div class="p-price">(.*?)</div>'
                               r'.*?<em>(.*?)</em>.*?<a id="J_comment_.*?>.*?</a>.*?</li>', r.text, re.S)
        for infos in info_list:
            # print(infos)
            print(infos[0])
            info_url = 'https://item.jd.com/{}.html'.format(infos[0])
            price = self.price_tool(infos[1])
            name = self.name_tool(infos[2])
            r1 = s.get(info_url)
            # print(r1.text)
            r2 = s.get(self.good_url.format(infos[0]))
            # print(r2.text)
            comment_num = re.findall(r'"CommentCount":(\d+),', r2.text, re.S)[0]
            goods = re.findall(r'"GoodRateShow":(\d+),', r2.text, re.S)[0]
            info_list2 = re.findall(r'<div class="name">.*?<a.*?>(.*?)</a>.*?</div>.*? '
                                    r'<ul class="parameter2.*?>(.*?)</ul>', r1.text, re.S)
            if not info_list2:
                info_list2 = re.findall(r'<h3 class=""><a.*?>(.*?)</a></h3>.*?'
                                        r'<ul class="parameter2.*?>(.*?)</ul>', r1.text, re.S)
            shop = self.shop_tool(info_list2[0][0])
            # print(info_list2)
            types, weight, px, heads, huafu = '', '', '', '', ''
            if '分类：' in info_list2[0][1]:
                types = re.findall(r'分类：(.*?)</li>', info_list2[0][1], re.S)[0]
            if '商品毛重：' in info_list2[0][1]:
                weight = re.findall(r'商品毛重：(.*?)</li>', info_list2[0][1], re.S)[0]
            if '万' in info_list2[0][1]:
                px = re.findall(r'(\d+-*\d+)万', info_list2[0][1], re.S)[0] + u'万'
            if '套头：' in info_list2[0][1]:
                heads = re.findall(r'套头：(.*?)</li>', info_list2[0][1], re.S)[0]
            if "画幅：" in info_list2[0][1] or "传感器尺寸：" in info_list2[0][1]:
                huafu = re.findall(r"[u'画幅',u'传感器尺寸']：(.*?)</li>", info_list2[0][1], re.S)[0]
            print(info_url, price, name, comment_num, goods, shop, types, weight, px, heads, huafu)
            self.insertmysql(price, name, comment_num, goods, shop, types, weight, px, heads, huafu)

    def gethtml2(self):
        s = requests.session()
        for page in range(1, 36):
            # 单数页
            if page % 2 == 1:
                referers = self.referer.format(page, 30*(int(page) - 1) + 1)
                header = {'referer': referers}
                r = s.get(self.d_page_url.format(page, 30 * (int(page) - 1) + 1), headers=header)
                self.gethtml1(s, page, r)
            if page % 2 == 0:
                referers = self.referer.format(page - 1, 30 * (int(page) - 2) + 1)
                header = {'referer': referers}
                r = s.get(self.s_page_url.format(page, 30 * (int(page) - 1) + 1), headers=header)
                self.gethtml1(s, page, r)

    @staticmethod
    def insertmysql(price, title, comment_num, goods, shop, types, weight, px, heads, huafu):
        conn_insert = pymysql.connect(host='localhost', port=3306, user='', password='', db='jingdong')
        cursor_ins = conn_insert.cursor()

        insert_sql = "insert into `jd` (`title`, `price`, `comms`, " \
                     "`goods`, `ty`, `shop`, `weight`, `px`, `ishead`, `huafu`)values('%s','%s','%s'," \
                     "'%s','%s','%s','%s','%s','%s','%s')" % (title, price, comment_num, goods, shop, types,
                                                              weight, px, heads, huafu)
        try:
            select_sql = "select `title` from `jd` where `title`='%s'" % title
            response = cursor_ins.execute(select_sql)
            conn_insert.commit()
            if response == 1:
                print(u'该相机已存在...')
            else:
                try:
                    cursor_ins.execute(insert_sql)
                    conn_insert.commit()
                    print(u'更新成功...')
                except Exception as e:
                    print(u'更新错误...', e)
                    conn_insert.rollback()
        except Exception as e:
            print(u'查询错误...', e)
            conn_insert.rollback()
        finally:
            cursor_ins.close()
            conn_insert.close()


if __name__ == '__main__':
    jd = JingDong()
    jd.gethtml2()
