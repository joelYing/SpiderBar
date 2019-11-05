## 课课家视频下载

代码用于下载已购买的课课家视频教程

## 前言

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
4、运行程序，输入course-3643即可

## 问题

1、Python os.system()出现乱码  
-- 该情况可能是由于pycharm编码设置导致的问题，在"File--Setting--FileEncodings--GlobalEncoding"中修改编码为GBK即可

2、TypeError: Object type class 'str' cannot be passed to C code  
-- https://blog.csdn.net/zhangpeterx/article/details/96351648  
-- https://www.cnblogs.com/huangjianting/p/8666446.html  

3、from Crypto.Cipher import AES  
-- https://www.cnblogs.com/zhangningyang/p/9117626.html

关于Crypto包，建议安装pycryptodome，然后在`C:\Python3\Lib\site-packages`中把crypto的小写c换成大写

## TODO
此部分关于m3u8文件解密的内容在后续补充

