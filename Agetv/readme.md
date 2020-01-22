## 百度云盘资源自动转存

Python3实现百度云盘资源自动转存，解决带有密码的分享链接自动转存，不含密码的资源自动转存，同时实现post请求转存以及selenium转存

### 前言
最近看上了一个免费的动漫网站，资源一出更得巨快，而且有很多的网盘资源，于是想......

于是写了一段代码，爬取了网站的全部资源

![](http://image.joelyings.com/2020-01-20_1.png)

然后就该一个个的保存到我的云盘中了，问题是手动的话1900多个得累死人，所以就打算通过Python来做

一开始的想法是拿selenium来操作，但是又好奇有没有通过普通的爬虫思路来做这件事，于是下面把摸索的过程也加上了

### 分析&代码
![](http://image.joelyings.com/2020-01-20_2.png)

分析目标，通过从数据库取出的资源链接以及密码，构造并发送请求，然后可以进入资源的保存页面，再通过selenium来点击操作

首先网盘带密码的提取链接是这样的
[https://pan.baidu.com/share/init?surl=xxx](https://pan.baidu.com/share/init?surl=xxx)

而不需要密码可以直接提取资源的链接是这样的
[https://pan.baidu.com/s/1xxx](https://pan.baidu.com/s/1xxx)

跟输入密码后跳转的提取页面差不多，注意，以上两个xxx的内容一致，有个1是从web端访问的固有参数，后面会提到

我们在输入密码后就可以进去，那么关键就是提交密码的过程是怎样的，按照常理按f12打开开发者工具，在输入密码的页面输入密码后，点击``提取文件``

![](http://image.joelyings.com/2020-01-20_3.png)

这里有一定可能你会出现404找不到资源的页面，当然你可以用fiddler抓包就肯定可以抓到

我们找到关键的请求

![](http://image.joelyings.com/2020-01-20_4.png)

![](http://image.joelyings.com/2020-01-20_5.png)

![](http://image.joelyings.com/2020-01-20_6.png)

这个post请求在发送时带上了一系列的参数，以及密码

下面的就是跳转的资源页面，而这个是一个get请求，没有带上其他的参数，但是你单拿出来直接去访问的话（从没有输过密码的时候），会直接被跳转到输入密码的页面，那么问题来了，为什么会这样

![](http://image.joelyings.com/2020-01-20_7.png)

有经验的能比较准的猜测可能是这两个请求的cookie中有差异，因为逻辑上我输入密码后的post请求会返回一个参数，而这个参数既没有体现在第二个请求的url上，也没有可以携带的formdata，所以可能是在cookie中存在差异

事实证明两个请求的cookie确实有不同，关键在于 [https://pan.baidu.com/s/1xxx](https://pan.baidu.com/s/1xxx)
 的cookie中的`BDCLND`正好是 [https://pan.baidu.com/share/verify?surl=5RdjtVK55eEuayvz82cDmg&t=1579432835477&channel=chunlei&web=1&app_id=250528&bdstoken=08a7da93cf25d7935788a123e3e10c3d&logid=MTU3OTQzMjgzNTQ3OTAuNjM2MDg4OTgzOTY3MzU0OQ==&clienttype=0](https://pan.baidu.com/share/verify?surl=5RdjtVK55eEuayvz82cDmg&t=1579432835477&channel=chunlei&web=1&app_id=250528&bdstoken=08a7da93cf25d7935788a123e3e10c3d&logid=MTU3OTQzMjgzNTQ3OTAuNjM2MDg4OTgzOTY3MzU0OQ==&clienttype=0) 返回的参数中的一个值，如图：

![https://pan.baidu.com/s/1xxx](http://image.joelyings.com/2020-01-20_8.png)

![post请求的返回参数，f12工具可能看不到，fiddler抓包可以](http://image.joelyings.com/2020-01-20_9.png)

也就是说我们要取得这个参数后再访问 [https://pan.baidu.com/s/1xxx](https://pan.baidu.com/s/1xxx) 时带上这个cookie才可以不被返回到输入密码的页面

那接下来就是如何获取这个参数的问题，我长话短说

对比分析多个post链接可以知道，链接中
[https://pan.baidu.com/share/verify?surl=5RdjtVK55eEuayvz82cDmg&t=1579432835477&channel=chunlei&web=1&app_id=250528&bdstoken=08a7da93cf25d7935788a123e3e10c3d&logid=MTU3OTQzMjgzNTQ3OTAuNjM2MDg4OTgzOTY3MzU0OQ==&clienttype=0](https://pan.baidu.com/share/verify?surl=5RdjtVK55eEuayvz82cDmg&t=1579432835477&channel=chunlei&web=1&app_id=250528&bdstoken=08a7da93cf25d7935788a123e3e10c3d&logid=MTU3OTQzMjgzNTQ3OTAuNjM2MDg4OTgzOTY3MzU0OQ==&clienttype=0)

参数 | 值 |  状态  
-|-|-
surl	| 5RdjtVK55eEuayvz82cDmg | 相当于资源的ID，已知 |
t| 1579432835477 | 13位时间戳 |
channel | chunlei | 反正是固定的（春雷？） |
web | 1 | 固定，也就是前面提到过的
app_id | 250528 | 固定
bdstoken | 08a7da93cf25d7935788a123e3e10c3d | 固定
logid | MTU3OTQzMjgzNTQ3OTAuNjM2MDg4OTgzOTY3MzU0OQ== | 变化
clienttype | 0 | 固定

就只有`logid`是改变的，然后我找了找，应该是在js中产生的，最后在这里
![](http://image.joelyings.com/2020-01-20_10.png)

找到了这段js生成代码具体如下：
``` javascript
    var u = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/~！@#￥%……&"
      , l = String.fromCharCode
      , d = function(e) {
        if (e.length < 2) {
            var n = e.charCodeAt(0);
            return 128 > n ? e : 2048 > n ? l(192 | n >>> 6) + l(128 | 63 & n) : l(224 | n >>> 12 & 15) + l(128 | n >>> 6 & 63) + l(128 | 63 & n)
        }
        var n = 65536 + 1024 * (e.charCodeAt(0) - 55296) + (e.charCodeAt(1) - 56320);
        return l(240 | n >>> 18 & 7) + l(128 | n >>> 12 & 63) + l(128 | n >>> 6 & 63) + l(128 | 63 & n)
    }
      , f = /[\uD800-\uDBFF][\uDC00-\uDFFFF]|[^\x00-\x7F]/g
      , g = function(e) {
        return (e + "" + Math.random()).replace(f, d)
    }
      , h = function(e) {
        var n = [0, 2, 1][e.length % 3]
          , t = e.charCodeAt(0) << 16 | (e.length > 1 ? e.charCodeAt(1) : 0) << 8 | (e.length > 2 ? e.charCodeAt(2) : 0)
          , o = [u.charAt(t >>> 18), u.charAt(t >>> 12 & 63), n >= 2 ? "=" : u.charAt(t >>> 6 & 63), n >= 1 ? "=" : u.charAt(63 & t)];
        return o.join("")
    }
      , m = function(e) {
        return e.replace(/[\s\S]{1,3}/g, h)
    }
      , p = function() {
        return m(g((new Date).getTime()))
    }
      , w = function(e, n) {
        return n ? p(String(e)).replace(/[+\/]/g, function(e) {
            return "+" == e ? "-" : "_"
        }).replace(/=/g, "") : p(String(e))
    };
    !function() {
        r(document).ajaxSend(function(e, n, t) {
            var i = w(s.getCookie("BAIDUID"));
           ...
        })
    }(),
``` 
主要是这段内容，通过一系列的方法来生成`logid`，由于比较复杂，所以决定通过第三方库`execjs`来调用，把这一段js稍加调整

``` javascript
var u = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/~！@#￥%……&",
l = String.fromCharCode,
d = function(e) {
    if (e.length < 2) {
        var n = e.charCodeAt(0);
        return 128 > n ? e : 2048 > n ? l(192 | n >>> 6) + l(128 | 63 & n) : l(224 | n >>> 12 & 15) + l(128 | n >>> 6 & 63) + l(128 | 63 & n)
    }
    var n = 65536 + 1024 * (e.charCodeAt(0) - 55296) + (e.charCodeAt(1) - 56320);
    return l(240 | n >>> 18 & 7) + l(128 | n >>> 12 & 63) + l(128 | n >>> 6 & 63) + l(128 | 63 & n)
},
f = /[\uD800-\uDBFF][\uDC00-\uDFFFF]|[^\x00-\x7F]/g,
g = function(e) {
    return (e + "" + Math.random()).replace(f, d)
},
h = function(e) {
    var n = [0, 2, 1][e.length % 3],
        t = e.charCodeAt(0) << 16 | (e.length > 1 ? e.charCodeAt(1) : 0) << 8 | (e.length > 2 ? e.charCodeAt(2) : 0),
        o = [u.charAt(t >>> 18), u.charAt(t >>> 12 & 63), n >= 2 ? "=" : u.charAt(t >>> 6 & 63), n >= 1 ? "=" : u.charAt(63 & t)];
    return o.join("")
},
m = function(e) {
    return e.replace(/[\s\S]{1,3}/g, h)
},
p = function() {
    return m(g((new Date).getTime()))
},
w = function(e, n) {
        return n ? p(String(e)).replace(/[+\/]/g, function(e) {
            return "+" == e ? "-" : "_"
        }).replace(/=/g, "") : p(String(e))
    };

function getLogId(data){
        var logid = w(data);
        return logid;
}
```

然后我们调用的时候，输入`BAIDUID`即可，这个可以在最早的输入密码页面的cookie中取得

安装`execjs` 注意，你没看错，命令就是输的`pyexecjs`：
``` python
pip install pyexecjs
```
因为Node.js 是Javascript语言服务器端运行环境，所以你还需要[安装nodejs]([https://nodejs.org/en/download/](https://nodejs.org/en/download/)
)

安装好的情况下在Python3环境下你可以看到
``` python
Python 3.6.3 (v3.6.3:2c5fed8, Oct  3 2017, 17:26:49) [MSC v.1900 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import execjs
>>> execjs.get().name
'Node.js (V8)'
```

然后来调用
``` python
    # 读入修改好的js代码文件
    def get_logid(self, baidu_id):
        with open('boot.js', encoding='utf-8') as f:
            bootjs = f.read()
        # 编译js代码
        js_obj = execjs.compile(bootjs)
        # 调用getLogId方法，给参数baidu_id，也就是BAIDUID，然后得到输出
        res = js_obj.call('getLogId', baidu_id)
        return res
```

这是测试发送请求的代码
``` python
    def __init__(self):
        # 从数据库中取资源链接及密码后存放的列表
        self.row_lists = []
        # 带上密码请求的需要format的链接
        self.pan_post = 'https://pan.baidu.com/share/verify?surl={}&t={}&channel=chunlei' \
                        '&web=1&app_id=250528&bdstoken=08a7da93cf25d7935788a123e3e10c3d' \
                        '&logid={}&clienttype=0'
        # 13位的时间戳
        self.t = int(round(time.time() * 1000))
        # 自己弄得随机ua
        self.user_agent = FaUa.get_ua()

    def get_logid(self, baidu_id):
        with open('boot.js', encoding='utf-8') as f:
            bootjs = f.read()
        js_obj = execjs.compile(bootjs)
        res = js_obj.call('getLogId', baidu_id)
        return res

    def test(self):
        # 保持会话
        session = requests.session()
        # 需要提取的资源链接
        s_url = 'https://pan.baidu.com/share/init?surl=5RdjtVK55eEuayvz82cDmg'
        # verify=False 可以一定程度上避免多次访问导致对方服务器封你，但是会出现警告，这是还需在前面加上加一条requests.packages.urllib3.disable_warnings()，即禁用安全请求警告
        r_bid = session.get(s_url, headers={'user-agent': self.user_agent}, verify=False)
        # 拿到cookie中的BAIDUID
        baiduid = r_bid.cookies['BAIDUID']
        # 根据BAIDUID得到返回的logid
        logid = self.get_logid(baiduid)
        # 获取资源的链接后一部分ID
        surl = s_url.split('surl=')[1]
        # post请求的参数，带上密码，后两个为空
        data = {
            'pwd': 'xxx',
            'vcode': '',
            'vcode_str': '',
        }
        # 请求头
        headers = {
            'user-agent':self.user_agent,
            'Referer': 'https://pan.baidu.com/share/init?surl=5RdjtVK55eEuayvz82cDmg',
            'Accept':'*/*',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With':'XMLHttpRequest',
            'Accept-Language':'zh-CN',
            'Accept-Encoding':'gzip, deflate',
            'Host':'pan.baidu.com',
            'DNT':'1',
            'Connection': 'Keep-Alive',
            'Cache-Control': 'no-cache',
        }
        # 发送post请求
        r = session.post(self.pan_post.format(surl, self.t, logid), data=data, headers=headers, verify=False)
        print(r.url, r.text)
        # 得到返回的BDCLND ，在下一个请求的cookie中带上
        BDCLND = r.json()['randsk']
        headers['Cookie'] = 'BDCLND=' + BDCLND
        print(headers)
        r2 = session.get('https://pan.baidu.com/s/15RdjtVK55eEuayvz82cDmg', headers=headers, verify=False)
        r2.encoding = 'utf-8'
        print(r2.text)
```

这是返回的页面结果
``` html
<!DOCTYPE html>
<html>
<head>

<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta http-equiv="X-UA-Compatible" content="IE=7,9,10,11" />
<meta name="renderer" content="webkit">
<script src="/sns/box-static/disk-share/js/share.dp.js?t=1578364180271"></script>
<link rel="shortcut icon" href="/res/static/images/favicon.ico"/>
<script src="/sns/box-static/disk-share/js/mod.js?t=1578364180271"></script>
<link rel="stylesheet" type="text/css" href="/box-static/consult/base.css"/>
<link rel="stylesheet" type="text/css" href="/box-static/consult/system-core.css"/>
<script src="/box-static/consult/base.js"></script>
<script src="/box-static/consult/system-core.js"></script>

<link rel="stylesheet" type="text/css" href="/box-static/consult/function.css"/>
...
<div class="slide-show-left">
<h2 class="file-name" title="文件名">
<em class="global-icon-16"></em>文件名</h2>
</div>
<div class="slide-show-right">
<span class="slide-header-funcs">
</span>
<div class="module-share-top-bar g-clearfix">
<div class="bar"></div>
</div>
</div>
<div class="cb"></div>
<div class="slide-show-other-infos">
<div class="share-file-info">
<span>2020-01-15 19:22</span>
</div>
<div class="share-valid-check">
失效时间：永久有效
</div>
<div class="slide-show-other-cns clearfix">
<span class="title-funcs">
<span class="funcs-share-area">
</span>
</span>
</div>
<div class="cb"></div>
</div>
</div>
</div>
<div class="share-list" id="shareqr">
<div class="module-toolbar g-clearfix">
<div class="default-dom">
<div class="list-grid-switch list-switched-on">
<a class="list-switch" href="javascript:void(0)" node-type="kyzmAM0B" style="display:none"></a>
<a class="grid-switch" href="javascript:void(0)" node-type="xgcvwQNp"></a>
</div>
</div>
<div class="after-dom"></div>
<div class="user-dom">
</div>
</div>
<!--[if IE]><iframe id="historyIFrameEmulator" style="display: none"></iframe><![endif]-->
<div node-type="KPDwCE" class="KPDwCE">
</div>
</div>
<div class="ad-platform-tips ad-multi-tips" node-type="share-mutil-bottom" id="web-multi-bottom" node-id="web-sharemultibanner">
<div style="margin: 0 auto; width: 960px;" id="cpro_u2164871"></div>
</div>

</div>
</div>
<div class="bd-aside">

<div node-type="module" class="module-share-person-info">
<div class="share-person-inner global-clearfix haha">
<div class="share-person-avatar">
<a href="//yun.baidu.com/buy/center?tag=1&from=sicon" class="vip-icon sicon" target="_blank"><em></em></a>
<a href="javascript:void(0)" title="去Ta的分享主页" class="person-icon"><img alt="fci****re2" src="https://ss0.bdstatic.com/7Ls0a8Sm1A5BphGlnYG/sys/portrait/item/netdisk.1.46160ad.44gPu69hQcgfXwSxAB1nrQ.jpg"></a>
</div>
<div class="share-person-data self">
<div class="share-person-data-top">
<a href="/share/home?uk=3821724077&suk=euEHLsAO_SkKFFGZ7JnePA" target="_blank" title="去Ta的分享主页" class="share-person-username global-ellipsis">fci****re2</a>
<a href="//yun.baidu.com/buy/center?tag=8&from=sicon" class="svip-icon sicon">
<em></em>
...
```

ok，以上就是摸索的内容，主要摸清楚了输入密码后跳转的`logid`如何取得，这样一来我们在拿到 [https://pan.baidu.com/share/init?surl=xxx](https://pan.baidu.com/share/init?surl=xxx) 这样的链接和密码时，就可以通过代码实现批量输入密码后获得访问资源文件页面的权限

那么如何通过请求做到创建新文件夹以及转存呢
我们对把一个资源转存自己盘中的操作进行抓包（第一步是创建一个文件夹，然后第二步再把资源存到这个文件夹中）

这样一来我们就可以看到有`两个明显的请求`：
```
# 创建文件夹的请求
https://pan.baidu.com/api/create?a=commit&channel=chunlei&app_id=250528&bdstoken=undefined&channel=chunlei&web=1&app_id=250528&bdstoken=08a7da93cf25d7935788a123e3e10c3d&logid=MTU3OTYwNDg1NTE3ODAuNTkxMDExODM4OTIwNDg1Mw==&clienttype=0 
```
```
# 转存资源的请求
https://pan.baidu.com/share/transfer?shareid=3153250388&from=3821724077&ondup=newcopy&async=1&channel=chunlei&web=1&app_id=250528&bdstoken=08a7da93cf25d7935788a123e3e10c3d&logid=MTU3OTYwNDg1NTE3ODAuNTkxMDExODM4OTIwNDg1Mw==&clienttype=0 
```

先来看创建文件夹部分的这个post请求：
https://pan.baidu.com/api/create?a=commit&channel=chunlei&app_id=250528&bdstoken=undefined&channel=chunlei&web=1&app_id=250528&bdstoken=08a7da93cf25d7935788a123e3e10c3d&logid=MTU3OTYwNDg1NTE3ODAuNTkxMDExODM4OTIwNDg1Mw==&clienttype=0 

querystring跟上面差不多，就只有`logid`需要改动，主要的是携带的data

参数 | 值 |  状态  
-|-|-
isdir	| 1 | 固定 |
size	| 空 | 固定 |
method| post | 固定  |
dataType	| json | 固定 |
path	| /动漫/斗罗大陆-20180062 01-最新话 | 自定义

可以看出其他的都不用动，在我们发送post请求时只要再带上自定义的path就可以了

``` python
self.create_dir_post = 'https://pan.baidu.com/api/create?a=commit&channel=chunlei' \
                       '&app_id=250528&bdstoken=undefined&channel=chunlei&web=1' \
                       '&app_id=250528&bdstoken=08a7da93cf25d7935788a123e3e10c3d' \
                       '&logid={}&clienttype=0'

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

logid = self.get_logid(baiduid)
create_path = '/动漫/' + source_filename
 # 新建文件夹请求所需的data参数
self.create_dir_data['path'] = create_path
self.headers['Referer'] = s_url
self.headers['Cookie'] = bdclnd + ';' + self._stoken_bduss
r_create_dir = requests.post(self.create_dir_post.format(logid), data=self.create_dir_data, headers=self.headers, verify=False)
print(r_create_dir.json())
```
请求成功后你就可以看到在你的网盘中创建了一个自己命名的文件夹

而下一个post就是实现转存内容的

https://pan.baidu.com/share/transfer?shareid=3153250388&from=3821724077&ondup=newcopy&async=1&channel=chunlei&web=1&app_id=250528&bdstoken=08a7da93cf25d7935788a123e3e10c3d&logid=MTU3OTYwNDg1NTE3ODAuNTkxMDExODM4OTIwNDg1Mw==&clienttype=0 

参数 | 值 |  状态  
-|-|-
shareid | 3153250388 | 变化 |
from | 3821724077 | 变化 |
logid | MTU3OTYwNDg1NTE3ODAuNTkxMDExODM4OTIwNDg1Mw==| 变化|

除了这三个其他querystring中的参数都是固定的，再来看post携带的data
参数 | 值 |  状态 
-|-|-
fsidlist | [597498773956140] | 变化 |
path	| /动漫/斗罗大陆-20180062 01-最新话 | 变化 |

`path`是需要你自己构造的，而`logid`，我们之前已经讲到过生成方法，最关键的就是剩下的三个参数：`shareid`， `from`， `fsidlist`

这参数要在哪里找得到呢

实际上仔细想想，这三个参数肯定在之前的页面源代码或者Js代码中有，之前我们已经可以成功访问 https://pan.baidu.com/s/1xxx 这样的页面了，但是没有注意这个页面的页面源代码有哪些内容，再一想这三个参数是在转存的时候用的，而转存的页面正好是在这个 https://pan.baidu.com/s/1xxx 页面

那么我们观察一下这个页面的源代码就不难发现，有这么些内容
``` html
        yunData.SHAREPAGETYPE = "multi_file";

        yunData.MYUK = "4503602932392500";
        yunData.SHARE_USER_NAME = "fci****re2";
        // 这个就是share_id -----------------------------------
        yunData.SHARE_ID = "3151703641";
        yunData.SIGN = "8e9fc93e128935d2b43ed0cb267c8bca964e33af";
        yunData.sign = "8e9fc93e128935d2b43ed0cb267c8bca964e33af";
        yunData.TIMESTAMP = "1579608010";
        // 这个就是from -----------------------------------
        yunData.SHARE_UK = "3821724077";
        yunData.SHARE_PUBLIC = 0;
        yunData.SHARE_TIME = "1579087633";
        yunData.SHARE_DESCRIPTION = "";
        yunData.MYSELF = +false;
        yunData.MYAVATAR = "https:\/\/ss0.bdstatic.com\/7Ls0a8Sm1A5BphGlnYG\/sys\/portrait\/item\/netdisk.1.c8d8ac7b.54y40Nw_2ayb-Pg7hPetiA.jpg";

                    yunData.NOVELID = "";
                // 这个就是fsidlist -----------------------------------
                yunData.FS_ID = "540067849856680";
        yunData.FILENAME = "20190069 科学的超电磁炮T";
        yunData.PATH = "\/sharelink3821724077-540067849856680\/20190069 科学的超电磁炮T";
        yunData.PATH_MD5 = "10451130099679229426";
        yunData.CTIME = "1579087633";
        yunData.CATEGORY = "6";
```
那么只要能够访问这个页面，然后用正则提取出来这三个参数，再构造url发送请求不就解决了嘛

这就是最后的代码：
``` python
        self._stoken_bduss = '这一部分自己在浏览器的cookie中复制粘贴'
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
        self.create_dir_data = {
            'isdir': '1',
            'size':	'',
            'block_list': [],
            'method': 'post',
            'dataType':	'json'
        }
        self.pwd_data = {
            'vcode': '',
            'vcode_str': '',
        }
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
        # print(res)
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
        baiduid = r_baiduid.cookies['BAIDUID']
        logid = self.get_logid(baiduid)
        surl = pan_url.split('surl=')[1]
        self.pwd_data['pwd'] = pan_pwd
        self.headers['Referer'] = pan_url
        # 带密码的post请求，成功可以访问'https://pan.baidu.com/s/1xxx'页面
        r = session.post(self.pan_post.format(surl, self.t, logid), data=self.pwd_data, headers=self.headers, verify=False)
        # 返回带有randsk的json数据，取得bdclnd
        bdclnd = 'BDCLND=' + r.json()['randsk']
        # 访问'https://pan.baidu.com/s/1xxx'的请求头
        self.headers['Cookie'] = bdclnd
        # 'https://pan.baidu.com/s/1xxx'
        s_url = self.pan_s_url.format(surl)
        r_s_url = session.get(s_url, headers=self.headers, verify=False)
        r_s_url.encoding = 'utf-8'
        # 利用正则 获取 转存资源的post请求 所需的三个参数
        params = re.findall(r'yunData\.SHARE_ID = "(.*?)";.*?yunData\.SHARE_UK = "(.*?)";.*?yunData\.FS_ID = "(.*?)";', r_s_url.text, re.S)[0]
        # 调用新建文件夹以及转存的请求
        self.create_dir(baiduid, s_url, source_filename, params, bdclnd)

    def create_dir(self, baiduid, s_url, source_filename, params, bdclnd):
        logid = self.get_logid(baiduid)
        shareid, from_id, fsidlist = params[0], params[1], params[2]
        transfer_url = self.transfer_post.format(shareid, from_id, logid)
        create_path = '/动漫/' + source_filename
        # 新建文件夹请求所需的data参数
        self.create_dir_data['path'] = create_path
        self.headers['Referer'] = s_url
        self.headers['Cookie'] = bdclnd + ';' + self._stoken_bduss
        # 需要两个参数BDUSS，STOKEN
        r_create_dir = requests.post(self.create_dir_post.format(logid), data=self.create_dir_data, headers=self.headers, verify=False)
        print(r_create_dir.json())
        # 需要三个参数BDUSS，BDCLND，STOKEN
        r_transfer = requests.post(transfer_url, data={'fsidlist': '[' + str(fsidlist) + ']', 'path': create_path}, headers=self.headers, verify=False)
        print(r_transfer.text)
```

解释一下 `source_filename, pan_url, pan_pwd`这三个参数分别是path的一部分，资源的链接，资源的密码

另外还有selenium的操作版本，我就直接放代码了

### Selenium操作
``` python
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
        # 自动输入密码
        browser.find_element_by_id("wkwj9A").send_keys(pan_pwd)
        time.sleep(2)
        # 自动回车
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
```


### 备忘
``` python
import time
import datetime

t = time.time()

print (t)                       #原始时间数据  1552267863.7501628
print (int(t))                  #秒级时间戳     1552267863
print (int(round(t * 1000)))    #毫秒级时间戳    1552267863750

nowTime = lambda:int(round(t * 1000))
print (nowTime());              #毫秒级时间戳，基于lambda    1552267863750

print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))   #日期格式化
2019-03-11 09:31:03

```


### 参考
[python3爬虫（5）百度云盘暴力破解尝试](https://blog.csdn.net/liujiayu2/article/details/86476406)
[OpenSSL.SSL.Error: [('SSL routines', 'tls_process_server_certificate', 'certificate verify failed')]（ssl证书问题）](https://www.cnblogs.com/qiaoer1993/p/10985376.html)
[python3+selenium常用语法汇总](https://www.cnblogs.com/1211-1010/p/10898727.html)
[https://www.52pojie.cn/thread-1059883-1-1.html](https://www.52pojie.cn/thread-1059883-1-1.html)











