# SpiderBar

[![](https://img.shields.io/badge/author-joel-orange)](https://github.com/joelYing)

高质量爬虫案例聚集，仅供测试，学习，切勿暴力索取!!!

少点套路，多点真诚，仍有不足，欢迎交流~~

每个文件夹都包含一个爬虫以及一个**raedme**文件

爬虫文件代码顶端加上author及日期
```
# author:xxx 19-9-22
```

## 目录

## [Ximalaya](https://github.com/joelYing/SpiderBar/tree/master/Ximalaya) 

喜马拉雅免费音频下载

运行后输入音频对应的ID即可批量下载

Tag：JS破解、音频下载

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

Tag：m3u8解密、视频下载

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

Tag：m3u8、视频下载

## [Cniao5](https://github.com/joelYing/SpiderBar/tree/master/Cniao5) 

代码用于下载菜鸟窝视频教程

1、首先找到课程首页链接，如[https://www.cniao5.com/course/lessons/10195](https://www.cniao5.com/course/lessons/10195)  
2、在代码中修改将要保存下载内容的路径
```python
self.file_path1 = 'D:\\Python\\PycharmProject\\Cniao5'
self.file_path2 = 'D:\\Python\\PycharmProject\\FinalCniao5'
```
4、运行程序，输入课程的ID即可，如输入：10195

Tag：区别下载、分析链接

## [SinaTouSu](https://github.com/joelYing/SpiderBar/tree/master/SinaTouSu) 

爬取新浪旗下黑猫投诉平台中，圆通速递投诉信息，保存于MySQL数据库

Tag：保存文字、MySQL、Unicode解析
