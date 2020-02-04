#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 19-11-9

"""
京东：一页 60 分两次加载，每次30
在用format格式化url时，若URL中也有 { } 这时则format 中以 {{ }} 两个大括号来转义
"""

import re
import time
import pymysql
import requests
from urllib import parse


class JingDong(object):
    def __init__(self):
        # 商品页面
        self.product_url = 'https://item.jd.com/{}.html'
        # 关键词搜索api
        self.search_url = 'https://search.jd.com/Search?keyword={}&enc=utf-8'
        # 单数页加载api
        self.single_page_url = 'https://search.jd.com/s_new.php?keyword={}&enc=utf-8&page={}&s={}'
        # 双数页加载api %E4%B8%80%E5%8A%A0
        self.double_page_url = 'https://search.jd.com/s_new.php?keyword={}&enc=utf-8&page={}&s={}&scrolling=y'
        # headers所需referer
        self.referer = 'https://search.jd.com/search?keyword={}&enc=utf-8&page={}&s={}'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/70.0.3538.102 Safari/537.36'
        self.header = {'referer': '', 'user-agent': self.user_agent}
        # 评论数
        self.good_url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}'
        # 评论详情 访问需带上 referer，最大10条 https://item.paipai.com/40990434065.html 或 https://item.jd.com/53536922317.html
        self.comments_type = 'https://sclub.jd.com/comment/productPageComments.action?productId={}' \
                             '&score=0&sortType=5&page=0&pageSize=10'
        # cat 在商品主页源代码中有，直接搜 'cat:'
        self.goods_price_api = 'https://c0.3.cn/stock?skuId={}&area=15_1158_46343_0' \
                               '&venderId={}&cat={}'

    @staticmethod
    def name_tool(name):
        name = re.sub(r'<.*?>', '', name)
        return name

    def get_comment(self, s, ids):
        # 好评数
        r_comment = s.get(self.good_url.format(ids))
        # 好评类型
        self.header['referer'] = 'https://item.jd.com/{}.html'.format(ids)
        # 访问频率过快会导致采集不到评论特点，这里最好加上随机 proxies
        r_comment_type = s.get(self.comments_type.format(ids), headers=self.header)
        comment_num = re.findall(r'"CommentCount":(\d+),', r_comment.text, re.S)
        if comment_num:
            comment_num = comment_num[0]
        comment_type = re.findall(r'\"hotCommentTagStatistics\":\[(.*?)\]', r_comment_type.text, re.S)
        comment_types = ''
        if comment_type and len(comment_type):
            comment_types_list2 = re.findall(r'{.*?"name":"(.*?)".*?"count":(\d+),.*?}', comment_type[0], re.S)
            for c in comment_types_list2:
                comment_types += (c[0] + "(" + str(c[1]) + ") ")
        return comment_num, comment_types

    def get_more_infos(self, s, pid, url, name):
        r_formats = s.get(url)
        cat_vid = re.findall(r'cat: \[(.*?)],.*?venderId:(.*?),', r_formats.text, re.S)
        if cat_vid[0]:
            cat, vid = cat_vid[0][0], cat_vid[0][1]
            r_refprice = s.get(self.goods_price_api.format(pid, vid, cat))
            ref_prices = re.findall(r'"jdPrice":{.*?"p":"(.*?)".*?"op":"(.*?)".*?}', r_refprice.text, re.S)
            price, ref_price = '', ''
            if ref_prices:
                ref_price = ref_prices[0][0]
                price = ref_prices[0][1]
                # if ref_prices[0][0] == ref_prices[0][1]:
                #     price = ''
                #     ref_price = ref_prices[0][1]
            comment_num, comment_types = self.get_comment(s, pid)
            # print(pid, url, price, ref_price, name, comment_num, comment_types)
            self.insertmysql(pid, url, price, ref_price, name, comment_num, comment_types)

    def get_goods_info(self, s, page, r):
        print(page)
        # 一页30个手机
        info_list = re.findall(r'<li class="gl-item" data-sku="(.*?)".*?>.*?<div class="p-price">(.*?)</div>'
                               r'.*?<em>(.*?)</em>.*?<a id="J_comment_.*?>.*?</a>.*?</li>', r.text, re.S)
        for infos in info_list:
            # 每一个手机
            info_id = infos[0]
            info_url = self.product_url.format(infos[0])
            print(info_url)
            name = self.name_tool(infos[2])
            self.get_more_infos(s, info_id, info_url, name)
            # 每个手机的多种搭配方式
            r_info_url = s.get(info_url)
            colorsize = re.findall(r'colorSize: \[(.*?)\]', r_info_url.text, re.S)
            if colorsize:
                skuids = re.findall(r'"skuId":(\d+),', colorsize[0], re.S)
                for skuid in skuids:
                    print(skuid)
                    skuid_url = self.product_url.format(skuid)
                    r_skuid_url = s.get(skuid_url)
                    # 每种类型的标题
                    skuid_name = re.findall(r'<div class="sku-name">(.*?)</div>', r_skuid_url.text, re.S)
                    if not skuid_name:
                        continue
                    skuid_name = self.name_tool(str(skuid_name[0])).strip()
                    self.get_more_infos(s, skuid, skuid_url, skuid_name)
                    # time.sleep(random.randint(0, 3))

    def get_info(self, keyword):
        s = requests.session()
        # 需要带上ua
        keyword = parse.quote(keyword)
        r_page = s.get(self.search_url.format(keyword), headers={'user-agent': self.user_agent})
        page = re.findall(r'<span class="fp-text">.*?<b>1</b><em>/</em><i>(\d+)</i>.*?</span>', r_page.text, re.S)
        # 用来循环的(商品总页数 + 1)
        pages = int(page[0])*2 + 1
        print(u'共' + str(pages) + u'页')
        for page in range(1, pages):
            # 单数页
            if page % 2 == 1:
                # header 中需要 format 的 referer 的页偏移值
                referers_s = 30*(int(page) - 1) + 1
                self.header['referer'] = self.referer.format(keyword, page, referers_s)
                r = requests.get(self.single_page_url.format(keyword, page, referers_s), headers=self.header)
            else:
                referers_s, double_s = 30 * (int(page) - 2) + 1, 30 * (int(page) - 1) + 1
                self.header['referer'] = self.referer.format(keyword, page - 1, referers_s)
                r = s.get(self.double_page_url.format(keyword, page, double_s), headers=self.header)
            self.get_goods_info(s, page, r)
            time.sleep(1)

    @staticmethod
    def insertmysql(info_id, info_url, price, refprice, name, comment_num, comment_types):
        conn_insert = pymysql.connect(host='localhost', port=3306, user='root', password='', db='jingdong')
        cursor_ins = conn_insert.cursor()

        insert_sql = "insert into `jd_search` (`pid`, `url`, `price`, `ref_price`, `name`, `comment_num`, " \
                     "`comment_type`)values('%s','%s','%s','%s','%s','%s','%s')" % \
                     (info_id, info_url, price, refprice, name, comment_num, comment_types)
        try:
            select_sql = "select `pid` from `jd_search` where `pid`='%s'" % info_id
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
    kw = input('请输入搜索关键词：')
    jd.get_info(kw)
