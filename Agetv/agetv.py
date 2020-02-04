#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 20-01-22

import re
import time
import pymysql
import requests
import random
from Agetv.faua import FaUa


class AgeSpider:
    def __init__(self):
        """
        若又有新的番完结，那么去遍历完结的目录，与数据库中的去匹配，若没有重复，则添加即可
        若要新爬取连载番的资源，可以新建一个表，或者直接存在agepan_wj，因为type不同
        连载的番不必急于保存，因为网盘资源链接一般不会变，等到其状态变为完结再爬取，或者先爬取也可以
        但是不用急于转存便是
        """
        self.headers = {
            'user-agent': FaUa.get_ua()
        }
        self.type_list = {
            '1': 'https://www.agefans.tv/catalog/all-all-all-all-all-time-{}-all-all-%E5%AE%8C%E7%BB%93',
            '2': 'https://www.agefans.tv/catalog/all-all-all-all-all-time-{}-all-all-%E8%BF%9E%E8%BD%BD',
            '3': 'https://www.agefans.tv/catalog/all-all-all-all-all-time-{}-all-all-%E6%9C%AA%E6%92%AD%E6%94%BE',
            '4': 'https://www.agefans.tv/catalog/all-all-all-all-all-time-{}',
            '5': 'https://www.agefans.tv/catalog/all-all-all-all-all-%E7%82%B9%E5%87%BB%E9%87%8F-{}-all-all-%E5%AE%8C%E7%BB%93'
        }
        self.base_url = 'https://www.agefans.tv'

    def age_spider(self, age_type):
        """
        网站有一定的反爬策略，所以加上随机的请求头
        后续爬取根据筛选条件选择未完结的即可
        1-完结：https://www.agefans.tv/catalog/all-all-all-all-all-time-1-all-all-%E5%AE%8C%E7%BB%93
        2-连载：https://www.agefans.tv/catalog/all-all-all-all-all-time-1-all-all-%E8%BF%9E%E8%BD%BD
        3-未播放：https://www.agefans.tv/catalog/all-all-all-all-all-time-1-all-all-%E6%9C%AA%E6%92%AD%E6%94%BE
        """
        s = requests.session()
        print('爬取' + age_type + '号资源')
        for page in range(114, 141):
            print('第' + str(page) + '页')
            page_url = self.type_list[age_type].format(page)
            r_page_url = s.get(page_url, headers=self.headers)
            # print(r_page_url.text)
            detail_url_list = re.findall(r'<div class="cell_imform">.*?<a href="(.*?)" '
                                         r'class="cell_imform_name">(.*?)</a></div>', r_page_url.text, re.S)
            for detail_url in detail_url_list:
                # 每一页中的每个视频
                d_url = self.base_url + detail_url[0]
                d_name = str(detail_url[1]).replace('\'', '\'\'')
                # print(d_name, d_url)
                r_d_url = s.get(d_url, headers=self.headers)
                pan_sources = re.findall(r'<span class="res_links">.*?<a class="res_links_a" href="(.*?)".*?>(.*?)</a>'
                                         r'.*?<span class="res_links_pswd_tag">\(提取码:</span>.*?<span class="'
                                         r'res_links_pswd">(.*?)\)</span></span>', r_d_url.text, re.S)
                for pan_source in pan_sources:
                    # 每个视频详情页面中的网盘资源
                    pan_url = self.base_url + pan_source[0]
                    pan_title = pan_source[1]
                    pan_psw = pan_source[2]
                    r = s.get(pan_url, headers=self.headers)
                    print(d_name, d_url, pan_url, pan_title, pan_psw, r.url, age_type)
                    self.insert(d_name, d_url, pan_url, pan_title, pan_psw, r.url, age_type)
                time.sleep(random.randint(0, 3))
            # break
            time.sleep(random.randint(0, 3))

    @staticmethod
    def insert(name, detail_url, pan_url, pan_title, pan_psw, pan_real_url, age_type):
        database = pymysql.connect(host='localhost', port=3306, user='root', passwd='12138', db='agetv')
        cursor = database.cursor()
        try:
            select_sql = "select pan_real_url from agepan_click where pan_real_url='%s'" % pan_real_url
            response = cursor.execute(select_sql)
            if response == 1:
                print(u'该条网盘资源已存在...')
            else:
                try:
                    insert_sql = "insert into agepan_click (`name`, `detail_url`, `pan_url`, `pan_title`, " \
                                 "`pan_psw`, `pan_real_url`, `age_type`)values('%s','%s','%s','%s','%s'," \
                                 "'%s','%s')" % (name, detail_url, pan_url, pan_title, pan_psw, pan_real_url, age_type)
                    cursor.execute(insert_sql)
                    database.commit()
                    print(u'提交成功...')
                except:
                    print(u'插入错误...')
                    database.rollback()
        except:
            print(u'查询错误...')
            database.rollback()
        finally:
            cursor.close()
            database.close()


if __name__ == '__main__':
    age = AgeSpider()
    age_types = input('请输入下载的资源状态序号：\n1、完结\n2、连载\n3、未播放\n4、全部\n5、按播放量\n')
    age.age_spider(str(age_types))
