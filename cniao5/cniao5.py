#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 18-6-5

"""
ts文件路径
https://vodi97egsxf.vod.126.net/vodi97egsxf/{}.ts

"""
import re
import os
import requests


class Cniao5(object):
    def __init__(self):
        self.file_path1 = 'D:\\Python\\PycharmProject\\Cniao5\\{}'
        self.file_path2 = 'D:\\Python\\PycharmProject\\FinalCniao5\\{}'

    @staticmethod
    def name_tool(name):
        if 'http' in name:
            name = str(name).split('http')[0]
        if '/' in name:
            name = str(name).replace('/', '')
        return name

    @staticmethod
    def mkd():
        """ 创建存放最终合成视频的文件夹 """
        for i in range(1, 25):
            finalpath = 'D:\\Python\\PycharmProject\\FinalCniao5\\{}'.format(i)
            f = os.path.exists(finalpath)
            if not f:
                os.makedirs(finalpath)
                print('make file success...')
            else:
                print('file already exists...')

    def mkds(self, path):
        f = os.path.exists(path)
        if not f:
            os.makedirs(path)
            print('make file success...')
        else:
            print('file already exists...')

    def gethtml(self):
        s = requests.session()
        r_chapters = s.get('https://www.cniao5.com/api/v1/course/10153/chapters')
        json_chapters = r_chapters.json()
        for chapter in json_chapters:
            # 每一个章节
            chapter_name = chapter['bsort']
            print(chapter_name)
            path1 = self.file_path1.format(chapter_name)
            f = os.path.exists(path1)
            if not f:
                os.makedirs(path1)
                print('make file success...')
            else:
                print('file already exists...')
            # 每一章节中的课程
            for lessons in chapter['lessons']:
                lessons_name = 'lessons' + str(lessons['bsort'])
                video_id = lessons['video_info']['vid']
                key = lessons['key']
                file_id = lessons['video_info']['file_id']
                print(lessons_name, video_id)
                # 每个视频创建一个视频id的文件夹
                path = 'D:\\Python\\PycharmProject\\Cniao5\\{}\\{}'.format(chapter_name, lessons_name)
                f = os.path.exists(path)
                # 基于中断后，创建文件时判断，若存在该文件夹则跳过对该视频的下载，若不存在则继续
                if not f:
                    os.makedirs(path)
                    print('2 make file success...')
                    # 通过合成 ts 文件为 mp4 下载
                    if video_id != 0:
                        r_lesson_m3u8 = s.post('https://www.cniao5.com/lesson/{}/urls'.format(video_id))
                        json_lesson_m3u8 = r_lesson_m3u8.json()
                        lesson_m3u8_url = 'http:' + json_lesson_m3u8['urls']['hd']
                        print(lesson_m3u8_url)
                        lesson_m3u8 = s.get(lesson_m3u8_url)
                        # 保存m3u8文件
                        # with open('D:\\Python\\PycharmProject\\Cniao5\\{}\\{}\\{}.txt'.format(
                        #         chapter_name, lessons_name, lessons_name), 'w') as f:
                        #     f.write(lesson_m3u8.text)
                        fand_url = re.findall(r'#EXTINF:.*?,(.*?)\.ts', lesson_m3u8.text, re.S)
                        nums = len(fand_url)
                        # for ts_url in fand_url:
                        for num in range(1, nums + 1):
                            short_url = 'https://vodi97egsxf.vod.126.net/vodi97egsxf/' + str(fand_url[num - 1]).replace('\n', '') + '.ts'
                            print(short_url)
                            res_ts = s.get(short_url)
                            # 命名ts文件为 001 002...形式，避免cmd合成出错
                            b_num = num
                            if num < 10:
                                b_num = '00' + str(num)
                            if 9 < num < 100:
                                b_num = '0' + str(num)
                            with open('D:\\Python\\PycharmProject\\Cniao5\\{}\\{}\\{}.ts'.format(
                                        chapter_name, lessons_name, b_num), 'wb') as f:
                                f.write(res_ts.content)
                                print('OK')
                        os.system('copy /b D:\\Python\\PycharmProject\\Cniao5\\{}\\{}\\*.ts  '
                                  'D:\\Python\\PycharmProject\\FinalCniao5\\{}\\{}.mp4'.format
                                  (chapter_name, lessons_name, chapter_name, lessons_name))
                    else:
                        # vid=0 的情况，通过找到 mp4 播放路径下载
                        r_0 = s.get('https://playvideo.qcloud.com/getplayinfo/v2/1255567694/{}'.format(file_id))
                        json_r_0 = r_0.json()
                        mp4_url = json_r_0['videoInfo']['sourceVideo']['url']
                        headers = {
                            'Referer': 'https://www.cniao5.com/lesson/play/{}.html'.format(key),
                        }
                        r_mp4 = s.get(mp4_url, headers=headers)
                        with open('D:\\Python\\PycharmProject\\FinalCniao5\\{}\\{}.mp4'.format
                                      (chapter_name, lessons_name), 'wb') as f:
                            f.write(r_mp4.content)
                        print(u'其他途径获取--ok')
                else:
                    print('2 file already exists...')


if __name__ == '__main__':
    cniao5 = Cniao5()
    cniao5.gethtml()
