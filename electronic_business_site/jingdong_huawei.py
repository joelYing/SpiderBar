#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 18-6-5

"""
京东：一页 60 分两次加载，每次30

"""

import random
import re
import time
import pymysql
import requests


# CREATE TABLE `jd_huawei` (
#   `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
#   `pid` varchar(32) CHARACTER SET utf8mb4 NOT NULL,
#   `url` varchar(128) CHARACTER SET utf8mb4 NOT NULL,
#   `price` double(10,2) NOT NULL,
#   `name` varchar(512) CHARACTER SET utf8mb4 NOT NULL,
#   `comment_num` int(10) NOT NULL,
#   `comment_type` varchar(512) CHARACTER SET utf8mb4 NOT NULL,
#   PRIMARY KEY (`id`),
#   KEY `pid` (`pid`) USING BTREE
# ) ENGINE=InnoDB AUTO_INCREMENT=30702 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;


class JingDong(object):
    def __init__(self):
        """
        修改 comment_num 类型
        之前只需添加 referer 现在还需添加 ua
        在用format格式化url时，若URL中也有 { } 这时则format 中以 {{ }} 两个大括号来转义
        """
        self.search_url = 'https://search.jd.com/search?keyword=%E5%8D%8E%E4%B8%BA&enc=utf-8&qrst=1&rt=1&' \
                          'stop=1&vt=2&bs=1&wq=%E5%8D%8E%E4%B8%BA&cid2=653&' \
                          'cid3=655&ev=exbrand_%E5%8D%8E%E4%B8%BA%EF%BC%88HUAWEI%EF%BC%89%5E&page=1&s=1&click=0'
        self.d_page_url = 'https://search.jd.com/s_new.php?keyword=%E5%8D%8E%E4%B8%BA&enc=utf-8&' \
                          'qrst=1&rt=1&stop=1&vt=2&bs=1&wq=%E5%8D%8E%E4%B8%BA&cid2=653&cid3=655&' \
                          'ev=exbrand_%E5%8D%8E%E4%B8%BA%EF%BC%88HUAWEI%EF%BC%89%5E&page={}&s={}&click=0'
        self.s_page_url = 'https://search.jd.com/s_new.php?keyword=%E5%8D%8E%E4%B8%BA&enc=utf-8&qrst=1&rt=1&' \
                          'stop=1&vt=2&bs=1&wq=%E5%8D%8E%E4%B8%BA&cid2=653&cid3=655&ev=exbrand_%E5%8D%8E%E4%B8' \
                          '%BA%EF%BC%88HUAWEI%EF%BC%89%5E&page={}&s={}&scrolling=y&log_id=1546069310.93962&tpl=3_M&' \
                          'show_items=7694047,5821455,7421462,8735304,100000822981,6946605,7081550,100000650837,' \
                          '7479912,100000766433,100000820311,100002293114,8240587,100001467225,6733024,6703015,' \
                          '34593872687,100000972490,6840907,5963066,6001239,28245104630,8058010,5826236,100000767811,' \
                          '8485229,7123633,100000084109,6737464,6055054'
        self.referer = 'https://search.jd.com/search?keyword=%E5%8D%8E%E4%B8%BA&enc=utf-8&' \
                       'qrst=1&rt=1&stop=1&vt=2&bs=1&wq=%E5%8D%8E%E4%B8%BA&cid2=653&cid3=655&' \
                       'ev=exbrand_%E5%8D%8E%E4%B8%BA%EF%BC%88HUAWEI%EF%BC%89%5E&page={}&s={}&click=0'
        self.good_url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}' \
                        '&callback=jQuery5661745&_=1540019538438'
        self.comments_type = 'https://sclub.jd.com/comment/productPageComments.action?' \
                             'callback=fetchJSON_comment98vv28643&productId={}&score=0&sortType=5' \
                             '&page=0&pageSize=10&isShadowSku=0&fold=1'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/70.0.3538.102 Safari/537.36'
        self.phone_price = 'https://c0.3.cn/stock?skuId={}&cat=9987,653,655&venderId=1000004259&area=1_72_2799_0&' \
                           'buyNum=1&choseSuitSkuIds=&extraParam={{%22originid%22:%221%22}}&ch=1&fqsp=0&' \
                           'pduid=1566822370&pdpin=jd_707f2cd751b1b&callback=jQuery7969932'

    @staticmethod
    def price_tool(prices):
        price = re.findall(r'<i>(.*?)</i>', prices, re.S)[0]
        if 'data-price' in prices:
            price = re.findall(r'data-price="(.*?)">', prices, re.S)[0]
        return price

    @staticmethod
    def name_tool(name):
        name = re.sub(r'<.*?>', '', name)
        return name

    def getcomment(self, s, ids):
        # 好评数
        r2 = s.get(self.good_url.format(ids))
        # 好评类型
        # r3 = s.get(self.comments_type.format(ids), proxies=self.proxies)
        comment_num = re.findall(r'"CommentCount":(\d+),', r2.text, re.S)
        if comment_num:
            comment_num = comment_num[0]
        # comment_type = re.findall(r'\"hotCommentTagStatistics\":\[(.*?)\]', r3.text, re.S)
        comment_types = ''
        # if comment_type and len(comment_type):
        #     comment_types_list2 = re.findall(r'{.*?"name":"(.*?)".*?"count":(\d+),.*?}', comment_type[0], re.S)
        #     for c in comment_types_list2:
        #         comment_types += (c[0] + "(" + str(c[1]) + ") ")
        return comment_num, comment_types

    def gethtml1(self, s, page, r):
        print(page)
        # 一页30个手机
        info_list = re.findall(r'<li class="gl-item" data-sku="(.*?)".*?>.*?<div class="p-price">(.*?)</div>'
                               r'.*?<em>(.*?)</em>.*?<a id="J_comment_.*?>.*?</a>.*?</li>', r.text, re.S)
        for infos in info_list:
            # 每一个手机
            info_id = infos[0]
            info_url = 'https://item.jd.com/{}.html'.format(infos[0])
            print(info_url)
            name = self.name_tool(infos[2])
            r_refprice = s.get(self.phone_price.format(info_id))
            ref_prices = re.findall(r'"jdPrice":{.*?"op":"(.*?)".*?"p":"(.*?)".*?}', r_refprice.text, re.S)
            price, ref_price = '', ''
            if ref_prices:
                ref_price = ref_prices[0][0]
                price = ref_prices[0][1]
                if ref_prices[0][0] == ref_prices[0][1]:
                    price = ''
                    ref_price = ref_prices[0][1]
            r1 = s.get(info_url)
            comment_num, comment_types = self.getcomment(s, infos[0])
            self.insertmysql(info_id, info_url, price, ref_price, name, comment_num, comment_types)
            # 每个手机的多种搭配方式
            colorsize = re.findall(r'colorSize: \[(.*?)\]', r1.text, re.S)

            if colorsize:
                skuIds = re.findall(r'"skuId":(\d+),', colorsize[0], re.S)
                for skuId in skuIds:
                    print(skuId)
                    skuid_url = 'https://item.jd.com/{}.html'.format(skuId)
                    r4 = s.get(skuid_url)
                    # 每种类型的标题
                    skuid_name = re.findall(r'<div class="sku-name">(.*?)</div>', r4.text, re.S)
                    if not skuid_name:
                        continue
                    skuid_name = self.name_tool(str(skuid_name[0])).strip()
                    r5 = s.get(self.phone_price.format(skuId))
                    # 每种类型的价格
                    skuid_prices = re.findall(r'"jdPrice":{.*?"op":"(.*?)".*?"p":"(.*?)".*?}', r5.text, re.S)
                    skuid_price, ref_skuid_price = '', ''
                    if skuid_prices:
                        ref_skuid_price = skuid_prices[0][0]
                        skuid_price = skuid_prices[0][1]
                        if skuid_prices[0][0] == skuid_prices[0][1]:
                            skuid_price = ''
                            ref_skuid_price = skuid_prices[0][1]
                    skuid_comment_num, skuid_comment_types = self.getcomment(s, skuId)
                    self.insertmysql(skuId, skuid_url, skuid_price, ref_skuid_price, skuid_name, skuid_comment_num, skuid_comment_types)
                    # time.sleep(random.randint(0, 3))

    def gethtml2(self):
        s = requests.session()
        # 需要带上ua
        r_page = s.get(self.search_url, headers={'user-agent': self.user_agent})
        page = re.findall(r'<span class="fp-text">.*?<b>1</b><em>/</em><i>(\d+)</i>.*?</span>', r_page.text, re.S)
        pages = int(page[0])*2 + 1
        print(u'共' + str(pages) + u'页')
        for page in range(115, pages):
            # 单数页
            if page % 2 == 1:
                referers = self.referer.format(page, 30*(int(page) - 1) + 1)
                header = {
                    'referer': referers,
                    'user-agent': self.user_agent,
                }
                r = s.get(self.d_page_url.format(page, 30 * (int(page) - 1) + 1), headers=header)
                self.gethtml1(s, page, r)
            if page % 2 == 0:
                referers = self.referer.format(page - 1, 30 * (int(page) - 2) + 1)
                header = {
                    'referer': referers,
                    'user-agent': self.user_agent,
                }
                r = s.get(self.s_page_url.format(page, 30 * (int(page) - 1) + 1), headers=header)
                self.gethtml1(s, page, r)
            time.sleep(1)

    @staticmethod
    def insertmysql(info_id, info_url, price, refprice, name, comment_num, comment_types):
        conn_insert = pymysql.connect(host='localhost', port=3306, user='', password='', db='jingdong')
        cursor_ins = conn_insert.cursor()

        insert_sql = "insert into `jd_huawei` (`pid`, `url`, `price`, " \
                     "`refprice`, `name`, `comment_num`, `comment_type`)values('%s','%s','%s'," \
                     "'%s','%s','%s','%s')" % (info_id, info_url, price, refprice, name, comment_num, comment_types)
        try:
            select_sql = "select `pid` from `jd_huawei` where `pid`='%s'" % info_id
            response = cursor_ins.execute(select_sql)
            conn_insert.commit()
            if response == 1:
                print(u'该手机已存在...')
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
