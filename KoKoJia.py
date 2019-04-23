#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:joel
# time:2019/3/12 18:26

import os
import re
import sys

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import requests

reload(sys)
sys.setdefaultencoding('utf-8')

class KoKoJia:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
        }
        self.cookie = {
            'Cookie': 'Hm_lvt_f530f7624f8a05758b78e413af3d70ca=1552372643; Hm_lvt_69a9e7b64ab4ee86e58df7fde25d232a=1552372644; hm_t_vis_89943=0; PHPSESSID=ev1g0fqt48umlimpaanfbkmah2; kkj_path=e13ac427d818cb874853cc1db161243f; kkj_userid=10524698; kkj_key=215e6c1c04e698d2fdcc0dc1765a900d; Hm_lvt_bae077bf678cc3da3549821dd25ddf30=1552372681; Hm_lpvt_bae077bf678cc3da3549821dd25ddf30=1552372687; Qs_lvt_186397=1552372696; course_player_lesson=51931; Qs_pv_186397=2511030017581781000%2C1298944550910456300%2C3798883090333389000%2C1999882891168709000%2C4246880754277030000; course_player_time=597; Hm_lpvt_f530f7624f8a05758b78e413af3d70ca=1552386710; Hm_lpvt_69a9e7b64ab4ee86e58df7fde25d232a=1552386710'
        }

    @staticmethod
    def mkd():
        # 该课程对应的 108 个存放 ts文件 的文件夹
        for i in range(1, 18):
            finalpath = 'D:\\Python\\PycharmProject\\KoKoJia\\{}'.format(i)
            f = os.path.exists(finalpath)
            if not f:
                os.makedirs(finalpath)
                print'make file success...'
            else:
                print 'file already exists...'

    def gethtml(self):
        s = requests.session()
        r1 = s.get("http://www.kokojia.com/course-3643.html")
        r1.encoding = "utf-8"
        lesson_url_list = re.findall(r'<span class="f-fl f-thide ks">(.*?)</span>.*?<h4><a class='
                                     r'"f-fl f-thide ksname" title="(.*?)" href="(.*?)".*?>.*?</h4>', r1.text, re.S)
        for i in range(1, len(lesson_url_list) + 1):
            # 构造访问每个视频的信息，处理部分非常规标题
            title = lesson_url_list[i - 1][0]  + lesson_url_list[i - 1][1]
            lesson_url = lesson_url_list[i - 1][2]
            print title, lesson_url
            # 判断是否已存在最终合成视频，用于中断后继续操作
            final_path = "D:\\Python\\PycharmProject\\FinalKoKoJia\\{}.mp4".format(title)
            f = os.path.exists(final_path)
            if not f:
                r2 = s.get(lesson_url, headers=self.headers, cookies=self.cookie)
                r2.encoding = "utf-8"
                m3u8_url = re.findall('"name":".*?", "url":"(.*?)"', r2.text, re.S)
                print(r2.text)
                print(m3u8_url)
                url_head = re.sub('kokojia_\d+\.m3u8', '', m3u8_url[0])
                r_m3u8 = s.get(m3u8_url[0])
                uri_key = re.findall('EXT-X-KEY:METHOD=AES-128,URI="(.*?)"', r_m3u8.text, re.S)
                vi = re.findall('.*?key=(.*?)', uri_key[0], re.S)[0]
                print(vi)
                key = s.get(uri_key[0]).text
                print key, vi
                # 得到m3u8文件内容
                ts_tail_list = re.findall('#EXTINF:.*?,(.*?)\.ts', r_m3u8.text, re.S)
                nums = len(ts_tail_list)
                for num in range(1, nums + 1):
                    # 请求m3u8文件中，每个ts链接
                    ts_url = url_head + ts_tail_list[num - 1].replace('\n', '') + '.ts'
                    print ts_url
                    cryptor = AES.new(vi, AES.MODE_CBC, key)
                    res_ts = s.get(ts_url)
                    b_num = num
                    if num < 10:
                        b_num = '00' + str(num)
                    if 9 < num < 100:
                        b_num = '0' + str(num)
                    with open('D:\\Python\\PycharmProject\\KoKoJia\\{}\\{}.ts'.format(i, b_num), 'wb') as f:
                        f.write(cryptor.decrypt(res_ts.content))
                        print 'OK'
                    break
                # 在为视频命名时注意文件名不能包含空格
                os.system('copy /b D:\\Python\\PycharmProject\\KoKoJia\\{}\\*.ts '
                          'D:\\Python\\PycharmProject\\FinalKoKoJia\\{}.mp4'.format(i, title))
                print 'make vedio success...'
            else:
                print 'vedio already exists...'
            break


if __name__ == '__main__':
    kokojia = KoKoJia()
    kokojia.gethtml()
    # kokojia.mkd()
