#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 19-11-10


"""
苏宁：一页120个 ajax一次30，共四次
页数 cp 0 1 2, 只有第一页没有&adNumber=0 , paging 有1， 2， 3
"""

import re
import pymysql
import requests
from urllib import parse


class SuNing(object):
    def __init__(self):
        self.index_url = 'https://search.suning.com/{}/'
        self.suning_list = 'https://search.suning.com/emall/searchV1Product.do?keyword={}&pg=01&cp={}&n=1&paging={}'
        self.nine_price_info = 'https://pas.suning.com/nspcpackage_000000000{}_{}_574_5740101__0_1.html'
        self.ele_price_info = 'https://pas.suning.com/nspcsale_0_0000000{}_0000000{}_{}_130_574_5740101.html'
        # 包含评论数等数据 9位ID package；11位ID general
        self.comment_num = 'https://review.suning.com/ajax/review_count/{}-{}-{}-{}-----satisfy.htm'
        # 评论印象
        self.comment_type = 'https://review.suning.com/ajax/getClusterReview_labels/' \
                            '{}-{}-{}-{}-----commodityrLabels.htm'
        # 评论详情
        self.comment_detail_11 = 'https://review.suning.com/ajax/cluster_review_lists/' \
                                 'general-30268267-000000010877217665-0070517287-total-1-default-10-----reviewList.htm'
        self.comment_detail_9 = 'https://review.suning.com/ajax/cluster_review_lists/' \
                                'package-30268267-000000000945052192-0070517287-total-1-default-10-----reviewList.htm'

    @staticmethod
    def nine_or_eleven(second_id):
        # 预定second_id长度为9
        x = 'package'
        long_second_str_id = '000000000' + second_id
        if len(second_id) == 11:
            x = 'general'
            long_second_str_id = '0000000' + second_id
        return x, long_second_str_id

    def del_price(self, s, first_str_id, second_str_id):
        """
        针对不同的第二id的手机有不同的获取price的接口
        second_phone_id = 9 对应 self.nine_price_info
        second_phone_id = 11 对应 self.ele_price_info
        可以发现 id 长度 与接口中 0串长度 和为 18
        """
        global r_price
        if len(second_str_id) == 9:
            r_price = s.get(self.nine_price_info.format(second_str_id, first_str_id))
        if len(second_str_id) == 11:
            r_price = s.get(self.ele_price_info.format(second_str_id, second_str_id, first_str_id))
        real_prices = re.findall(r'"promotionPrice":"(.*?)"', r_price.text, re.S)
        real_price = real_prices[0]
        ref_prices = re.findall(r'"pgPrice":"(.*?)"', r_price.text, re.S)
        ref_price = ref_prices[0]
        # if ref_price == '' or ref_price == real_price:
        #     ref_price = ''
        #     real_price = ref_price
        return real_price, ref_price

    def get_commentinfo(self, s, comment_num_url, comment_type_url, name, goods_url, first_str_id, second_str_id):
        # 手机评论数
        r_comment_num = s.get(comment_num_url)
        comment_num = re.findall(r'"totalCount":(\d+)', r_comment_num.text, re.S)
        if comment_num:
            comment_num = str(comment_num[0])
        # 评论印象
        comment_type = ''
        r_comment_num_type = s.get(comment_type_url)
        comment_types = re.findall(r'{"labelName":"(.*?)","labelCnt":(\d+)}', r_comment_num_type.text, re.S)
        if comment_types:
            for types in comment_types:
                comment_type += types[0] + '(' + str(types[1]) + ') '
        # 价格
        price, ref_price = self.del_price(s, first_str_id, second_str_id)
        self.insert_mysql(second_str_id, goods_url, name, price, ref_price, comment_num, comment_type)

    def get_more_goods(self, s, part_numbers, first_str_id, vendorcode, comment_cluster_id):
        # 每个手机的不同规格
        y = ''
        for part_number in part_numbers:
            # 从多的先开始匹配
            number_copy = part_number
            if str(part_number).startswith('000000000'):
                y = 'package'
                part_number = str(part_number).replace('000000000', '')
            if str(part_number).startswith('0000000'):
                y = 'general'
                part_number = str(part_number).replace('0000000', '')
            othors_goods_url = 'https://product.suning.com/' + str(vendorcode) + '/' + part_number + '.html'
            print(othors_goods_url)
            r_othors_goods_url = s.get(othors_goods_url)
            othors_goods_names = re.findall(r'"itemDisplayName":"(.*?)"', r_othors_goods_url.text, re.S)
            othors_goods_name = othors_goods_names[0]
            # 针对 “碎屏险一年套餐，碎屏无忧” 的情况好像没什么实际意义
            if '套装清单' in r_othors_goods_url.text:
                continue
            comment_num_url, comment_type_url = self.comment_num.format(
                y, comment_cluster_id, str(number_copy), vendorcode), self.comment_type.format(
                y, comment_cluster_id, str(number_copy), vendorcode)
            self.get_commentinfo(s, comment_num_url, comment_type_url, othors_goods_name, othors_goods_url,
                                 first_str_id, part_number)

    def get_infos(self, response):
        s = requests.session()
        goods_base_info = re.findall(r'<a target="_blank".*?href="(.*?)".*?>.*?<img alt="(.*?)".*?>', response, re.S)
        if goods_base_info:
            for goods in goods_base_info:
                # 列表中的（30） 的每一个手机
                goods_url = 'https:' + goods[0]
                print(goods_url)
                name = goods[1]
                # 手机页面url中的两个数串
                first_str_id = re.findall(r'/(\d+)/\d+\.html', goods[0], re.S)[0]
                second_str_id = re.findall(r'/(\d+)\.html', goods[0], re.S)[0]
                r_goods_url = s.get(goods_url)
                if '很抱歉,此商品不存在' in r_goods_url.text:
                    print(u'商品不存在')
                    continue
                vendor_codes = re.findall(r'sn\.review = {.*?"vendorCode":"(.*?)".*?"clusterId":"(.*?)".*?}',
                                          r_goods_url.text, re.S)
                # 相当于first_str_id
                vendorcode = vendor_codes[0][0]
                # 查询跟评论有关的数据时用到的数字，同一手机不同配置下公用同一个
                comment_cluster_id = vendor_codes[0][1]
                x, long_second_str_id = self.nine_or_eleven(second_str_id)
                comment_num_url, comment_type_url = self.comment_num.format(
                    x, comment_cluster_id, long_second_str_id, vendorcode), self.comment_type.format(
                    x, comment_cluster_id, long_second_str_id, vendorcode)

                self.get_commentinfo(s, comment_num_url, comment_type_url, name, goods_url,
                                     first_str_id, second_str_id)
                partnumbers = re.findall(r'{"versionId":".*?","partNumber":"(\d+)"}', r_goods_url.text, re.S)
                self.get_more_goods(s, partnumbers, first_str_id, vendorcode, comment_cluster_id)

    def get_info_list(self, keyword):
        # 关键词中文转URL编码
        keyword = parse.quote(keyword)
        r_index = requests.get(self.index_url.format(keyword))
        # 商品总页数
        pages = re.findall(r'<span class="fl">.*?<em class="low">1</em> /.*?<em>(\d+)</em>.*?</span>',
                           r_index.text, re.S)
        # cp: 0,1,2,3,...默认20页
        for cp in range(0, int(pages[0])):
            print('第' + str(cp + 1) + '页')
            for paging in range(0, 4):
                r = requests.get(self.suning_list.format(keyword, cp, paging))
                self.get_infos(r.text)

    @staticmethod
    def insert_mysql(goods_id, goods_url, name, price, ref_price, comment_num, comment_type):
        conn_insert = pymysql.connect(host='localhost', port=3306, user='root', password='', db='suning')
        cursor_ins = conn_insert.cursor()

        insert_sql = "insert into `sn_search` (`pid`, `url`, `price`, " \
                     "`ref_price`, `name`, `comment_num`, `comment_type`)values('%s','%s','%s'," \
                     "'%s','%s','%s','%s')" % (goods_id, goods_url, price, ref_price, name, comment_num, comment_type)
        try:
            select_sql = "select `pid` from `sn_search` where `pid`='%s'" % goods_id
            response = cursor_ins.execute(select_sql)
            conn_insert.commit()
            if response == 1:
                print(u'该商品已存在...')
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
    suning = SuNing()
    kw = input('请输入搜索关键词：')
    suning.get_info_list(kw)
