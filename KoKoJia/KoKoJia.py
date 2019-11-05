#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 19/3/12


import os
import re
from Crypto.Cipher import AES
import requests


class KoKoJia:
    def __init__(self):
        self.url = 'http://www.kokojia.com/{}.html '
        self.path1 = 'D:\\Python\\PycharmProject\\KoKoJia'
        self.path2 = 'D:\\Python\\PycharmProject\\FinalKoKoJia'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
        }
        self.cookie = {
            'Cookie': ''
        }

    def mkd(self):
        # 创建存放ts文件以及mp4文件的文件夹
        paths = [self.path1, self.path2]
        for path in paths:
            f = os.path.exists(path)
            if not f:
                os.makedirs(path)
                print('make file success...')
            else:
                print('file already exists...')

    def gethtml(self, index_url):
        s = requests.session()
        r1 = s.get(self.url.format(index_url))
        r1.encoding = "utf-8"
        lesson_url_list = re.findall(r'<span class="f-fl f-thide ks">(.*?)</span>.*?<h4><a class='
                                     r'"f-fl f-thide ksname" title="(.*?)" href="(.*?)".*?>.*?</h4>', r1.text, re.S)
        for i in range(1, len(lesson_url_list) + 1):
            ts_path = self.path1 + '\\{}'.format(i)
            f = os.path.exists(ts_path)
            if not f:
                os.makedirs(ts_path)
                print('make file success...')
            else:
                print('file already exists...')
            # 构造访问每个视频的信息，处理部分非常规标题
            title = lesson_url_list[i - 1][0] + lesson_url_list[i - 1][1]
            lesson_url = lesson_url_list[i - 1][2]
            print(title, lesson_url)
            # 判断是否已存在最终合成视频，用于中断后继续操作
            final_path = self.path2 + "\\{}.mp4".format(i)
            f = os.path.exists(final_path)
            if not f:
                r2 = s.get(lesson_url, headers=self.headers, cookies=self.cookie)
                r2.encoding = "utf-8"
                m3u8_url = re.findall('"name":".*?", "url":"(.*?)"', r2.text, re.S)
                url_head = re.sub('kokojia_\d+\.m3u8', '', m3u8_url[0])
                r_m3u8 = s.get(m3u8_url[0])
                uri_key = re.findall('EXT-X-KEY:METHOD=AES-128,URI="(.*?)"', r_m3u8.text, re.S)
                key = s.get(uri_key[0], cookies=self.cookie).text
                print(key)
                # 得到m3u8文件内容
                ts_tail_list = re.findall('#EXTINF:.*?,(.*?)\.ts', r_m3u8.text, re.S)
                nums = len(ts_tail_list)
                for num in range(1, nums + 1):
                    # if num < 100:
                    # 请求m3u8文件中，每个ts链接
                    ts_url = url_head + ts_tail_list[num - 1].replace('\n', '') + '.ts'
                    print(ts_url)
                    vi = bytes('{:016}'.format(num - 1).encode('utf-8'))
                    # vi = bytes('0b' + '{:014b}'.format(num - 1))
                    # print(key, vi)
                    cryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC, vi)
                    res_ts = s.get(ts_url)
                    b_num = num
                    if num < 10:
                        b_num = '00' + str(num)
                    if 9 < num < 100:
                        b_num = '0' + str(num)
                    with open(self.path1 + '\\{}\\{}.ts'.format(i, b_num), 'wb') as f:
                        f.write(cryptor.decrypt(res_ts.content))
                        print('OK')
                    # break
                # 在为视频命名时注意文件名不能包含空格
                os.system("copy /b {}\\{}\\*.ts {}\\{}.mp4".format(self.path1, i, self.path2, i))
                print('make vedio success...')
            else:
                print('vedio already exists...')
            # break


if __name__ == '__main__':
    kokojia = KoKoJia()
    kokojia.mkd()
    url = input(u'请输入要下载的课程：')
    kokojia.gethtml(url)
