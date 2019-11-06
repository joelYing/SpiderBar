#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:joel 19-11-6

import re
import time
import pymysql
from lxml import etree
import requests


class YuanTong(object):
    def __init__(self):
        # 6:已回复，7：已完成 ，8：已关闭，4：处理中
        # base_url 在 https://tousu.sina.com.cn 黑猫投诉中搜索圆通，出现的就是针对圆通公司的投诉
        self.base_url = 'https://tousu.sina.com.cn/api/company/received_complaints?' \
                   'callback=jQuery111208122936695176131_1543212371581&couid=2146783270' \
                   '&type=1&page_size=10&page={}&_=1543212371582'
        # api_2 是一般所有的投诉
        self.api_2 = 'https://tousu.sina.com.cn/api/index/feed?' \
                     'callback=jQuery1112035396594072642396_1573025736517&' \
                     'type=1&page_size=10&page=1&_=1573025736518'

    @staticmethod
    def status_tool(num):
        status = ''
        if num == '4':
            status = u'处理中'
        if num == '6':
            status = u'已回复'
        if num == '7':
            status = u'已完成'
        if num == '8':
            status = u'已关闭'
        return status

    @staticmethod
    def url_tool(url):
        url = re.sub(r'\\', '', url)
        url = 'https:' + url
        return url

    @staticmethod
    def text_tool(text):
        text = re.sub(r'<.*?>', '', text)
        text = text.strip()
        return text

    def getinfo(self, pages):
        for i in range(1, int(pages) + 1):
            print(u'第' + str(i) + u'页')
            r = requests.get(self.base_url.format(i))
            result = r.text.encode('utf-8').decode('unicode_escape')
            real_result = re.findall(r'"complaints":\[(.*?)],"pager"', result, re.S)
            # print(real_result[0])
            tousu_lists = re.findall(r'"main":{.*?"title":"(.*?)".*?"appeal":"(.*?)","comment_id":"(.*?)","timestamp":'
                                     r'"(.*?)","status":(\d+),.*?"url":"(.*?)".*?}', real_result[0], re.S)
            for tousu in tousu_lists:
                # print(tousu)
                title, appeal, comment_id = tousu[0], tousu[1], tousu[2]
                createtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(tousu[3])))
                status = self.status_tool(str(tousu[4]))
                url = self.url_tool(tousu[5])
                tousu_detail = requests.get(url)
                html = etree.HTML(tousu_detail.text)
                detail_lists = re.findall(r'涉诉金额：</label>(.*?)</li>.*?投诉进度：</label><b>(.*?)</b></li>.*?',
                                          tousu_detail.text, re.S)
                ts_details = html.xpath('//div[@class="ts-reply"]/p/text()')
                ts_detail = ts_details[len(ts_details) - 1]
                money, detail_status = detail_lists[0][0], detail_lists[0][1]
                # print(title, appeal, comment_id, createtime, status, url, money, detail_status, ts_detail, '\n')
                self.insertmysql(title, appeal, comment_id, createtime, detail_status, url, money, ts_detail)

    @staticmethod
    def insertmysql(title, appeal, comment_id, createtime, detail_status, url, money, ts_detail):
        conn = pymysql.connect(host='', port=3306, user='root', passwd='', db='yuantong_tousu')
        cursor = conn.cursor()

        insert_sql = "insert into `yt_ts` (`comment_id`, `title`, `appeal`, `create_time`, " \
                     "`status`, `url`, `money`, `detail_content`)values('%s','%s','%s','%s','%s','%s','%s','%s')" \
                     % (comment_id, title, appeal, createtime, detail_status, url, money, ts_detail)
        select_sql = "select `comment_id` from `yt_ts` where `comment_id`='%s'" % comment_id

        try:
            response = cursor.execute(select_sql)
            conn.commit()
            if response == 1:
                print(u'投诉信息已存在...')
            else:
                try:
                    cursor.execute(insert_sql)
                    conn.commit()
                    print(u'投诉信息插入成功...')
                except Exception as e:
                    print(u'投诉信息插入错误...', e)
                    conn.rollback()
        except Exception as e:
            print(u'查询信息错误...', e)
            conn.rollback()
        finally:
            cursor.close()
            conn.close()


if __name__ == '__main__':
    yuantong = YuanTong()
    page_num = input(u'请输入获取投诉信息的页数：')
    yuantong.getinfo(page_num)
