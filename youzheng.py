#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:joel
# time:2019/2/20 10:39

import re
import pymysql
import requests


def youzheng():
    ses = requests.session()
    for i in range(1, 2346):
        r1 = ses.get("http://sswz.spb.gov.cn/chooseView.do?basePageNo={}".format(i))
        ss = re.findall(r'<div class="news-blocks">.*?<a href="(.*?)">(.*?)</a>.*?'
                        r'<em>\[&nbsp;(.*?)&nbsp;]</em>.*?</div>', r1.text, re.S)

        if '2018-' in r1.text:
            for s in ss:
                detailurl = "http://sswz.spb.gov.cn" + s[0]
                title = s[1]
                time = s[2]
                print(detailurl, title, time)

                if '2018-' in time:
                    r2 = ses.get(detailurl)
                    # print(r2.text)
                    messages = re.findall(r'<div class="message">.*?<a href="#" class="name">(.*?)</a>'
                                          r'.*?class="body">(.*?)</span>.*?</div>.*?<div class="message">.*?'
                                          r'<a href="#" class="name">(.*?)</a>'
                                          r'.*?class="body">(.*?)</span>.*?</div>', r2.text, re.S)

                    for message in messages:
                        messagetype1 = message[0]
                        messageinfo1 = message[1].strip().replace("\r", "")

                        tsmessage1 = messagetype1 + ": \"" + messageinfo1 + "\""

                        messagetype2 = message[2]
                        messageinfo2 = message[3].strip().replace("\r", "")

                        tsmessage2 = messagetype2 + ": \"" + messageinfo2 + "\""
                        # print(tsmessage1 + "\n" + tsmessage2)
                        # insertmysql(detailurl, title, time, tsmessage1, tsmessage2)
                else:
                    break
        else:
            break


def insertmysql(detailurl, title, time, tsmessage1, tsmessage2):
    conn = pymysql.connect(host='localhost', port=3306, user='',passwd='', db='sswz')
    cursor = conn.cursor()

    insert_sql = "insert into `sswz` (`tousu_url`, `tousu_title`, `tousu_time`, `comsumer_info`, `reply_info`" \
                 ")values('%s','%s','%s','%s','%s')" % (detailurl, title, time, tsmessage1, tsmessage2)

    select_sql = "select `comsumer_info` from `sswz` where `comsumer_info`='%s'" % tsmessage1

    try:
        response = cursor.execute(select_sql)
        conn.commit()
        if response == 1:
            print(u'该投诉信息存在...')
        else:
            try:
                cursor.execute(insert_sql)
                conn.commit()
                print(u'投诉信息插入成功...')
            except Exception as e:
                print(u'投诉信息插入错误...', e)
                conn.rollback()
    except Exception as e:
        print(u'查询错误...', e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


youzheng()
