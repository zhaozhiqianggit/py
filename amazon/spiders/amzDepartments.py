# -*- coding: utf-8 -*-
# Created by wl at 2017-9-5 15:02:56
# 亚马逊分类
import scrapy
import urllib.parse
import datetime

class test(scrapy.Spider):

    name = "departments2"

    start_urls = [
        "https://www.amazon.com/gp/site-directory/ref=nav_shopall_btn",
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            'amazon.pipelines.KafkaCategoryPipeline': 300,
        }
    }

    storeItem = {}

    def parse(self, response):
        base = response.xpath('//*[@id="a-page"]/div[2]/div/div[4]/div[1]')
        title = base.xpath('./h2/text()').extract_first()
        level1 = base.xpath('./div//a')
        for i in level1:
            url = i.xpath('./@href').extract_first()
            item = {}
            item['rootDepartments'] = title
            item['departments'] = title + '->' + i.xpath('./text()').extract_first()
            item['href'] = 'https://www.amazon.com'+url
            item['level'] = 2
            item['nodeID'] = url[url.find('node=')+5:]
            yield response.follow(url=url, callback=self.parse_iter1, meta={'msg': item})

    def parse_iter1(self,response):
        item = response.meta.get('msg')
        # count = response.xpath('//*[@id="s-result-count"]/text()').extract()
        # print(count)
        # if count:
        #     for i in count:
        #         start = i.find('of')
        #         if start == -1:
        #             start = -3
        #         item['count'] = i[start + 3:i.find('result') - 1]
        #         break
        # else:
        #     item['count'] = ''


        # yield item  # 获取数量后，保存上级完整数据

        base = response.xpath('//*[@id="leftNav"]/ul[@class="a-unordered-list a-nostyle a-vertical a-spacing-base"]/ul//a|//*[@id="leftNavContainer"]/ul[@class="a-unordered-list a-nostyle a-vertical a-spacing-base"]/ul//a')
        level= item['level']
        if level<10:
            if base:
                departments = item['departments']
                for i in base:
                    item2 = {}
                    item2['level'] = item['level'] + 1
                    url = i.xpath('./@href').extract_first()
                    urlParse = urllib.parse.unquote(url)
                    item2['departments'] = departments + '->' + i.xpath('./span/text()').extract_first()
                    item2['href'] = 'https://www.amazon.com' + url
                    item2['nodeID'] = urlParse[urlParse.rfind('n:')+2:urlParse.find('&bbn=')]
                    item2['timeStamp'] = int(1000*datetime.datetime.now().timestamp())
                    # item2['count'] = 0

                    if item2['level'] == 3:
                        item3 = {}
                        item3['href'] = item2['href']
                        yield item3

                    yield response.follow(url=url, callback=self.parse_iter1, meta={'msg': item2})