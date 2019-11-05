# SpiderBar

高质量爬虫案例聚集，仅供测试，学习，切勿暴力索取!!!

每个文件夹都包含一个爬虫以及一个**raedme**文件

爬虫文件代码顶端加上
```angular2html
# author:xxx 19-9-22
```

## 目录

## [Ximalaya](https://github.com/joelYing/SpiderBar/tree/master/Ximalaya) 

喜马拉雅免费音频下载

运行后输入音频对应的ID即可批量下载

## [KoKoJia](https://github.com/joelYing/SpiderBar/tree/master/KoKoJia) 

代码用于下载已购买的课课家视频教程

请注意，前提是已经购买该课程

1、首先找到课程首页链接，如[http://www.kokojia.com/course-3643.html](http://www.kokojia.com/course-3643.html)  
2、点击课程中任意视频，打开开发者工具，刷新页面，获取类似如下的cookie，可以直接把整个cookie复制，填入代码中
```
Hm_lvt_f530f7624f8a05758b78e413af3d70ca=1572921480; ****** Hm_lpvt_69a9e7b64ab4ee86e58df7fde25d232a=1572922143; issldd=y
```
3、在代码中修改将要保存下载内容的路径
```python
self.path1 = 'D:\\Python\\PycharmProject\\KoKoJia'
self.path2 = 'D:\\Python\\PycharmProject\\FinalKoKoJia'
```
4、运行程序，输入`course-3643`即可

## [TaoBaoEdu](https://github.com/joelYing/SpiderBar/tree/master/TaoBaoEdu) 

代码用于下载已购买的淘宝教育视频教程

请注意，前提是已经购买该课程

1、首先找到课程首页链接，如[http://v.xue.taobao.com/learn.htm?courseId=102063](http://v.xue.taobao.com/learn.htm?courseId=102063)  
2、点击课程中任意视频，打开开发者工具，刷新页面，获取课程首页连接的类似如下的cookie，可以直接把整个cookie复制，填入代码中
```
miid=1160271546849586574; cna=I******HIcbgIaCaPg3cIsW27ThGSPsEHUbmJ-agH
```
3、在代码中修改将要保存下载内容的路径
```python
self.path1 = 'D:\\Python\\PycharmProject\\TaoBaoEdu'
self.path2 = 'D:\\Python\\PycharmProject\\FinalTaoBaoEdu'
```
4、运行程序，输入课程id也就是输入102063，即可

### cniao5  

```
Python爬取菜鸟窝教程视频脚本  
包含爬取脚本以及批量文件重命名脚本
```


### cniao5  

```
Python爬取菜鸟窝教程视频脚本  
包含爬取脚本以及批量文件重命名脚本
```

### electronic_business_site  

```
Python爬取各电商网站实战记录  
爬取京东华为旗舰店手机数据，包含折扣价、价格、评论数等，下同  
爬取京东单反数据  
爬取苏宁华为手机数据  
爬取天猫华为手机数据， 还包含销量  
以及 request headers 处理工具
```

### utils  

```
大量 user-agent 以及 headerstool  
```

### wechat  

```
Python爬取微信公众号永久链接  
```

### YuanTong_tousu  

```
爬取圆通投诉信息（利用正则+xpath）  
```

### twitter_user  

```
Twitter用户tweet采集，需要翻墙（ss）  
```

### taobaoedu

```
Python3 爬取淘宝教育指定课程视频，前提是该视频免费，或已购买
```

### youzheng

```
国家邮政局申诉网站-案例选登（18年投诉信息）
```
