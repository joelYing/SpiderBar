#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:joel
# time:2018/10/24 10:28

# twitter 通过搜索接口的tweet需要添加 user-agent

import re
import time

import pymysql
import requests

"""
搜索接口1：
'https://twitter.com/i/profiles/show/{}/timeline/tweets?q=%23{}&composed_count=0&include_available_features=1&
include_entities=1&include_new_items_bar=true&interval=30000&latent_count=0&max_position={}'


搜索接口2: 根据时间段来搜索，需要参数：关键词，max_position（该页第二十个tweet的id），每一页数量
'https://twitter.com/i/search/timeline?vertical=default&q=%23Beijing2022&since=2015-01-01&until=2018-11-23&l=en&
src=typd&include_available_features=1&include_entities=1&max_position=1064878625680351232&reset_error_state=false'

测试结果：Twitter第二页的max_position参数可以在第一页的data-max-position中找到（data-min-position 也在），且fiddle抓包结果，
翻第二页时带上的max_position参数的值就是data-max-position,问题带上参数后发起请求可能少了某个参数导致返回没有对应的数据
"""


class Weibo(object):
    def __init__(self):
        """
        关键字搜索url
        'https://twitter.com/search?l=ja&q=%E7%86%8A%E6%9C%AC%E5%9F%8Esince%3A2016-04-01%20until%3A2017-11-01&src=typd
        """
        self.search_url = 'https://twitter.com/search?l=en&q=%23{}since%3A2016-04-01until%3A2018-11-01&src=typd'
        self.next_page = 'https://twitter.com/i/search/timeline?vertical=default&q=%23{}since%3A2016-04-01' \
                         'until%3A2018-11-01&l=en&src=typd&include_available_features=1&include_entities=1&' \
                         'max_position={}&reset_error_state=false'
        self.proxies = {"http": "http://localhost:1080", "https": "http://localhost:1080", }
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.102 Safari/537.36',
            }
        self.maxposition = ''

    @staticmethod
    def tag_tool(text):
        text = re.sub(r'<.*?>|&rlm;|&nbsp;|"  "|\n|\t|\r', '', text)
        text = re.sub(r'Verified account', ' ',text)
        return text

    @staticmethod
    def space_tool(text):
        text = re.sub(r'<.*?>|&rlm;|&nbsp;|"  "|\n|\t|\r|\s|&amp;', '', text)
        text = re.sub(r'Verified account|Verifiedaccount', ' ', text)
        return text

    @staticmethod
    def js_tool(text):
        text = re.sub(r'\\u003c', '<', text)
        text = re.sub(r'\\u003e', '>', text)
        text = re.sub(r'\\n', '', text)
        text = re.sub(r'\\', '', text)
        return text

    def nextpage(self, kw):
        s = requests.session()
        user_id, name, verify, descript, locate, tweets, following, followers, last_content_id = '', '', '', '', '', \
                                                                                                 '', '', '', '',
        for i in range(1, 4):
            print(i)
            if i == 1:
                r = s.get(self.search_url.format(kw), proxies=self.proxies, headers=self.headers)
                # print(r.text)
                self.gettweets(r.text)
                time.sleep(2)
            else:
                r = s.get(self.next_page.format(kw, self.maxposition), proxies=self.proxies, headers=self.headers)
                text = self.js_tool(r.text)
                # print(text)
                self.gettweets(text)
                time.sleep(2)
                # break

    def gettweets(self, text):
        user_tweets = re.findall(r'li class="js-stream-item stream-item stream-item.*?>.*?'
                                 r'data-tweet-id="(.*?)".*?<div class="stream-item-header">(.*?)<small class="time">'
                                 r'.*?<a.*?class="tweet-timestamp js-permalink js-nav js-tooltip".*?title="(.*?)".*?>'
                                 r'.*?<p class="TweetTextSize.*?".*?>(.*?)</p>'
                                 r'.*?<div class="stream-item-footer">(.*?)</div>.*?</li>', text, re.S)
        first_maxposition = re.findall(r'data-max-position="(.*?)"', text, re.S)
        if first_maxposition:
            self.maxposition = first_maxposition[0]
            print(self.maxposition)
        min_position = re.findall(r'"min_position":"(.*?)",', text, re.S)
        if min_position:
            self.maxposition = min_position[0]
            print(self.maxposition)
        for user_tweet in user_tweets:
            # print(user_tweet)
            content_id = user_tweet[0]
            laiyuan = self.space_tool(user_tweet[1])
            user = laiyuan.split('@')[1].strip()
            createtime = user_tweet[2]
            content = self.tag_tool(user_tweet[3])
            nums = re.findall(r'<span class="ProfileTweet-actionCount".*?data-tweet-stat-count="(.*?)">',
                              user_tweet[4], re.S)
            replies, retweets, likes = nums[0], nums[1], nums[2]
            # print(content_id, laiyuan)
            link = 'https://twitter.com/{}/status/{}'.format(user, content_id)
            print(content_id, laiyuan, link, createtime, content, replies, retweets, likes)
            # self.insertmysql(content_id, laiyuan, link, createtime, content, replies, retweets, likes)
            # break

    @staticmethod
    def insertmysql(content_id, laiyuan, link, createtime, content, replies, retweets, likes):
        conn = pymysql.connect(host='192.168.101.160', port=3306, user='suosi', passwd='Mysql123.com', db='spider')
        cursor = conn.cursor()

        insert_sql = "insert into `twitter_2022` (`content_id`, `source`, `link`, `content`, `replies`, `retweets`, " \
                     "`likes`, `time`)values('%s','%s','%s','%s','%s','%s','%s','%s')" % \
                     (content_id, laiyuan, link, content, replies, retweets, likes, createtime)
        # select_sql = "select `content_id` from `twitter_user` where `content_id`='%s'" % content_id

        try:
            cursor.execute(insert_sql)
            conn.commit()
            print(u'tweet插入成功...')
        except Exception as e:
            print(u'tweet插入错误...', e)
            conn.rollback()
        finally:
            cursor.close()
            conn.close()


if __name__ == '__main__':
    wb = Weibo()
    wb.nextpage(u"Beijing2022")
