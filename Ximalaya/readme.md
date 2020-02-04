## 再更新

<p id="div-border-left-red">2020-02-02</p>

完成VIP音频下载功能

使用方法：

* 首先你已经开通了喜马会员
* 该音频属于会员或者付费可听
* 运行程序，选择`VIP`选项，然后输入音频集的albumID，以及你的token，点击运行即可

token在下图这里复制

![](http://image.joelyings.com/2020-02-02_1.png)

就是`1&_token=xxx`，这一部分，不用加`;`

### 探索过程

这次为了《雪中》付费的下半部，我再次尝试下载音频，通过一个活动领取了15天的免费喜马VIP

然后打开下半部的[页面](https://www.ximalaya.com/youshengshu/5130435/)

这里只有前三个音频是`试听`的，也就是说前三个是我们可以在不开通VIP的情况下也可以下载的，但是后面的就不行，幸好现在开了VIP都可以收听

对`第861回`这个收费音频来分析，页面加载完成后，打开`fiddler`抓包，观察点击播放按钮后抓到的数据包

我们可以发现两个链接：

```
# 链接一
https://mpay.ximalaya.com/mobile/track/pay/20641515?device=pc&isBackend=true&_=1580528471441

# 返回的response
ret: 0,
msg: "0",
trackId: 20641515,
uid: 2342717,
albumId: 5130435,
title: "雪中悍刀行 - 861",
domain: "http://audiopay.cos.xmcdn.com",
totalLength: 10533707,
sampleDuration: 0,
sampleLength: 0,
isAuthorized: true,
apiVersion: "1.0.0",
seed: 8644,
fileId: "6*33*22*66*59*29*62*11*31*3*62*67*47*62*31*29*62*54*21*6*63*11*52*48*50*52*41*38*1*23*33*51*30*28*21*45*43*51*54*1*48*66*6*22*34*3*34*15*5*3*46*",
buyKey: "617574686f72697a6564",
duration: 1301,
ep: "20NvOoh6T39X3qwKO4cY5g5bVhg+hSXHRYUYeFznDiuuzOiKiKrbmelc2/zZg6UxDO9x2nIYeKZm0+z+xg0V3r0aPyxS",
highestQualityLevel: 1,
downloadQualityLevel: 1,
authorizedType: 1
```

```
# 链接二 没有返回，这就是音频的真实播放地址

http://audiopay.cos.xmcdn.com/download/1.0.0/group1/M04/DF/01/wKgJMlvblh6xqrSXAKC7Swxvugo848.m4a?sign=a464311c1753bfdf581ac9560dc8bf9a&buy_key=617574686f72697a6564&token=5400&timestamp=1580528473&duration=1301
```

链接二携带的参数

| 参数 | 值 | 状态 |
|--|--|--|
|sign|a464311c1753bfdf581ac9560dc8bf9a|变化|
|buy_key|617574686f72697a6564|固定|
|token|5400|变化|
|timestamp|1580528473|时间戳|
|duration|1301|每个音频特有|

链接二的`M04/DF/01/wKgJMlvblh6xqrSXAKC7Swxvugo848`也是变化的

问题就在于链接一我们很好理解，带上音频的ID就可以返回一串response，再通过JS生成链接二得到音频真实地址

关键在于这个JS比较麻烦，JS片段：

``` javascript
var gt = vt("xm", "Ä[ÜJ=Û3Áf÷N")
  , bt = [19, 1, 4, 7, 30, 14, 28, 8, 24, 17, 6, 35, 34, 16, 9, 10, 13, 22, 32, 29, 31, 21, 18, 3, 2, 23, 25, 27, 11, 20, 5, 15, 12, 0, 33, 26]
  , wt = function(t) {
    var e = vt(function(t, e) {
        for (var n = [], r = 0; r < t.length; r++) {
            for (var o = "a" <= t[r] && "z" >= t[r] ? t[r].charCodeAt() - 97 : t[r].charCodeAt() - "0".charCodeAt() + 26, i = 0; 36 > i; i++)
                if (e[i] == o) {
                    o = i;
                    break
                }
            n[r] = 25 < o ? String.fromCharCode(o - 26 + "0".charCodeAt()) : String.fromCharCode(o + 97)
        }
        return n.join("")
    }("d" + gt + "9", bt), function(t) {
        if (!t)
            return "";
        var e, n, r, o, i, a = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 62, -1, -1, -1, 63, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, -1, -1, -1, -1, -1, -1, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, -1, -1, -1, -1, -1, -1, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, -1, -1, -1, -1, -1];
        for (o = (t = t.toString()).length,
        r = 0,
        i = ""; r < o; ) {
            do {
                e = a[255 & t.charCodeAt(r++)]
            } while (r < o && -1 == e);if (-1 == e)
                break;
            do {
                n = a[255 & t.charCodeAt(r++)]
            } while (r < o && -1 == n);if (-1 == n)
                break;
            i += String.fromCharCode(e << 2 | (48 & n) >> 4);
            do {
                if (61 == (e = 255 & t.charCodeAt(r++)))
                    return i;
                e = a[e]
            } while (r < o && -1 == e);if (-1 == e)
                break;
            i += String.fromCharCode((15 & n) << 4 | (60 & e) >> 2);
            do {
                if (61 == (n = 255 & t.charCodeAt(r++)))
                    return i;
                n = a[n]
            } while (r < o && -1 == n);if (-1 == n)
                break;
            i += String.fromCharCode((3 & e) << 6 | n)
        }
        return i
    }(t)).split("-")
      , n = tt(e, 4)
      , r = n[0];
    return {
        sign: n[1],
        buy_key: r,
        token: n[2],
        timestamp: n[3]
    }
}
```

还有加密的字符`var gt = vt("xm", "Ä[ÜJ=Û3Áf÷N")`，全部代码在[这里](http://image.joelyings.com/b20b549ee.js)

有能力的各位可以试着解决一下哈哈~

鉴于本人JS能力不够便放弃了这种方法，但是又想到`只要获取这个链接二就可以下载音频`，那么我能不能`直接拿到这个链接`而不是通过JS生成一系列相关的参数去构造

随后我就想到了抓包，我们通过fiddler可以抓到这个链接，那么，Python有没有类似的第三方库呢？

答案是有的，`Scapy`，对，`不是Scrapy`，Scapy具有模拟发送数据包、监听解析数据包、互联网协议解析、数据挖掘等多种用处

然后发现scapy-http这个模块，二者配合使用后，可以解析抓到的包的url等参数

### 安装工具
``` bash
pip3 install scapy

pip3 install scapy-http
```

还要安装winpcap软件，为监控网卡提供接口，[下载地址](https://www.winpcap.org/install/default.htm)

[iface 参数为你要监听的网卡的名称，参考这里](https://blog.csdn.net/luanpeng825485697/article/details/78379154)

``` python
# 核心代码，因为观察到链接二，这个音频真实链接的发送IP是变化的，但是端口是固定的80
# count=5，表示抓取5个端口为80且属于TCP的报文
# 在对应的音频详情播放页，运行程序后，点击播放按钮，然后就可以抓到，注意顺序不能乱

pkts = sniff(filter="tcp and port 80", iface="Qualcomm Atheros AR956x Wireless Network Adapter", count=5)
print('抓包成功,开始解析', pkts)
for pkt in pkts:
    # 判断是否有HTTPRequest
    if TCP in pkt and pkt.haslayer(http.HTTPRequest):
        # print(pkt.show())
        http_header = pkt[http.HTTPRequest].fields
        req_url = 'http://' + bytes.decode(http_header['Host']) + bytes.decode(http_header['Path'])
        # print(req_url)
        return req_url
```

```
# ptk.show()的内容示例

###[ Ethernet ]### 
  ...
  type      = IPv4
###[ IP ]### 
     ...
     \options   \
###[ TCP ]### 
        ...
        options   = []
###[ HTTP ]### 
###[ HTTP Request ]### 
      Method    = 'GET'
      Path      = '/download/1.0.0/group1/M02/DE/F7/wKgJMlvbkluA76b0AKfFEVJys4k253.m4a?sign=68fbb62e424b3af077c30a9a2d4e8bad&buy_key=617574686f72697a6564&token=4060&timestamp=1580616979&duration=1358'
      Http-Version= 'HTTP/1.1'
      Host      = 'audiopay.cos.xmcdn.com'

      ...

      Headers   = 'Host: audiopay.cos.xmcdn.com\r\nConnection: keep-alive\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/79.0.3945.130 Safari/537.36\r\nAccept-Encoding: identity;q=1, *;q=0\r\nAccept: */*\r\nRange: bytes=0-'
      Additional-Headers= None

```

这样我们就可以通过抓包的方式直接拿到链接，但是要一个一个点播放按钮还是太耗人力，所辛我们还有`selenium`+`Chromedriver`

可以设置Chromedriver为headless模式

``` python
# 设置无头模式
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
browser = webdriver.Chrome(chrome_options=chrome_options)
# 访问音频播放页面，这是为了后面添加cookie指定添加的页面是哪一个
browser.get(url)
# 添加cookie
browser.add_cookie({
    'domain': '.ximalaya.com',  # 此处xxx.com前，需要带点
    'name': '1&_token',
    'value': 'xxx'
})
# 添加cookie后的再次访问
browser.get(url)
# 等待加载页面完全
time.sleep(4)
print('开始抓包')
# 点击播放按钮，这里的顺序不能搞错，换成先抓包再点击的话，试过，但是抓不到
browser.find_element_by_css_selector(".play-btn.fR_").click()
# 下面的iface是电脑网卡的名称 count是捕获报文的数目
pkts = sniff(filter="tcp and port 80", iface="Qualcomm Atheros AR956x Wireless Network Adapter", count=5)
print('抓包成功,开始解析', pkts)
# 退出browser，避免selenium报错
browser.quit()

...

```

这里就不多赘述，想使用的可以去我的[github](https://github.com/joelYing/XimalayaFM)下载

附：

selenium报错

``` 
ignored in: <bound method Popen.__del__ of <subprocess.Popen object at 0x043...
```

解决方法

```
driver.quit()
```

`pyqt5`生成`.py`文件

``` bash
pyuic5 -o xmd_ui.py ximadownloader.ui
```

## 更新

* 2019-10-12 19:10

[CSDN](https://blog.csdn.net/weixin_42050513/article/details/101224552)上有人评论说`xm-sign`规则改了，于是去看了看，发现实际只改了一个字母，整体流程任可以看下方正文

把`hashlib.md5("ximalaya-{}".format(servertime).encode()`中的`ximalaya`替换成`himalaya`即可

改动点如下图

![](http://image.joelyings.com/20191012-1.png)

![](http://image.joelyings.com/20191012-2.png)

改动不大，可能是发现了有人在大量爬取，先小地方改动，随后可能会有较大的规则改动，教程写出来的目的是学习、测试，切勿过度爬取！


## 前言

应该也有一年了吧，之前也在[简书](https://www.jianshu.com/p/f533ffb85e70)，[CSDN](https://blog.csdn.net/weixin_42050513/article/details/80771860)上写过爬取喜马拉雅音频的文章，经历了一次喜马拉雅的改版，同时也更新了一波代码

最近为了喜欢的`雪中悍刀行`，回去重新打算跑一下代码下载音频，这一跑不要紧，结果就发现喜马拉雅又改版了

得，又得重新写代码，且这次还加了JS反爬的手段，让我也好好学习了一把，嗯，下面进入正题

## 分析

### 初步分析

老样子，首先来看看我们要爬取的目标`https://www.ximalaya.com/youshengshu/2684034/`

![](http://image.joelyings.com/20190923-1.png)

![](http://image.joelyings.com/20190923-2.png)

像这样的882个音频，共计30页，每页一般标准的有30个，最后要将这882个音频保存到本地，那么我们最需要的是找到音频的源播放地址，我们不妨打开一个音频来看看，同时按F12打开开发者工具

首先我看了看`https://www.ximalaya.com/youshengshu/2684034/2725352`的网页源代码中，并没有相关的播放地址，所以我开始在开发者工具中找

![](http://image.joelyings.com/20190923-3.png)

页面刷新完之后的XHR中我没有找到明显的播放地址，然后我点了一下页面的播放按钮，之后XHR又跳出来好几条信息，随后我找到了

![](http://image.joelyings.com/20190923-4.png)

可以看到，`src`对应的`m4a`链接就是音频的源播放地址，我们只要拿到这个链接就行了

![](http://image.joelyings.com/20190923-5.png)

那么我们接下来就应该要访问上面这个链接，从而拿到音频的播放地址，但是当我们复制链接后去打开时会发现

![](http://image.joelyings.com/20190923-6.png)

`[SIGN] no sign or wrong sign`，是的，你很大几率会看到这个，没有sign或错误的sign，那么也就是说这个链接是打不开的？那么带上请求头试试？后来我用postman访问这个链接，带上请求头后还是没有得到结果，然后想了想，返回给我们的提示是`sign`

正好请求头中就有这个`xm-sign`，于是我重新试了一下，只带上这个`xm-sign`去访问，发现在一次尝试中拿到了之前看到的带有播放链接的`response`

```
xm-sign: dcf3736db17584cb0b7260c1fcb1f05f(45)1569231095030(64)1569231094006
```

那么下一步要解决的就是如何获得这个`xm-sign`

### 进阶分析

`xm-sign`并不在XHR中能够找到，所以我下一步的目标是在JS文件中找

![](http://image.joelyings.com/20190923-7.png)

找啊找，终于在上面的js文件中，找到了点头绪，出现了同样的`xm-sign`，这个过程对我来说是比较漫长的，因为需要在js文件中一个个的浏览过去，当然你通过fiddler抓包去找也是差不多的

然后为了明确知道`xm-sign`是怎么来的，我们就需要对这个js文件进行打断点调试，在控制台的`Source`中打开该Js文件

![](http://image.joelyings.com/20190923-8.png)

右键该JS文件，点击`Open in Sources panel`，或者鼠标轻放在该文件上，会出现该文件的路径，到控制台`Source`中找到它

![](http://image.joelyings.com/20190923-9.png)

找到该文件后点击打开，然后点击下方的`花括号`按钮，美化代码，再按`ctrl + f`搜索`xm-sign`，就可以定位到`xm-sign`

![](http://image.joelyings.com/20190923-10.png)

我们需要知道对应`xm-sign`的值`t`到底是怎么样的，接着在`return e`上打上断点，这样一来，当页面刷新运行到这里的时候会自动停止之后的JS代码，可以让我们来进行调试，如何通过Chrome调试可以参考[这篇文章](https://www.jianshu.com/p/1ca8db74c526)

打好断点后，刷新页面，等待一会，不用动别的，然后就可以看到下图

![](http://image.joelyings.com/20190923-11.png)

图中所示的`xm-sign`的值就是`t`的值，再往上一点，`t`的值就是由`o.default`产生的

```javascript
n.interceptors.request.use(function(e) {
        if (e.url.indexOf("/revision") > -1) {
            var t = (0,
            o.default)();  //  然后点击 o.default 进入该方法中 
            e.headers = function(e) {
                for (var t = 1; t < arguments.length; t++) {
                    var r = null != arguments[t] ? arguments[t] : {};
                    t % 2 ? i(r, !0).forEach(function(t) {
                        u(e, t, r[t])
                    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r)) : i(r).forEach(function(t) {
                        Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(r, t))
                    })
                }
                return e
            }({}, e.headers, {
                "xm-sign": t
            })
        }
        return e
    });
```

接着我们点击`o.default`这个方法，进去看看这一串值到底如何生成，鼠标放在`o.default`上，点击出现的`anonymous`方法

![](http://image.joelyings.com/20190923-12.png)

我们就自动跳转到了下一个JS文件，同样格式化后我们就看到了下图所示的`function`部分

![](http://image.joelyings.com/20190923-13.png)

```javascript
function() {
    return function(t) {
        var e = Date.now();  // 当前时间戳
        return ("{ximalaya-" + t + "}(" + Le(100) + ")" + t + "(" + Le(100) + ")" + e).replace(/{([\w-]+)}/, function(t, e) {
            return Ue(e)
        })
    }(Ne() ? Date.now() : window.XM_SERVER_CLOCK || 0)
}
```

这个方法最终返回的就是我们的`xm-sign`的值，而`return`部分就是

```javascript
("{ximalaya-" + t + "}(" + Le(100) + ")" + t + "(" + Le(100) + ")" + e).replace(/{([\w-]+)}/, function(t, e) {return Ue(e)}
```

取消之前的断点，我们可以在下图中再打断点，再刷新页面，等待，调试

![](http://image.joelyings.com/20190923-14.png)

可以看到

![](http://image.joelyings.com/20190923-15.png)

这里面`t`就是时间戳，这个我们可以在前面的找到对应的服务器时间戳，请求这个即可`https://www.ximalaya.com/revision/time`

`Le(100)`是上面的一个函数，能生产100以内的随机数，如下，`e`就是当前的时间戳

```javascript
function Le(t) {
    return ~~(Math.random() * t)  
    // ~~ 代表双非按位取反运算符，对于正数，它向下取整；对于负数，向上取整；非数字取值为0
}
```

`replace(/{([\w-]+)}/, function(t, e) {return Ue(e)}`，replace就是把`{ximalaya-" + t + "}`部分替换成`Ue(e)`的值

我们接着看`Ue()`，同样鼠标放在`Ue`上，点击出现的`anonymous(t, n)`方法

![](http://image.joelyings.com/20190923-16.png)

```
 t.exports = function(t, n) {
                if (null == t)
                    throw new Error("Illegal argument " + t);
                var r = e.wordsToBytes(i(t, n));
                // 以下就是返回的值
                return n && n.asBytes ? r : n && n.asString ? o.bytesToString(r) : e.bytesToHex(r)
            }
```

我们在这里也可以打个断点看看返回的是什么，并且右键编辑断点时要打印的数据，我在这里就设置在控制台打印当前返回的内容

![](http://image.joelyings.com/20190923-17.png)

![](http://image.joelyings.com/20190923-18.png)

![](http://image.joelyings.com/20190923-19.png)

然后这个箭头就会变橙色，我们取消其他的断点，再次刷新页面，等待一会，调试

![](http://image.joelyings.com/20190923-20.png)

可以看到`t = "ximalaya-1569237828683", n = undefined`，并且控制台打印有`15de4b221c3cb112d4d8200ccf094a8e`这样的一串字符

![](http://image.joelyings.com/20190923-21.png)

根据经验猜测这可能是md5码，于是我们尝试使用在线转换工具，将`ximalaya-1569237828683`转换为MD5编码格式的内容，结果如下

![](http://image.joelyings.com/20190923-22.png)

结果正确，现在我们可以得出结论，参数`xm-sign`的值其实就是

<span id="inline-purple">MD5(ximalaya-服务器时间戳) + (100以内的随机数) + 服务器时间戳 + (100以内的随机数) + 现在的时间戳</span>

## 代码

解决了上面的JS反爬问题，我们来看看实际代码，这是主要的爬取起始部分

```python
# 传入专辑的ID，xm_fm_id
def get_fm(self, xm_fm_id):
    # 根据有声书ID构造url
    fm_url = self.base_url + '/youshengshu/{}'.format(xm_fm_id)
    print(fm_url)
    r_fm_url = self.s.get(fm_url, headers=self.header)
    # 获取书名
    fm_title = re.findall('<h1 class="title _leU">(.*?)</h1>', r_fm_url.text, re.S)[0]
    print('书名：' + fm_title)
    # 新建有声书ID的文件夹
    fm_path = self.make_dir(xm_fm_id)
    # 取最大页数
    max_page = re.findall(r'<input type="number" placeholder="请输入页码" step="1" min="1" '
                          r'max="(\d+)" class="control-input _bfuk" value=""/>', r_fm_url.text, re.S)
    if max_page and max_page[0]:
        for page in range(1, int(max_page[0]) + 1):
            print('第' + str(page) + '页')
            # 获取当前时间对应的 xm-sign 添加到请求头中
            self.get_sign()
            # 访问链接
            r = self.s.get(self.base_api.format(xm_fm_id, page), headers=self.header)
            # print(json.loads(r.text))
            r_json = json.loads(r.text)
            for audio in r_json['data']['tracksAudioPlay']:
            	# 获取json中的每个音频的标题以及播放源地址
                audio_title = str(audio['trackName']).replace(' ', '')
                audio_src = audio['src']
                # 交给下载的方法
                self.get_detail(audio_title, audio_src, fm_path)
            # 每爬取1页，30个音频，休眠3秒
            time.sleep(3)
    else:
        print(os.error)
```

这是构造`xm-sign`的方法，用到了Python的`hashlib`包

```python
def __init__(self):
    self.base_url = 'https://www.ximalaya.com'
    self.base_api = 'https://www.ximalaya.com/revision/play/album?albumId={}&pageNum={}&sort=0&pageSize=30'
    self.time_api = 'https://www.ximalaya.com/revision/time'
    self.header = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
    }
    self.s = requests.session()

def get_time(self):
    """
    获取服务器时间戳
    :return:
    """
    r = self.s.get(self.time_api, headers=self.header)
    return r.text

def get_sign(self):
    """
    获取sign： md5(ximalaya-服务器时间戳)(100以内随机数)服务器时间戳(100以内随机数)现在时间戳
    :return: xm_sign
    """
    nowtime = str(round(time.time() * 1000))
    # 得到服务器时间戳
    servertime = self.get_time()
    # 构造 xm-sign
    sign = str(hashlib.md5("ximalaya-{}".format(servertime).encode()).hexdigest()) + "({})".format(
        str(round(random.random() * 100))) + servertime + "({})".format(str(round(random.random() * 100))) + nowtime
    # 添加到请求头
    self.header["xm-sign"] = sign
    # print(sign)
    # return sign
```

这是保存音频的部分

```python
def get_detail(self, title, src, path):
	# 请求源地址的链接，得到response
    r_audio_src = self.s.get(src, headers=self.header)
    # 构造保存路径
    m4a_path = path + title + '.m4a'
    if not os.path.exists(m4a_path):
        with open(m4a_path, 'wb') as f:
        	# 写入
            f.write(r_audio_src.content)
            print(title + '保存完毕...')
    else:
        print(title + 'm4a已存在')
```

## 成果

![](http://image.joelyings.com/20190923-23.png)

## 后续

当然这只是喜马拉雅非付费的音频专辑，如果是付费后的专辑则需要另一套更加复杂的JS破解方法，我搞了半天，先拿手机抓包试了试，到最后发现还是得破解如何构造最后的下载地址

网上也有那种软件，这个就不多说了

需要代码的可以去我的GitHub，[传送门](https://github.com/joelYing/XimalayaFM/blob/master/ximalaya_search_new.py)

## 参考

[python模拟喜马拉雅js，全过程突破xm-sign，轻松爬取音频数据](https://blog.csdn.net/steadyhzc/article/details/99708520)  
[python爬取喜马拉雅音频，突破xm-sign校验反爬（爬虫）](https://blog.csdn.net/travel_Capsule/article/details/90312545)  
[爬虫之突破xm-sign校验反爬](http://www.likecs.com/show-65535.html)  
[喜马拉雅音频下载工具](https://github.com/smallmuou/xmlyfetcher)  
[Chrome 开发者工具代码行断点调试](https://www.jianshu.com/p/1ca8db74c526)  
[js中~~和 | 的妙用](http://www.fly63.com/article/detial/2802)