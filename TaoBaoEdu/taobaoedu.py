#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 19-11-5

import json
import os
import re
import requests


class TaoBaoEdu:
    def __init__(self):
        # 存放ts文件
        self.path1 = 'D:\\Python\\PycharmProject\\TaoBaoEdu'
        # 存放mp4文件
        self.path2 = 'D:\\Python\\PycharmProject\\FinalTaoBaoEdu'
        # 课程专页 id为102063
        self.coursehtml = "http://v.xue.taobao.com/learn.htm?courseId={}"
        # 请求 self.resource 需要加 cookie
        self.resources = "http://v.xue.taobao.com/json/asynResource.do?courseId={}&resourceId={}" \
                         "&resourceType=1&sectionId={}&last=false&liveToolType=-1&_ksTS=1550305173724_30" \
                         "&callback=jsonp31"

    def mkd(self):
        # 该课程对应的 108 个存放 ts文件 的文件夹
        paths = [self.path1, self.path2]
        for path in paths:
            f = os.path.exists(path)
            if not f:
                os.makedirs(path)
                print('make file success...')
            else:
                print('file already exists...')

    def gethtml(self, course_id):
        s = requests.session()
        res_headers = {
            # cookie（动态加载视频的cookie） 容易失效，需要在采集前添加
            'Cookie': ''
        }
        r1 = s.get(self.coursehtml.format(course_id))
        # 解析获取所有课程的ID
        pattern = r'{.*?"courseId":.*?,"id":(.*?),.*?"beginTimeStr1":"","id":(.*?),.*?' \
                  r'"sections":\[],"sellerId":(.*?),"status":0,"title":"(.*?)".*?}'
        ids = re.findall(pattern, r1.text, re.S)
        # i 对应 108个文件夹
        for i in range(1, len(ids) + 1):
            ts_path = self.path1 + '\\{}'.format(i)
            f = os.path.exists(ts_path)
            if not f:
                os.makedirs(ts_path)
                print('make file success...')
            else:
                print('file already exists...')
            # 构造访问每个视频的信息，处理部分非常规标题
            title = re.sub(r'&.*?;|\.avi|" "', '', str(ids[i-1][3]))
            title = str(title).replace(" ", "")
            print(title)
            # 判断是否已存在最终合成视频，用于中断后继续操作
            final_path = self.path2 + "\\{}.mp4".format(title)
            f = os.path.exists(final_path)
            if not f:
                resource_url = self.resources.format(course_id, ids[i - 1][1], ids[i - 1][0])
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
                    with open(self.path1 + '\\{}\\{}.ts'.format(i, b_num), 'wb') as f:
                        f.write(res_ts.content)
                        print('OK')
                # 在为视频命名时注意文件名不能包含空格
                os.system('copy /b {}\\{}\\*.ts {}\\{}.mp4'.format(self.path1, i, self.path2, title))
                print('make vedio success...')
            else:
                print('vedio already exists...')


if __name__ == '__main__':
    taobaoedu = TaoBaoEdu()
    taobaoedu.mkd()
    courseId = input(u'请输入要下载的课程courseId：')
    taobaoedu.gethtml(courseId)
