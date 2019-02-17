#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 18-6-5

import json
import os
import re
import requests


class TaoBaoEdu:
    def __init__(self):
        # 课程专页 id为103778
        self.coursehtml = "http://v.xue.taobao.com/learn.htm?courseId=103778"
        # 请求 self.resource 需要加 cookie
        self.resources = "http://v.xue.taobao.com/json/asynResource.do?courseId=103778&resourceId={}" \
                         "&resourceType=1&sectionId={}&last=false&liveToolType=-1&_ksTS=1550305173724_30" \
                         "&callback=jsonp31"

    @staticmethod
    def mkd():
        # 该课程对应的 108 个存放 ts文件 的文件夹
        for i in range(1, 109):
            finalpath = 'D:\\Python\\PycharmProject\\TBEdu\\{}'.format(i)
            f = os.path.exists(finalpath)
            if not f:
                os.makedirs(finalpath)
                print('make file success...')
            else:
                print('file already exists...')

    def gethtml(self):
        s = requests.session()
        res_headers = {
            # cookie（动态加载视频的cookie） 容易失效，需要在采集前添加
            'Cookie': '自行登录后，在动态加载视频的响应中获取'
        }
        r1 = s.get(self.coursehtml)
        # 解析获取所有课程的ID
        pattern = r'{.*?"courseId":103778,"id":(.*?),.*?"beginTimeStr1":"","id":(.*?),.*?' \
                  r'"sellerId":(.*?),"status":0,"title":"(.*?)".*?}'
        ids = re.findall(pattern, r1.text, re.S)

        # i 对应 108个文件夹
        for i in range(1, len(ids) + 1):
            # 构造访问每个视频的信息，处理部分非常规标题
            title = str(ids[i-1][3]).replace(".avi", "").replace(" ", "").replace("&hellip;", "")
            print(title)
            # 判断是否已存在最终合成视频，用于中断后继续操作
            final_path = "D:\\Python\\PycharmProject\\FinalTBEdu\\{}.mp4".format(title)
            f = os.path.exists(final_path)
            if not f:
                resource_url = self.resources.format(ids[i - 1][1], ids[i - 1][0])
                r_resource = s.get(resource_url, headers=res_headers)

                # 提取每个视频中的 m3u8 链接，以及 key
                m3u8_json = re.findall(r'jsonp31\((.*?)\)', r_resource.text, re.S)
                m3u8_json = json.loads(m3u8_json[0])

                ud_url = m3u8_json['data']['resource']['extObj']['videoPlayInfo']['webUrlMap']['ud']
                authkey = m3u8_json['data']['resource']['authority']['authKey']

                # 得到m3u8文件内容
                r_ud_url = s.get(ud_url + "?auth_key=" + authkey)
                fand_ts_url = re.findall(r'#EXTINF:.*?,(.*?)\.ts', r_ud_url.text, re.S)
                nums = len(fand_ts_url)
                for num in range(1, nums + 1):
                    # 请求m3u8文件中，每个ts链接
                    short_url = str(fand_ts_url[num - 1]).replace('\n', '') + '.ts'
                    print(short_url)
                    res_ts = s.get(short_url)
                    b_num = num
                    if num < 10:
                        b_num = '00' + str(num)
                    if 9 < num < 100:
                        b_num = '0' + str(num)
                    with open('D:\\Python\\PycharmProject\\TBEdu\\{}\\{}.ts'.format(i, b_num), 'wb') as f:
                        f.write(res_ts.content)
                        print('OK')
                # 在为视频命名时注意文件名不能包含空格
                os.system('copy /b D:\\Python\\PycharmProject\\TBEdu\\{}\\*.ts '
                          'D:\\Python\\PycharmProject\\FinalTBEdu\\{}.mp4'.format(i, title))
                print('make vedio success...')
            else:
                print('vedio already exists...')


if __name__ == '__main__':
    taobaoedu = TaoBaoEdu()
    taobaoedu.gethtml()
