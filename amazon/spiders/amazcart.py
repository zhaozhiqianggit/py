# -*- coding: utf-8 -*-
# Created by wl at 2017-9-6 15:02:56
# 亚马逊购物车
import datetime

import scrapy
import time


class Amazcart(scrapy.Spider):

    name = 'cart_backup'


    custom_settings = {
        'ITEM_PIPELINES': {
            'amazon.pipelines.KafkaSimulateCartPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'amazon.middlewares.PhantomJSMiddleware': 700,
        }
    }

    # def parse(self, response):
    #     self.logger.info('cart spider:{}'.format(response))
    #     request = scrapy.Request(url=response.url, callback=self.parse2)
    #     request.meta['PhantomJS'] = True
    #     request.meta['asin'] = response.meta[b'frontier_request'].meta.get('asin')
    #     yield request

    def parse(self, response):
        try:
            if not response.meta.get('flag', False):
                item = {}
                text = response.xpath('//*[@id="sc-subtotal-label-activecart"]/text()').extract_first().strip()
                start = text.find('(')
                end = text.find(' item')
                # item['asin'] = response.meta['asin']
                item['asin'] = response.meta.get(b'frontier_request').meta.get('asin')
                item['inventoryQuantity'] = text[start + 1:end]
                # item['scrapyTime'] = int(datetime.datetime.utcnow().timestamp())
                item['scrapyTime'] = int(1000000000 * datetime.datetime.utcnow().timestamp())
                yield item
            else:
                item = {}
                # item['asin'] = response.meta['asin']
                item['asin'] = response.meta.get(b'frontier_request').meta.get('asin')
                item['inventoryQuantity'] = '0'
                item['scrapyTime'] = int(1000000000 * datetime.datetime.utcnow().timestamp())
                yield item
        except Exception as e:
            self.logger.info('cart error %s' % e.__str__())
            self.crawler.stats.inc_value('error_count')
            errors = self.crawler.stats.get_value('errors', [])
            error_msg={'spider_name':self.name,'error_str':e.__str__(),'url':response.url}
            errors.append(error_msg)
            self.crawler.stats.set_value('errors',errors)