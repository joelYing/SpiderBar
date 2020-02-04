#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 2020-02-02


import json
import time
import random
from scapy.layers.inet import TCP
from scapy.all import sniff
from scapy_http import http
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Ximalaya import XiMaDownloader

"""
注意请修改 make_dir() 中的下载路径
2019-10-28 -- 喜马更新，https://www.ximalaya.com/youshengshu/19139131/ 源代码压缩
"""


class XiMa(object):
    def __init__(self):
        self.xmd = XiMaDownloader.XiMaDownloader()

    def index_choose(self):
        c_num = input(u'请输入对应操作的选项：\n'
                      u'1、下载整部免费有声书\n'
                      u'2、下载单个音源\n'
                      u'3、下载已付费有声书\n'
                      u'4、返回\n')
        if c_num == '1':
            xm_id = input(u'请输入要获取的喜马拉雅节目的ID：')
            xima.get_free_fm(xm_id)
            self.index_choose()
        elif c_num == '2':
            xm_id = input(u'请输入要获取的音源：')
            print(xm_id)
            self.index_choose()
        elif c_num == '3':
            xm_id = input(u'请输入要获取的已付费的喜马拉雅节目的ID：')
            xima.get_pay_fm(xm_id)
            self.index_choose()
        elif c_num == '4':
            print('结束')
        else:
            pass

    def get_free_fm(self, xm_fm_id):
        fm_count, fm_path, max_page = self.xmd.get_fm(xm_fm_id)
        if max_page:
            for page in range(1, int(max_page) + 1):
                print('第' + str(page) + '页')
                r = self.xmd.get_free_sign(xm_fm_id, page)
                r_json = json.loads(r.text)
                for audio in r_json['data']['tracksAudioPlay']:
                    audio_title = str(audio['trackName']).replace(' ', '')
                    audio_src = audio['src']
                    self.xmd.save_fm2local(audio_title, audio_src, fm_path)
                # 每爬取1页，30个音频，休眠3秒
                time.sleep(3)
        else:
            print('no max_page')

    def get_pay_fm(self, xm_fm_id):
        fm_count, fm_path, max_page = self.xmd.get_fm(xm_fm_id)
        if max_page:
            # 这里应该是 fm_count
            r = self.xmd.get_pay_album(xm_fm_id, fm_count)
            r_json = json.loads(r.text)
            tracks = r_json['data']['tracks']['list']
            for i, track in enumerate(tracks):
                if i > 22:
                    audio_id = track['trackId']
                    audio_title = str(track['title']).replace(' ', '')
                    audio_url = self.xmd.yss_api.format(str(track['albumId']), audio_id)
                    print(audio_title, audio_url)
                    real_url = self.auto_click(audio_url)
                    self.xmd.save_fm2local(audio_title, real_url, fm_path)
                    # 每爬取1页，30个音频，休眠1~3秒
                    time.sleep(random.randint(1, 3))
        else:
            print('no max_page')

    def auto_click(self, url):
        """
        参数url为对应的VIP音频的播放页面，selenium访问页面后，带上cookie（1&_token）模拟登陆再次访问，前提你已经是会员
        等待页面加载完成，通过selenium+Chromedriver的无头浏览器模拟点击音频播放按钮
        scapy开始抓点击后音频真实地址的数据包，退出browser，解析包
        注意click与抓包的顺序，先点击再抓包
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        browser = webdriver.Chrome(chrome_options=chrome_options)
        # browser = webdriver.Chrome()
        browser.get(url)
        browser.add_cookie({
            # 此处xxx.com前，需要带点，注意domain也是cookie必须的
            'domain': '.ximalaya.com',
            'name': '1&_token',
            'value': 'xxx'
        })
        browser.get(url)
        time.sleep(4)
        print('开始抓包')
        # selenium 点击播放按钮
        browser.find_element_by_css_selector(".play-btn.fR_").click()
        # 下面的iface是电脑网卡的名称 count是捕获报文的数目
        pkts = sniff(filter="tcp and port 80", iface="Qualcomm Atheros AR956x Wireless Network Adapter", count=5)
        print('抓包成功,开始解析', pkts)
        browser.quit()
        for pkt in pkts:
            if TCP in pkt and pkt.haslayer(http.HTTPRequest):
                # print(pkt.show())
                http_header = pkt[http.HTTPRequest].fields
                req_url = 'http://' + bytes.decode(http_header['Host']) + bytes.decode(http_header['Path'])
                # print(req_url)
                return req_url


if __name__ == '__main__':
    xima = XiMa()
    xima.index_choose()
