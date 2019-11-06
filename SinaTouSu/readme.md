## 新浪旗下黑猫投诉平台有关圆通速递投诉信息

爬取圆通速递投诉信息，保存于MySQL数据库

## 简介

1、平台链接：[https://tousu.sina.com.cn/](https://tousu.sina.com.cn/)  

2、修改数据库配置，建表
```python
conn = pymysql.connect(host='', port=3306, user='root', passwd='', db='yuantong_tousu')
```

```sql
CREATE TABLE `yt_ts` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(512) DEFAULT NULL COMMENT '投诉标题',
  `appeal` varchar(256) DEFAULT NULL COMMENT '申诉',
  `comment_id` varchar(128) DEFAULT NULL COMMENT '投诉ID',
  `create_time` varchar(128) DEFAULT NULL COMMENT '投诉时间',
  `status` varchar(128) DEFAULT NULL COMMENT '投诉状态',
  `url` varchar(256) DEFAULT NULL,
  `money` varchar(128) DEFAULT NULL,
  `detail_content` text,
  PRIMARY KEY (`id`),
  KEY `id` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;
```

3、运行程序，输入爬取页数即可即可

## 接口

base_url 在 https://tousu.sina.com.cn 黑猫投诉中搜索圆通，出现的就是针对圆通公司的投诉
```python
self.base_url = 'https://tousu.sina.com.cn/api/company/received_complaints?callback=jQuery111208122936695176131_1543212371581&couid=2146783270&type=1&page_size=10&page={}&_=1543212371582'
```
       
api_2 是一般所有的投诉
```python
self.api_2 = 'https://tousu.sina.com.cn/api/index/feed?callback=jQuery1112035396594072642396_1573025736517&type=1&page_size=10&page=1&_=1573025736518'
```



