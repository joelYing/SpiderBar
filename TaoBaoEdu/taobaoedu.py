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
            'Cookie': 'miid=1160271546849586574; cna=I4twEVCBYiwCAdxzFy+naXZk; tg=0; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; t=c379c7409659dd137ad549b87449ae16; UM_distinctid=16d3a1638474ba-01f3dc3356a1e2-5b1c3511-100200-16d3a1638484cf; cookie2=19acf53b2c1a15975bc0cff70dce1a2e; v=0; _tb_token_=681ba7be0393; CNZZDATA1272960300=692079039-1572950774-%7C1572950774; unb=2647660185; uc3=lg2=VFC%2FuZ9ayeYq2g%3D%3D&nk2=1CAkEYIyOIBEzX%2BAYVbSmums&id2=UU6lSsTTvJbvbA%3D%3D&vt3=F8dByuay24tF%2FGfkLLQ%3D; csg=1b3b1468; lgc=%5Cu98CE%5Cu4E2D%5Cu4E00%5Cu5339%5Cu72FC12138000; cookie17=UU6lSsTTvJbvbA%3D%3D; dnk=%5Cu98CE%5Cu4E2D%5Cu4E00%5Cu5339%5Cu72FC12138000; skt=c08a312f06492afa; existShop=MTU3Mjk1NDAwNg%3D%3D; uc4=nk4=0%401vEAHSSkoAxmo1uSa9b2EkUzErj2sT6sfVarM4E%3D&id4=0%40U2xo%2BvhOM3yTd6SmZ1uUlLe5xInf; tracknick=%5Cu98CE%5Cu4E2D%5Cu4E00%5Cu5339%5Cu72FC12138000; _cc_=VFC%2FuZ9ajQ%3D%3D; _l_g_=Ug%3D%3D; sg=05f; _nk_=%5Cu98CE%5Cu4E2D%5Cu4E00%5Cu5339%5Cu72FC12138000; cookie1=UtJX3G2wolm77D%2FQUyesMdmZT1O4vEyOkjqydHUVl3U%3D; mt=ci=21_1; uc1=cookie16=URm48syIJ1yk0MX2J7mAAEhTuw%3D%3D&cookie21=V32FPkk%2FgihF%2FS5nr3O5&cookie15=U%2BGCWk%2F75gdr5Q%3D%3D&existShop=false&pas=0&cookie14=UoTbnxEl6OUqjA%3D%3D&tag=8&lng=zh_CN; l=dBS7glRmqcSzq1hUKOfw5uI8L17T4QAb8sPzw4OG2ICP_qCeJ2B5WZdfDh8wCnGV3se6R3zUxM0LBDT8Vy4ehBmvVPAaqFi9_pLeR; isg=BMzMnxKe_d5D_umfmuE-2fsDnSo-rXHIcbgIaCaPg3cIsW27ThGSPsEHUbmJ-agH'
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
