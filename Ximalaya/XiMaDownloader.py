# author:joel 2020-02-02
import hashlib
import json
import math
import os
import random
import time
import requests


class XiMaDownloader:
    def __init__(self):
        self.base_url = 'https://www.ximalaya.com'
        # 有声书
        self.yss_api = 'https://www.ximalaya.com/youshengshu/{}/{}'
        # 需要带上sign访问的api，适用于免费的音频的播放源
        self.free_sign_api = 'https://www.ximalaya.com/revision/play/album?albumId={}&pageNum={}&sort=0&pageSize=30'
        # 获取单个免费音频api （trackId）
        self.free_track_api = 'http://mobile.ximalaya.com/mobile/redirect/free/play/{}/2'
        # 时间戳api
        self.time_api = 'https://www.ximalaya.com/revision/time'
        # 获取节目总音源个数与节目名
        self.album_api = 'https://www.ximalaya.com/revision/album?albumId={}'
        # 获取指定albumID的每一页音频的ID等track信息
        self.album_tracks_api = 'https://www.ximalaya.com/revision/album/v1/getTracksList?albumId={}&pageNum={}'
        # APP抓包得到，可用于获取付费节目总音源个数与节目名，获取音集所有音频ID，通过改变pageSize的大小，（albumId, pageSize）
        self.pay_size_api = 'http://180.153.255.6/mobile-album/album/page/ts-1569206246849?ac=WIFI&albumId={}' \
                            '&device=android&isAsc=true&isQueryInvitationBrand=true&isVideoAsc=true&pageId=1' \
                            '&pageSize={}'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
        }
        self.s = requests.session()

    def get_time(self):
        """
        获取服务器时间戳
        """
        r = self.s.get(self.time_api, headers=self.header)
        r_time = r.text
        return r_time

    def get_sign(self):
        """
        获取sign： md5(ximalaya-服务器时间戳)(100以内随机数)服务器时间戳(100以内随机数)现在时间戳
        """
        nowtime = str(round(time.time() * 1000))
        servertime = self.get_time()
        sign = str(hashlib.md5("himalaya-{}".format(servertime).encode()).hexdigest()) + "({})".format(
            str(round(random.random() * 100))) + servertime + "({})".format(str(round(random.random() * 100))) + nowtime
        self.header["xm-sign"] = sign

    @classmethod
    def make_dir(cls, xm_fm_id):
        """
        保存路径，请自行修改，这里是以有声书ID作为文件夹的路径
        """
        fm_path = 'E:\\{}\\'.format(xm_fm_id)
        f = os.path.exists(fm_path)
        if not f:
            os.makedirs(fm_path)
            print('make file success...')
        else:
            print('file already exists...')
        return fm_path

    def get_fm(self, xm_fm_id):
        """
        根据albumID解析 免费 fm信息
        """
        # 根据有声书ID构造url
        r_fm_url = self.s.get(self.album_api.format(xm_fm_id), headers=self.header)
        r_fm_json = json.loads(r_fm_url.text)
        fm_title = r_fm_json['data']['mainInfo']['albumTitle']
        fm_count = r_fm_json['data']['tracksInfo']['trackTotalCount']
        fm_page_size = r_fm_json['data']['tracksInfo']['pageSize']
        print('书名：' + fm_title)
        # 新建有声书ID的文件夹
        fm_path = self.make_dir(xm_fm_id)
        # 取最大页数，向上取整
        max_page = math.ceil(fm_count/fm_page_size)
        return fm_count, fm_path, max_page

    def get_free_sign(self, xm_fm_id, page):
        """
        下载免费的音频的播放源信息
        :param xm_fm_id:
        :param page:
        :return: response
        """
        self.get_sign()
        response = self.s.get(self.free_sign_api.format(xm_fm_id, page), headers=self.header)
        return response

    def get_pay_album(self, xm_fm_id, max_page):
        """
        获取付费的音频的播放源信息
        :param xm_fm_id:
        :param max_page:
        :return: response
        """
        response = self.s.get(self.pay_size_api.format(xm_fm_id, max_page), headers=self.header)
        return response

    def save_fm2local(self, title, src, path):
        """
        保存音频到本地
        :param title:
        :param src:
        :param path:
        """
        r_audio_src = requests.get(src, headers=self.header)
        m4a_path = path + title + '.m4a'
        if not os.path.exists(m4a_path):
            with open(m4a_path, 'wb') as f:
                f.write(r_audio_src.content)
                print(title + '保存完毕...')
        else:
            print(title + 'm4a已存在')
