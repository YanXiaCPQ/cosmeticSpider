# -*- coding: utf-8 -*-
import scrapy
import re
import urllib.request
from scrapy.http import Request
from huaZhuangPing.items import HuazhuangpingItem
import requests

class TbSpider(scrapy.Spider):
    name = 'taobao'
    allowed_domains = ['s.taobao.com']
    start_urls = [
        "https://s.taobao.com/list?cat=1801%2C50071436%2C50010788&style=grid&seller_type=taobao&spm=a217i.7269965.1000187.1&bcoffset=12&s=0"]

    def star_request(self):
        yield Request(
            "https://s.taobao.com/list?cat=1801%2C50071436%2C50010788&style=grid&seller_type=taobao&spm=a217i.7269965.1000187.1&bcoffset=12&s=0",
            headers={
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.3964.2 Safari/537.36"})

    def parse(self, response):
        patid = '"nid":"(.*?)"'
        patprice = '"view_price":"(.*?)"'
        patname = '"raw_title":"(.*?)"'
        pataddress = '"item_loc":"(.*?)"'

        all_id = re.compile(patid).findall(str(response.body.decode("utf-8")))
        all_price = re.compile(patprice).findall(str(response.body.decode("utf-8")))
        all_name = re.compile(patname).findall(str(response.body.decode("utf-8")))
        all_address = re.compile(pataddress).findall(str(response.body.decode("utf-8")))

        # 模拟成浏览器
        # headers2 = ('User-Agent',
        #             "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.3964.2 Safari/537.36")
        # opener = urllib.request.build_opener()
        # opener.addheaders = [headers2]
        # 将opener安装为全局
        # urllib.request.install_opener(opener)
        patcom = '"rateContent":"(.*?)"'
        patpage = '"lastPage":(.*?),'

        for i in range(len(all_id)):

            thisid = all_id[i]
            price = all_price[i]
            name = all_name[i]
            address = all_address[i]
            url1 = "https://item.taobao.com/item.htm?&id=" + str(all_id[i]) + "&ns=1&abbucket=5"
            patlink = '<link rel="canonical" href="(.*?)"'
            data = urllib.request.urlopen(url1).read().decode('gb18030')
            thislink = re.compile(patlink).findall(data)

            # 开始爬取评论
            url2 = "https://rate.tmall.com/list_detail_rate.htm?itemId=" + thisid + "&sellerId=1782965438&order=3&currentPage=1&append=0&content=1&callback=jsonp1026"

            try:
                com_data = urllib.request.urlopen(url2).read().decode('gb18030')
                all_comment = re.compile(patcom).findall(com_data)
                lastpage = re.compile(patpage).findall(com_data)
                for j in range(2, int(lastpage[0]) + 1):
                    url3 = "https://rate.tmall.com/list_detail_rate.htm?itemId=" + all_id[
                        j] + "&sellerId=1782965438&order=3&currentPage=1&append=0&content=1&callback=jsonp1026"
                    com_data2 = urllib.request.urlopen(url3).read().decode('gb18030')
                    comment = re.compile(patcom).findall(com_data2)
                    all_comment.extend(comment)
            except:
                print(thisid + "商品无评论")
                continue

            print(all_comment)

            yield Request(url=url1, callback=self.next,
                          meta={"price": price, "name": name, "address": address, "id": thisid, "link": thislink})

    def next(self, response):
        item = HuazhuangpingItem()
        item['id'] = response.meta['id']
        item['title'] = response.meta['name']
        item['link'] = response.meta.url
        item['price'] = response.meta['price']
        item['address'] = response.meta['address']
        return item
'''
cd\
cd Spider\huaZhuangPing
scrapy crawl taobao --nolog
'''
