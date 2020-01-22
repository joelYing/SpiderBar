#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 20-01-22

import random
import re
import time
import pymysql
import execjs
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from Agetv.faua import FaUa
# 避免出现请求不安全的警告
requests.packages.urllib3.disable_warnings()


class AutoSave(object):
    def __init__(self):
        self.row_lists = []
        self.select_text = '/完结动漫/'
        self.user_agent = FaUa.get_ua()
        # 最好把BAIDUID、STOKEN、BDUSS这三个参数提前从浏览器中拿出来
        self.baiduid = ''
        self._stoken_bduss = ''
        # 用于selenium登录网盘的账号密码
        self.username = ''
        self.password = ''
        self.pan_post = 'https://pan.baidu.com/share/verify?surl={}&t={}&channel=chunlei' \
                        '&web=1&app_id=250528&bdstoken=08a7da93cf25d7935788a123e3e10c3d' \
                        '&logid={}&clienttype=0'
        self.create_dir_post = 'https://pan.baidu.com/api/create?a=commit&channel=chunlei' \
                               '&app_id=250528&bdstoken=undefined&channel=chunlei&web=1' \
                               '&app_id=250528&bdstoken=08a7da93cf25d7935788a123e3e10c3d' \
                               '&logid={}&clienttype=0'
        self.transfer_post = 'https://pan.baidu.com/share/transfer?shareid={}' \
                             '&from={}&ondup=newcopy&async=1&channel=chunlei' \
                             '&web=1&app_id=250528&bdstoken=08a7da93cf25d7935788a123e3e10c3d' \
                             '&logid={}&clienttype=0'
        self.pan_s_url = 'https://pan.baidu.com/s/1{}'
        self.create_dir_data = {'isdir': '1', 'size':	'', 'block_list': [], 'method': 'post', 'dataType':	'json'}
        self.pwd_data = {'vcode': '', 'vcode_str': ''}
        self.headers = {
            'User-Agent': self.user_agent,
            'Host': 'pan.baidu.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://pan.baidu.com',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        self.t = int(round(time.time() * 1000))

    def get_logid(self, baidu_id):
        with open('boot.js', encoding='utf-8') as f:
            bootjs = f.read()
        js_obj = execjs.compile(bootjs)
        res = js_obj.call('getLogId', baidu_id)
        return res

    def enter_pwd(self, source_filename, pan_url, pan_pwd):
        """
        通过execjs运行生成logid的代码，获取后跟密码等参数一起发送post请求，将返回的BDCLND参数作为cookie加入到get
        'https://pan.baidu.com/s/1xxx' 的请求头中，可以正常访问资源文件页面
        """
        session = requests.session()
        # 请求需要密码的网盘资源的url；verify=False 避免频繁尝试被封，断开SSL，但是这个请求是不安全的
        r_baiduid = session.get(pan_url, headers={'user-agent': self.user_agent}, verify=False)
        # 获得当前的BAIDUID用于生成logid
        if '404' in r_baiduid.url:
            print('404，找不到页面')
            self.update_status(pan_url)
            return 'fail'
        # baiduid = r_baiduid.cookies['BAIDUID']
        logid = self.get_logid(self.baiduid)
        surl = pan_url.split('surl=')[1]
        self.pwd_data['pwd'] = pan_pwd
        self.headers['Referer'] = pan_url
        # 带密码的post请求，成功可以访问'https://pan.baidu.com/s/1xxx'页面
        r = session.post(self.pan_post.format(surl, self.t, logid), data=self.pwd_data, headers=self.headers, verify=False)
        # 返回带有randsk的json数据，取得bdclnd
        bdclnd = 'BDCLND=' + r.json()['randsk']
        main_data = {
            'source_filename': source_filename, 'bdclnd': bdclnd, 'surl': surl, 'pan_url': pan_url
        }
        # 调用新建文件夹以及转存的请求
        self.transfer_save(main_data)

    def transfer_save(self, main_data):
        """
        免密的发送转存请求时不需要BDCLND
        """
        pan_url = ''
        if len(main_data) == 4:
            # 访问'https://pan.baidu.com/s/1xxx'的请求头
            self.headers['Cookie'] = main_data['bdclnd']
            # 'https://pan.baidu.com/s/1xxx'
            pan_url = self.pan_s_url.format(main_data['surl'])
        else:
            self.headers['Referer'] = main_data['pan_url']
            pan_url = main_data['pan_url']
        r_pan_url = requests.get(pan_url, headers=self.headers, verify=False)
        r_pan_url.encoding = 'utf-8'
        if '404' in r_pan_url.url or '此链接分享内容可能因为涉及侵权、色情、反动、低俗等信息，无法访问' in r_pan_url.text:
            print('404，找不到页面')
            self.update_status(main_data['pan_url'])
            return 'fail'
        # 利用正则 获取 转存资源的post请求 所需的三个参数
        params = re.findall(r'yunData\.SHARE_ID = "(.*?)";.*?yunData\.SHARE_UK = '
                            r'"(.*?)";.*?yunData\.FS_ID = "(.*?)";', r_pan_url.text, re.S)[0]
        logid = self.get_logid(self.baiduid)
        shareid, from_id, fsidlist = params[0], params[1], params[2]
        transfer_url = self.transfer_post.format(shareid, from_id, logid)
        # 处理创建文件夹不能使用的字符
        source_filename = re.sub(':|<|\||>|\*|\?|/|♪|', '', main_data['source_filename'])
        create_path = '/完结动漫/' + source_filename
        # 新建文件夹请求所需的data参数
        self.create_dir_data['path'] = create_path
        self.headers['Referer'] = pan_url
        if len(main_data) == 4:
            self.headers['Cookie'] = main_data['bdclnd'] + ';' + self._stoken_bduss
        else:
            self.headers['Cookie'] = self._stoken_bduss
        # 需要两个参数BDUSS，STOKEN
        r_create_dir = requests.post(self.create_dir_post.format(logid), data=self.create_dir_data,
                                     headers=self.headers, verify=False)
        print('创建文件夹成功', r_create_dir.json())
        # 需要三个参数BDUSS，BDCLND，STOKEN
        r_transfer = requests.post(transfer_url, data={'fsidlist': '[' + str(fsidlist) + ']', 'path': create_path},
                                   headers=self.headers, verify=False)
        print('转存资源成功', r_transfer.text)
        time.sleep(random.randint(0, 3))
        return 'success'

    def s_enter_pwd(self, source_filename, pan_url, pan_pwd):
        """
        selenium操作的输入密码
        """
        browser = webdriver.Chrome()
        browser.get(pan_url)
        time.sleep(3)
        if '404' in browser.current_url:
            print('404，找不到页面')
            self.update_status(pan_url)
            time.sleep(10)
            browser.close()
        # print(browser.page_source)
        browser.find_element_by_id("wkwj9A").send_keys(pan_pwd)
        time.sleep(2)
        browser.find_element_by_id("wkwj9A").send_keys(Keys.ENTER)
        time.sleep(5)
        print(browser.current_url)
        # 点击保存到网盘，跳出登录框
        browser.find_element_by_css_selector('.g-button.g-button-blue').click()
        time.sleep(5)
        # 输入账号密码
        browser.find_element_by_id("TANGRAM__PSP_10__footerULoginBtn").click()
        time.sleep(3)
        browser.find_element_by_id("TANGRAM__PSP_10__userName").send_keys(self.username)
        browser.find_element_by_id("TANGRAM__PSP_10__password").send_keys(self.password)
        browser.find_element_by_id("TANGRAM__PSP_10__submit").click()
        # 若出现旋转验证码
        try:
            slid_ing = browser.find_element_by_class_name('vcode-spin-button')
            if slid_ing:
                while True:
                    ActionChains(browser).click_and_hold(on_element=slid_ing).perform()
                    time.sleep(0.2)
                    for track in [0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4]:
                        ActionChains(browser).move_by_offset(xoffset=track, yoffset=0).perform()
                    try:
                        ActionChains(browser).release(on_element=slid_ing).perform()
                    except:
                        break
        except NoSuchElementException as e:
            print(e)
        time.sleep(10)
        browser.find_element_by_css_selector('.Qxyfvg.fydGNC').click()
        time.sleep(2)
        # 再次点击保存到网盘
        browser.find_element_by_css_selector('.g-button.g-button-blue').click()
        time.sleep(2)
        # 选择需要保存的文件夹的xpath，这里根据需要改动
        browser.find_element_by_xpath('//*[@id="fileTreeDialog"]/div[2]/div/ul/li/ul/li[4]/div/span').click()
        time.sleep(2)
        browser.find_element_by_css_selector('.icon.icon-newfolder').click()
        time.sleep(3)
        browser.find_element_by_css_selector('.input.shareFolderInput').clear()
        browser.find_element_by_css_selector('.input.shareFolderInput').send_keys(source_filename)
        browser.find_element_by_css_selector('.input.shareFolderInput').send_keys(Keys.ENTER)
        time.sleep(2)
        browser.find_element_by_css_selector('.treeview-node.treenode-empty.treeview-node-on').click()
        browser.find_element_by_xpath('//*[@id="fileTreeDialog"]/div[3]/a[2]').click()
        time.sleep(30)
        browser.close()

    def pan_save(self):
        """
        因有的资源网站也缺失所以总条数少于2059，共1944
        2020-01-22 20：59  续点 第1021条资源未完成
        """
        for i in range(0, len(self.row_lists)):
            # print(source)
            if 'pan.baidu.com' in self.row_lists[i]['pan_real_url']:
                print('第' + str(i + 1) + '条资源')
                source_filename = self.row_lists[i]['name'] + '-' + self.row_lists[i]['detail_url'][-8:] + ' ' + self.row_lists[i]['pan_title']
                pan_url = self.row_lists[i]['pan_real_url']
                pan_pwd = self.row_lists[i]['pan_psw']
                print(source_filename, pan_url, pan_pwd)
                if 'share' in pan_url:
                    # 代码发送创建文件夹的请求以及转存的请求
                    status = self.enter_pwd(source_filename, pan_url, pan_pwd)
                    # 用selenium自动保存
                    # self.s_enter_pwd(source_filename, pan_url, pan_pwd)
                if '/s/' in pan_url:
                    main_data = {'source_filename': source_filename, 'pan_url': pan_url}
                    status = self.transfer_save(main_data)
            else:
                # print('quqi：' + source)
                pass
            # break

    def select_pan_url(self):
        db = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='')
        cursor = db.cursor(cursor=pymysql.cursors.SSDictCursor)

        select_sql = "select `name`, `detail_url`, `pan_title`, `pan_psw`, `pan_real_url` from agepan_wj"
        try:
            cursor.execute(select_sql)
            # 在处理大量数据时可以分割进行
            datas = cursor.fetchall()
            for pan in datas:
                self.row_lists.append(pan)
        except Exception as e:
            print('取数据失败', e)
            db.rollback()
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def update_status(pan_real_url):
        db = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='')
        cursor = db.cursor()

        update_sql = "update agepan_wj set `status`=0 where `pan_real_url`='%s'" % pan_real_url
        try:
            cursor.execute(update_sql)
            db.commit()
            print('更新状态成功')
        except Exception as e:
            print('更新状态失败', e)
            db.rollback()
        finally:
            cursor.close()
            db.close()


if __name__ == '__main__':
    autosave = AutoSave()
    autosave.select_pan_url()
    autosave.pan_save()
