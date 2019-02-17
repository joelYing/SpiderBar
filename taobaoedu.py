#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 18-6-5
import json
import os
import re
import requests


class TaoBaoEdu:
    def __init__(self):
        self.coursehtml = "http://v.xue.taobao.com/learn.htm?courseId=103778"
        # 请求 self.resource 需要加 cookie
        self.resources = "http://v.xue.taobao.com/json/asynResource.do?courseId=103778&resourceId={}" \
                         "&resourceType=1&sectionId={}&last=false&liveToolType=-1&_ksTS=1550305173724_30" \
                         "&callback=jsonp31"

    @staticmethod
    def mkd():
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
            'Cookie': 'miid=1160271546849586574; cna=I4twEVCBYiwCAdxzFy+naXZk; tg=0; '
                      'x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; '
                      'thw=cn; t=a29059ce8774dfc44543e0e7e46c3c8c; UM_distinctid=168f15464212c-0a538f6'
                      '7e6b4ae-38395f0b-100200-168f1546422fe; tracknick=%5Cu5C14%5Cu7FBD532421; lgc=%5'
                      'Cu5C14%5Cu7FBD532421; mt=ci=20_1&np=; cookie2=11ddd9256802cc76b0e39ff2fd463922; '
                      'v=0; _tb_token_=53371e388a89e; dnk=%5Cu5C14%5Cu7FBD532421; _cc_=U%2BGCWk%2F7og%3'
                      'D%3D; unb=2583435601; sg=114; _l_g_=Ug%3D%3D; skt=b70af59a429f911d; cookie1=BxSp'
                      'TR2RxDA5i1XYzlaATNwsOlRu8ywczHkqxxd8l0E%3D; csg=050356a0; uc3=vt3=F8dByE0EgWRoby'
                      'vUYbc%3D&id2=UU26%2F3q0l7x2KQ%3D%3D&nk2=1QYRT%2FH4al9thQ%3D%3D&lg2=URm48syIIVrS'
                      'KA%3D%3D; existShop=MTU1MDMyOTE1OQ%3D%3D; _nk_=%5Cu5C14%5Cu7FBD532421; cookie17'
                      '=UU26%2F3q0l7x2KQ%3D%3D; l=AqurfcSJPKppBhnKhuur8hUBu8SVwL9C; CNZZDATA1272960300='
                      '844935236-1550236270-null%7C1550326568; uc1=cookie16=V32FPkk%2FxXMk5UvIbNtImtMfJ'
                      'Q%3D%3D&cookie21=VFC%2FuZ9aiKCaj7AzMHh1&cookie15=WqG3DMC9VAQiUQ%3D%3D&existShop=f'
                      'alse&pas=0&cookie14=UoTZ5OML1Q1Jyg%3D%3D&tag=8&lng=zh_CN; isg=BL-_SgQK3544ItuCZVb'
                      'Snc4bTpPgxxNGx5SciVGMzm60YN3iWXBrlkE2onA7OOu-'
        }
        r1 = s.get(self.coursehtml)
        # 解析获取所有课程的ID
        pattern = r'{.*?"courseId":103778,"id":(.*?),.*?"beginTimeStr1":"","id":(.*?),.*?' \
                  r'"sellerId":(.*?),"status":0,"title":"(.*?)".*?}'
        ids = re.findall(pattern, r1.text, re.S)

        # i 对应 108个文件夹
        for i in range(1, len(ids) + 1):
            # 构造访问每个视频的信息
            title = str(ids[i-1][3]).replace(".avi", "").replace(" ", "").replace("&hellip;", "")
            print(title)
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
