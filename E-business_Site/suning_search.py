#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 18-6-5


"""
苏宁：一页120个 ajax一次30，共四次
页数 cp 0 1 2, 只有第一页没有&adNumber=0 , paging 有1， 2， 3，
"""
import re
import pymysql
import requests


class SuNing(object):
    def __init__(self):
        self.suning_list = 'http://search.suning.com/emall/searchV1Product.do?' \
                           'keyword=%E5%8D%8E%E4%B8%BA&ci=20006&pg=01&cp={}&il=0&st=0&iy=0&' \
                           'hf=brand_Name_FacetAll:%E5%8D%8E%E4%B8%BA%28HUAWEI%29{}&n=1&sesab=ACAABAAB&id=IDENTIFYING' \
                           '&cc=010{}&sub=1&jzq=1498'
        self.nine_price_info = 'http://pas.suning.com/nspcsale_0_000000000{}_000000000{}_{}_20_' \
                               '021_0210101_20089_1000267_9264_12113_Z001___R1901001_0.58_0___000060864__.html?' \
                               'callback=pcData&_=1546397609500'
        self.ele_price_info = 'http://pas.suning.com/nspcsale_0_0000000{}_0000000{}_{}_' \
                              '20_021_0210101_20089_1000267_9264_12113_Z001___R1901001_0.5_3___000060864_01_.html?' \
                              'callback=pcData&_=1546399092869'
        self.comment = 'http://review.suning.com/ajax/cluster_review_satisfy/cluster-{}-{}-' \
                       '{}-----satisfy.htm?callback=satisfy'
        self.comment_type = 'http://review.suning.com/ajax/getClusterReview_labels/' \
                            'general-{}-{}-{}-----commodityrLabels.htm?' \
                            'callback=commodityrLabels&_=1546419526971'
        self.comment_taocan = 'http://review.suning.com/ajax/review_count/' \
                              'package--{}-{}-----satisfy.htm?callback=satisfy'
        self.comment_type_taocan = 'http://review.suning.com/ajax/getClusterReview_labels/' \
                                   'package--{}-{}-----commodityrLabels.htm?' \
                                   'callback=commodityrLabels&_=1546484821414'

    def delprice(self, s, first_phone_id, second_phone_id):
        """
        针对不同的第二id的手机有不同的获取price的接口
        second_phone_id = 9 对应 self.nine_price_info
        second_phone_id = 11 对应 self.ele_price_info
        可以发现 id 长度 与接口中 0串长度 和为 18
        """
        global price
        if len(second_phone_id) == 9:
            price = s.get(self.nine_price_info.format(second_phone_id, second_phone_id, first_phone_id))
        if len(second_phone_id) == 11:
            price = s.get(self.ele_price_info.format(second_phone_id, second_phone_id, first_phone_id))
        phone_price = re.findall(r'"promotionPrice":"(.*?)"', price.text, re.S)
        if phone_price:
            phone_price = phone_price[0]
        ref_phone_price = re.findall(r'"refPrice":"(.*?)"', price.text, re.S)
        if ref_phone_price:
            ref_phone_price = ref_phone_price[0]
        if ref_phone_price == '' or ref_phone_price == phone_price:
            ref_phone_price = phone_price
            phone_price = ''
        return phone_price, ref_phone_price

    def getcommentinfo(self, s, comment_num_url, comment_type_url):
        # 手机评论数
        r_comment_num = s.get(comment_num_url)
        comment_num = re.findall(r'"totalCount":(\d+)', r_comment_num.text, re.S)
        if comment_num:
            comment_num = str(comment_num[0])
        # 评论类型
        comment_type = ''
        r_comment_num_type = s.get(comment_type_url)
        comment_types = re.findall(r'{"labelName":"(.*?)","labelCnt":(\d+)}', r_comment_num_type.text,
                                    re.S)
        if comment_types:
            for types in comment_types:
                comment_type += types[0] + '(' + str(types[1]) + ') '
        return comment_num, comment_type

    def getinfos(self, s, response):
        global comment_num_queryid, long_second_phone_id, vendorcode
        phone_url_name = re.findall(r'<a target="_blank".*?href="(.*?)".*?>.*?<img alt="(.*?)".*?>', response, re.S)
        if phone_url_name:
            for url_name in phone_url_name:
                # 列表中的（30） 的每一个手机
                phone_url = 'http:' + url_name[0]
                print(phone_url)
                name = url_name[1]
                # 手机页面url中的两个数串
                second_phone_id = re.findall(r'/(\d+)\.html', url_name[0], re.S)[0]

                first_phone_id = re.findall(r'/(\d+)/\d+\.html', url_name[0], re.S)[0]
                r_phone_url = s.get(phone_url)
                if '很抱歉,此商品不存在' in r_phone_url.text:
                    print(u'商品不存在')
                    continue
                vendorcodes = re.findall(r'sn\.review = {.*?"vendorCode":"(.*?)".*?"clusterId":"(.*?)".*?}',
                                         r_phone_url.text, re.S)
                if vendorcodes:
                    # 相当于url中的第一串数字
                    vendorcode = vendorcodes[0][0]
                    # 查询评论数时用到的数字，一个手机下公用同一个
                    comment_num_queryid = vendorcodes[0][1]
                if len(second_phone_id) == 9:
                    long_second_phone_id = '000000000' + second_phone_id
                if len(second_phone_id) == 11:
                    long_second_phone_id = '0000000' + second_phone_id

                if comment_num_queryid == '':
                    print(u'套餐类型')
                    comment_num1, comment_type1 = self.getcommentinfo(s, self.comment_taocan.format(
                        long_second_phone_id, vendorcodes[0][0]), self.comment_type_taocan.format(
                        long_second_phone_id, vendorcodes[0][0]))
                else:
                    comment_num1, comment_type1 = self.getcommentinfo(s, self.comment.format(
                        str(comment_num_queryid), long_second_phone_id, vendorcodes[0][0]), self.comment_type.format(
                        str(comment_num_queryid), long_second_phone_id, vendorcodes[0][0]))

                phone_price, ref_phone_price = self.delprice(s, first_phone_id, second_phone_id)
                self.insertmysql(second_phone_id, phone_url, name, phone_price, ref_phone_price, comment_num1, comment_type1)

                partnumber = re.findall(r'{"versionId":".*?","partNumber":"(\d+)"}', r_phone_url.text, re.S)
                if partnumber:
                    # 每个手机的不同规格
                    for number in partnumber:
                        # 从多的先开始匹配
                        numberx = number
                        if str(number).startswith('000000000'):
                            number = str(number).replace('000000000', '')
                        if str(number).startswith('0000000'):
                            number = str(number).replace('0000000', '')
                        config_phone_url = 'http://product.suning.com/' + str(vendorcode) + '/' + number + '.html'
                        print(config_phone_url)
                        r_config_phone_url = s.get(config_phone_url)
                        config_phone_name = re.findall(r'"itemDisplayName":"(.*?)"', r_config_phone_url.text, re.S)
                        if config_phone_name:
                            config_phone_name = config_phone_name[0]
                        # 针对 “碎屏险一年套餐，碎屏无忧” 的情况好像没什么实际意义
                        if '套装清单' in r_config_phone_url.text:
                            continue
                        if comment_num_queryid == '':
                            print(u'套餐类型')
                            comment_num2, comment_type2 = self.getcommentinfo(s, self.comment_taocan.format(
                                str(numberx), vendorcode), self.comment_type_taocan.format(str(numberx), vendorcode))
                        else:
                            comment_num2, comment_type2 = self.getcommentinfo(s, self.comment.format(
                                comment_num_queryid, str(numberx), vendorcode), self.comment_type.format(
                                comment_num_queryid, str(numberx), vendorcode))
                        # 注：若既没有现价也没有原价，则该手机可能下架或暂无销售
                        phone_price, ref_phone_price = self.delprice(s, vendorcode, number)

                        self.insertmysql(number, config_phone_url, config_phone_name, phone_price, ref_phone_price, comment_num2, comment_type2)

    def getfourajax(self, s, adnumber, cp):
        paging0 = s.get(self.suning_list.format(cp, adnumber, ''))
        self.getinfos(s, paging0.text)
        for page in range(1, 4):
            paging = s.get(self.suning_list.format(cp, adnumber, '&paging=' + str(page)))
            self.getinfos(s, paging.text)

    def gethtml(self):
        s = requests.session()
        for cp in range(0, 20):
            if cp == 0:
                adnumber = ''
                self.getfourajax(s, adnumber, cp)
            else:
                adnumber = '&adNumber=0'
                self.getfourajax(s, adnumber, cp)
            break

    @staticmethod
    def insertmysql(info_id, info_url, name, price, refprice, comment_num, comment_types):
        conn_insert = pymysql.connect(host='localhost', port=3306, user='', password='', db='suning')
        cursor_ins = conn_insert.cursor()

        insert_sql = "insert into `sn_huawei` (`pid`, `url`, `price`, " \
                     "`refprice`, `name`, `comment_num`, `comment_type`)values('%s','%s','%s'," \
                     "'%s','%s','%s','%s')" % (info_id, info_url, price, refprice, name, comment_num, comment_types)
        try:
            select_sql = "select `pid` from `sn_huawei` where `pid`='%s'" % info_id
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
    suning = SuNing()
    suning.gethtml()
