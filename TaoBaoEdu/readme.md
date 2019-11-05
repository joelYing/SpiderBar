## 淘宝教育已购视频下载

代码用于下载已购买的淘宝教育视频教程

## 前言

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

## 问题

核心与[爬取课课家视频](https://github.com/joelYing/SpiderBar/tree/master/KoKoJia)相同，但是不需要m3u8解密


