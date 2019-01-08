#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:joel
# time:2019/1/4 9:39

import random
import re
import time
import pymysql
import requests
import fk_ua

"""
快速爬取容易引起注意，容易封账号（可能是暂时的）
建议备一个账号使用，尽量一次性搞定
url没有什么问题，以pageNo分页，但是注意带上完整的headers 
重复过多会重定向到 输入账号密码的界面
"""


class TmallMi(object):
    """
    天猫华为旗舰店 - 华为手机
    """
    def __init__(self):
        self.tm_url = 'https://huaweistore.tmall.com/i/asynSearch.htm?_ksTS=1546840502296_117&callback=jsonp118&mid=w-14758655684-0&wid=14758655684&path=/view_shop.htm&spm=a1z10.3-b-s.w4011-14758655684.5.3abd2c5aiDgayt&q=%BB%AA%CE%AA%CA%D6%BB%FA&type=p&from=inshophq_4_0&search=y&newHeader_b=s_from&searcy_type=item'
        self.uaer_agent = fk_ua.fa_ua[random.randint(0, len(fk_ua.fa_ua))]
        # self.proxies = {"http": "http://localhost:1080", "https": "http://localhost:1080", }

    def nametool(self, name):
        name = re.sub(r'<.*?>', '', name)
        return name

    def gethtml(self):
        headers = {
            'accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'cookie': 'your-cookie',
            'pragma': 'no-cache',
            'referer': 'https://huaweistore.tmall.com/?spm=a1z10.3-b-s.w4011-14758655684.5.3abd2c5aiDgayt&q=%BB%AA%CE%AA%CA%D6%BB%FA&type=p&from=inshophq_4_0&search=y&newHeader_b=s_from&searcy_type=item',
            'user-agent': self.uaer_agent,
            'x-requested-with': 'XMLHttpRequest',
        }
        r = requests.get(self.tm_url, headers=headers)
        tmall_mis = re.findall(r'<dd class=\\"detail\\">.*?<a.*?href=\\"(.*?)\\".*?>(.*?)</a>.*?'
                               r'class=\\"c-price\\">(.*?)</span>.*?总销量：<span.*?class=\\"sale-num\\">'
                               r'(\d+)</span>.*?</dd>', r.text, re.S)
        for tmall_mi in tmall_mis:
            tm_url = 'https:' + str(tmall_mi[0]).strip()
            tid = re.findall(r'id=(.*?)&rn', tm_url, re.S)[0]
            name = str(tmall_mi[1]).strip()
            name = self.nametool(name)
            price = str(tmall_mi[2]).strip()
            sale_num = str(tmall_mi[3]).strip()
            print(tid, tm_url, name, price, sale_num)
            self.insertmysql(tid, tm_url, name, price, sale_num)
        time.sleep(random.randint(1, 40))

    def insertmysql(self, tid, tm_url, name, price, sale_num):
        conn_insert = pymysql.connect(host='localhost', port=3306, user='', password='', db='tmallmi')
        cursor_ins = conn_insert.cursor()

        insert_sql = "insert into `tmall_huawei` (`tid`, `url`, `name`, `price`, `salenums`)values('%s','%s','%s'," \
                     "'%s','%s')" % (tid, tm_url, name, price, sale_num)
        try:
            select_sql = "select `tid` from `tmall_huawei` where `tid`='%s'" % tid
            response = cursor_ins.execute(select_sql)
            conn_insert.commit()
            if response == 1:
                print(u'该小米商品已存在...')
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
    tm = TmallMi()
    tm.gethtml()