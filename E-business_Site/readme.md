## 电商网站数据爬取
## 京东

**jingdong_search.py**

京东主要是单页内容分为两次加载，这两次加载的API存在差异，同时有的API在请求时需要带上referer(通过postman模拟请求)

当请求评论时由于请求过于频繁会导致接口不返回数据，这一点需要使用大量的代理IP来解决

**jingdong_camera.py**

之前根据人家提出的具体需求做的爬取京东单反相机数据的脚本

## 苏宁

**suning_search.py**

第一页的四次加载API
```python
# https://search.suning.com/emall/searchV1Product.do?keyword=%E5%8D%8E%E4%B8%BA&ci=0&pg=01&cp=0&il=0&st=0&iy=0&hf=brand_Name_FacetAll:%E5%8D%8E%E4%B8%BA%28HUAWEI%29%3B%E8%8D%A3%E8%80%80%28honor%29&isDoufu=1&isNoResult=0&n=1&sc=0&sesab=ACAABAABCAAA&id=IDENTIFYING&cc=574&sub=1&jzq=9657
# https://search.suning.com/emall/searchV1Product.do?keyword=%E5%8D%8E%E4%B8%BA&ci=0&pg=01&cp=0&il=0&st=0&iy=0&hf=brand_Name_FacetAll:%E5%8D%8E%E4%B8%BA%28HUAWEI%29%3B%E8%8D%A3%E8%80%80%28honor%29&isDoufu=1&isNoResult=0&n=1&sc=0&sesab=ACAABAABCAAA&id=IDENTIFYING&cc=574&paging=1&sub=1&jzq=9657
# https://search.suning.com/emall/searchV1Product.do?keyword=%E5%8D%8E%E4%B8%BA&ci=0&pg=01&cp=0&il=0&st=0&iy=0&hf=brand_Name_FacetAll:%E5%8D%8E%E4%B8%BA%28HUAWEI%29%3B%E8%8D%A3%E8%80%80%28honor%29&isDoufu=1&isNoResult=0&n=1&sc=0&sesab=ACAABAABCAAA&id=IDENTIFYING&cc=574&paging=2&sub=1&jzq=9657
# https://search.suning.com/emall/searchV1Product.do?keyword=%E5%8D%8E%E4%B8%BA&ci=0&pg=01&cp=0&il=0&st=0&iy=0&hf=brand_Name_FacetAll:%E5%8D%8E%E4%B8%BA%28HUAWEI%29%3B%E8%8D%A3%E8%80%80%28honor%29&isDoufu=1&isNoResult=0&n=1&sc=0&sesab=ACAABAABCAAA&id=IDENTIFYING&cc=574&paging=3&sub=1&jzq=9657
```

第二页的前两次加载API
```python
# https://search.suning.com/emall/searchV1Product.do?keyword=%E5%8D%8E%E4%B8%BA&ci=0&pg=01&cp=1&il=0&st=0&iy=0&hf=brand_Name_FacetAll:%E5%8D%8E%E4%B8%BA%28HUAWEI%29%3B%E8%8D%A3%E8%80%80%28honor%29&adNumber=0&isDoufu=1&isNoResult=0&n=1&sc=0&sesab=ACAABAABCAAA&id=IDENTIFYING&cc=574&sub=1&jzq=9657
# https://search.suning.com/emall/searchV1Product.do?keyword=%E5%8D%8E%E4%B8%BA&ci=0&pg=01&cp=1&il=0&st=0&iy=0&hf=brand_Name_FacetAll:%E5%8D%8E%E4%B8%BA%28HUAWEI%29%3B%E8%8D%A3%E8%80%80%28honor%29&adNumber=0&isDoufu=1&isNoResult=0&n=1&sc=0&sesab=ACAABAABCAAA&id=IDENTIFYING&cc=574&paging=1&sub=1&jzq=9657
```

分析结果：

1、每一大页的第一次加载没有paging=这个参数，后面三次分别是paging=1,2,3，实际上paging可以=0  
2、第一大页都没有&adNumber=0，后面都有，但是实际上都不需要  
3、页数按cp=0,1,2,3

商品页面URL：https://product.suning.com/0070517287/10877217665.html  

```python
# 评论数API
# https://review.suning.com/ajax/review_count/general-30268267-000000010877217665-0070517287-----satisfy.htm?callback=satisfy  
# 评论印象API
# https://review.suning.com/ajax/getClusterReview_labels/general-30268267-000000010877217665-0070517287-----commodityrLabels.htm?callback=commodityrLabels&_=1573354366601
# 评论详情API
# https://review.suning.com/ajax/cluster_review_lists/general-30268267-000000010877217665-0070517287-total-1-default-10-----reviewList.htm?callback=reviewList  
```

多种价格API
```python
# https://icps.suning.com/icps-web/getVarnishAllPriceNoCache/000000010808789832,000000000945052194,000000000945052191,000000010808789789,000000010903285808,000000010808789813,000000000945052195,000000000945052192,000000010808789767,000000010905217874,000000010877217665,000000011310617186,000000000945056466,000000011020918908,000000000945052220,000000010808789826,000000000945052196,000000000945052193,000000010808789773,000000011037268249_574_5740101_0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287,0070517287_1_getClusterPrice.jsonp?callback=getClusterPrice
# https://icps.suning.com/icps-web/getVarnishAllPriceNoCache/000000010808976899,000000011091753624,000000000945059423,000000000945056465,000000011020919031,000000000945052197_574_5740101_0070517287,0070517287,0070517287,0070517287,0070517287,0070517287_1_getClusterPrice.jsonp?callback=getClusterPrice
```

套餐价格api
```python
# 9位ID用的是package的接口
# https://pas.suning.com/nspcpackage_000000000945052192_0070517287_574_5740101_000000010808789767%7C1%7CR1901001%7C1.000-000000010689088940%7C1%7CR9004701%7C1.000_0_1__1_.html?callback=pcData&_=1573357546819

# 11位的接口
# https://pas.suning.com/nspcsale_0_000000010808976899_000000010808976899_0070517287_130_574_5740101_20089_1000326_9318_12524_Z001___R1901001_1.0_1___000066138___.html?callback=pcData&_=1573357131057
```

数据预览
```sql
# 1	11433294065	https://product.suning.com/0070517287/11433294065.html	3268.00	3258.00	一加 OnePlus 7T 全网通 8GB+256GB 冰际蓝 骁龙855Plus 90Hz流体屏 4800万超广角三摄 全面屏拍照智能游戏手机 一加7t	33	拍照效果好(11) 外观漂亮(6) 屏幕清晰(6) 做工精致(5) 功能齐全(5) 系统流畅(5) 待机时间长(5) 性价比高 (5) 信号稳定(3) 
```


## 天猫

**tmall_search.py**

IP池完成后更新