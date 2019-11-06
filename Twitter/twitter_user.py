#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:joel 19-11-6


import re
import pymysql
import requests


class Weibo(object):
    def __init__(self):
        self.search_url = 'https://twitter.com/search?f=users&q={}&src=typd&lang=en'
        self.info_url = 'https://twitter.com/{}'
        # self.next_page = 'https://twitter.com/i/profiles/show/{}/timeline/' \
        #                  'tweets?composed_count=0&include_available_features=1' \
        #                  '&include_entities=1&include_new_items_bar=true&interval=30000' \
        #                  '&latent_count=0&max_position={}'
        self.next_page = 'https://twitter.com/i/profiles/show/{}/timeline/tweets?' \
                         'include_available_features=1&include_entities=1&max_position={}&' \
                         'reset_error_state=false '
        self.proxies = {"http": "http://localhost:1080", "https": "http://localhost:1080"}

    @staticmethod
    def tag_tool(text):
        text = re.sub(r'<.*?>|&rlm;|&nbsp;|"  "|\n|\t|\r', '', text)
        text = re.sub(r'Verified account', ' ', text)
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
        uid, name, verifys, description, location, tweets, following, followers, last_content_id = '', '', '', '', '',\
                                                                                                   '', '', '', '',
        for i in range(1, 3):
            print(i)
            if i == 1:
                r = s.get(self.info_url.format(kw), proxies=self.proxies)
                # print(r.text)
                uid, name, verifys, description, location, tweets, following, followers, last_content_id = self.gethtml(r)
                self.gettweets(r.text, uid, name, verifys, description, location, tweets, following, followers)
            else:
                r = s.get(self.next_page.format(kw, last_content_id), proxies=self.proxies)
                text = self.js_tool(r.text)
                self.gettweets(text, uid, name, verifys, description, location, tweets, following, followers)

    def gethtml(self, r):
        card_infos = re.findall(r'<div class="ProfileHeaderCard">(.*?)<div class="PhotoRail">', r.text, re.S)
        tffl_infos = re.findall(r'<div class="Grid-cell u-size2of3 u-lg-size3of4">\s*?<div '
                                r'class="ProfileCanopy-nav">(.*?)</div>', r.text, re.S)
        verifys, description, location, tweets, following, followers = '', '', '', '', '', ''
        name = re.findall(r'<h1 class="ProfileHeaderCard-name">.*?<a href="/(.*?)".*?>', card_infos[0], re.S)[0]
        verified = re.findall(r'<span class="Icon Icon--verified"><span '
                              r'class="u-hiddenVisually">(.*?)</span></span>', card_infos[0], re.S)
        if verified:
            verifys = verified[0]
        bio = re.findall(r'<p class="ProfileHeaderCard-bio u-dir" dir="ltr">(.*?)</p>', card_infos[0], re.S)
        if bio:
            description = self.tag_tool(bio[0])
        location_text = re.findall(r'<span class="ProfileHeaderCard-locationText u-dir" dir="ltr">(.*?)</span>',
                                   card_infos[0], re.S)
        if location_text:
            location = self.space_tool(location_text[0])

        uid = re.findall(r'<div class="ProfileNav" role="navigation" data-user-id="(.*?)">', tffl_infos[0], re.S)[0]
        t = re.findall(r'<li class="ProfileNav-item ProfileNav-item--tweets is-active".*?<span '
                       r'class="ProfileNav-value"\s*?data-count=(.*?) data-is-compact=".*?">', tffl_infos[0], re.S)
        if t:
            tweets = t[0]
        fing = re.findall(r'<li class="ProfileNav-item ProfileNav-item--following">.*?<span '
                          r'class="ProfileNav-value" data-count=(.*?) data-is-compact=".*?">', tffl_infos[0], re.S)
        if fing:
            following = fing[0]
        fers = re.findall(r'<li class="ProfileNav-item ProfileNav-item--followers">.*?<span '
                          r'class="ProfileNav-value" data-count=(.*?) data-is-compact=".*?">', tffl_infos[0], re.S)
        if fing:
            followers = fers[0]
        content_ids = re.findall(r'<li class="js-stream-item stream-item stream-item.*?>.*?'
                                 r'data-tweet-id="(.*?)".*?<div class="stream-item-header">', r.text, re.S)
        last_content_id = content_ids[len(content_ids) - 1]
        return uid, name, verifys, description, location, tweets, following, followers, last_content_id

    def gettweets(self, text, uid, name, verifys, description, location, tweets, following, followers):
        user_tweets = re.findall(r'li class="js-stream-item stream-item stream-item.*?>.*?'
                                 r'data-tweet-id="(.*?)".*?<div class="stream-item-header">(.*?)<small class="time">'
                                 r'.*?<a.*?class="tweet-timestamp js-permalink js-nav js-tooltip".*?title="(.*?)".*?>'
                                 r'.*?<p class="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text"'
                                 r'.*?>(.*?)</p>.*?<div class="stream-item-footer">(.*?)<div class="dismiss-module">'
                                 r'.*?</li>', text, re.S)
        for user_tweet in user_tweets:
            content_id = user_tweet[0]
            source = self.space_tool(user_tweet[1])
            pub_time = user_tweet[2]
            content = self.tag_tool(user_tweet[3])
            nums = re.findall(r'<span class="ProfileTweet-actionCount".*?data-tweet-stat-count="(.*?)">',
                              user_tweet[4], re.S)
            replies, retweets, likes = nums[0], nums[1], nums[2]
            # print(uid, name, verifys, description, location, tweets, following, followers,
            #         content_id, source, pub_time, content, replies, retweets, likes)
            self.insertmysql(uid, name, verifys, description, location, tweets, following, followers,
                                content_id, source, pub_time, content, replies, retweets, likes)

    @staticmethod
    def insertmysql(uid, name, verifys, description, location, tweets, following, followers,
                    content_id, source, pub_time, content, replies, retweets, likes):
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='twitter')
        cursor = conn.cursor()

        insert_sql = "insert into `twitter_user_tweet` (`uid`, `name`, `veritys`, `description`, `location`, `tweets`" \
                     ", `following`, `followers`,`content_id`, `source`, `content`, `replies`, `retweets`, " \
                     "`likes`, `pub_time`)values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'," \
                     "'%s','%s')" % (uid, name, verifys, description, location, tweets, following, followers, content_id,
                                     source, content, replies, retweets, likes, pub_time)
        # select_sql = "select `content_id` from `twitter_user` where `content_id`='%s'" % content_id

        try:
            # response = cursor.execute(select_sql)
            # conn.commit()
            # if response == 1:
            #     print(u'该tweet存在...')
            # else:
            #     try:
            # print(insert_sql)
            cursor.execute(insert_sql)
            conn.commit()
            print(u'tweet插入成功...')
        except Exception as e:
            print(u'tweet插入错误...', e)
            conn.rollback()
        # except Exception as e:
        #     print(u'查询错误...', e)
        #     conn.rollback()
        finally:
            cursor.close()
            conn.close()


if __name__ == '__main__':
    wb = Weibo()
    wb.nextpage('jfla')
