# -*- coding: utf-8 -*-
# Created by hanyi at 2017年10月12日
# 亚马逊购物车
import datetime

import scrapy
from scrapy.utils.response import open_in_browser


class Amazcart(scrapy.Spider):
    # TODO 修改这里也要最下面的子类, 子类从这里copy过去的现在
    custom_settings = {
        'COOKIES_ENABLED': True,
        # 'COOKIES_DEBUG':True,
        # 'LOG_LEVEL':'DEBUG',
        'TO_OBTAIN_IP_ADDRESS': 'http://111.204.107.59:5000',
        'TO_OBTAIN_IP_ADDRESS_USER': 'xbniao',
        'TO_OBTAIN_IP_ADDRESS_PWD': 'xbniao123',
        'CART_MAX_RETRY': 5,

        'DOWNLOADER_MIDDLEWARES': {
            'amazon.middlewares.RotateUserAgentDisableCrawleraCookiesMiddleware': 100,
            'amazon.middlewares.SetVPSPorxyMiddlewares': 110,
            # 'amazon.middlewares.DisableCrawleraCookies': 200,
            # 'scrapy_crawlera.CrawleraMiddleware': 600,
            # 'scrapy_crawlera.CrawleraMiddleware': None,
            'amazon.middlewares.CustomSchedulerDownloaderMiddleware': 1000,
            'amazon.middlewares.CustomCookiesMiddleware':500,
            'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
        },
        'ITEM_PIPELINES': {
            'amazon.pipelines.FilterEmptyItemPipeline': 1,
            'amazon.pipelines.KafkaSimulateCartPipeline': 300,
        },
    }
    name = 'cart'

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        maxRetries = crawler.settings.get('CART_MAX_RETRY', 5)

        return cls(maxRetries, crawler, *args, **kwargs)

    def __init__(self, maxRetries, crawler, *args, **kwargs):
        self.maxRetries = maxRetries
        self.crawler = crawler

    start_urls = []

    # def start_requests(self):
    #
    #     start_urls = [
    #         "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761SL1CX&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761NGLDJ&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761NS2X2&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B076D52S9Z&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761P3KGS&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761Q5WXW&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761MZ651&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761RZXBH&Quantity.1=999&add=add",
    #         #
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761S7J6K&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0769SJY2X&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761MMCF7&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761P1KW3&Quantity.1=999&add=add",
    #         #
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B071XLBJMT&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B075SSQL1B&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761RS9DL&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761N6RG6&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B01M2X7EPZ&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B00E4LGVUO&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B01LR7151C&Quantity.1=999&add=add",
    #         # "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B01G9MC7GC&Quantity.1=999&add=add",
    #     ]
    #
    #     for i, url in enumerate(start_urls):
    #         yield scrapy.Request(url, meta={'cookiejar': i,"saveCookies":1},
    #                              callback=self.parse)
    #     for url in  start_urls:
    #         yield scrapy.FormRequest(url,
    #                                    callback=self.parse)


    # start_urls = [
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761SL1CX&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761NGLDJ&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761NS2X2&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B076D52S9Z&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761P3KGS&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761Q5WXW&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761MZ651&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761RZXBH&Quantity.1=999&add=add",
    #
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761S7J6K&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0769SJY2X&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761MMCF7&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761P1KW3&Quantity.1=999&add=add",
    #
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B071XLBJMT&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B075SSQL1B&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761RS9DL&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0761N6RG6&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B01M2X7EPZ&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B00E4LGVUO&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B01LR7151C&Quantity.1=999&add=add",
    #     "https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B01G9MC7GC&Quantity.1=999&add=add",
    # ]

    def parse(self, response):
        self.logger.debug("++++++++parse++++++++++")
        self.logger.info('cart spider:{}'.format(response.url))
        # 解析隐含域信息
        # open_in_browser(response)
        try:
            asin = response.url[response.url.index('ASIN.1=', 1) + 7:response.url.index('&Quantity.1', 1)]  # 测试
            # asin = response.meta.get(b'frontier_request').meta.get('asin')
        except Exception as e:
            self.logger.info('error,can not get asin from frontier_request.meta.')
            yield {}
        try:
            OfferListingId = response.css('input[name="OfferListingId.1"]').xpath('@value').extract_first()
            Quantity = response.css('input[name="Quantity.1"]').xpath('@value').extract_first()
            add = response.css('input[name="add"]').xpath('@value').extract_first()
            confirmPage = response.css('input[name="confirmPage"]').xpath('@value').extract_first()
            SessionId = response.css('input[name="SessionId"]').xpath('@value').extract_first()
            url1 = 'https://www.amazon.com/gp/aws/cart/add.html?OfferListingId.1={}&Quantity.1={}&add={}&confirmPage={}&SessionId={}'.format(
                OfferListingId, Quantity, add, confirmPage, SessionId)
            UserAgent = response.request.headers["User-Agent"]
            #httpclient()

            request = scrapy.Request(url=url1, callback=self.parse2,
                                     meta={'UserAgent': UserAgent, 'asin': asin,
                                           'cookiejar': response.meta.get('cookiejar', asin),'deleteCookies':1,'saveCookies':0})
            yield request
        except Exception as e:
            try:
                self.logger.info('cart error %s, %s' % (e.__str__(), asin))
                self.crawler.stats.inc_value('error_count')
                errors = self.crawler.stats.get_value('errors', [])
                error_msg = {'spider_name:': self.name, 'error_str:': e.__str__(), 'url:': response.url}
                errors.append(error_msg)
                self.crawler.stats.set_value('errors', errors)
            except:
                pass
            yield {}

    def parse2(self, response):
        self.logger.info("++++++++parse2++++++++++")
        self.logger.debug(f"url:{response.url}")
        # open_in_browser(response)
        retries = response.meta.get("retries", 0)
        # open_in_browser(response)
        try:
            item = {}
            inventoryQuantity='-1'
            self.logger.info(f"asin:{response.meta.get('asin', 'default')}url:{response.url}")
            item['asin'] = response.meta.get('asin', 'default')
            item['scrapyTime'] = int(1000 * datetime.datetime.now().timestamp())



            elument = response.xpath('//*[@id="sc-subtotal-label-activecart"]/text()').extract_first()
            elumentContinue = response.css('input[alt="Continue"]').extract_first()

            if not elument and elumentContinue:
                self.logger.info("++++++++request2++++++++++")
                self.logger.debug(f"asin:{response.meta.get('asin', 'default')}url:{response.url}")
                # open_in_browser(response)
                OfferListingId = response.css('input[name="OfferListingId.1"]').xpath('@value').extract_first()
                Quantity = response.css('input[name="Quantity.1"]').xpath('@value').extract_first()
                add = response.css('input[name="add"]').xpath('@value').extract_first()
                confirmPage = response.css('input[name="confirmPage"]').xpath('@value').extract_first()
                SessionId = response.css('input[name="SessionId"]').xpath('@value').extract_first()
                url1 = 'https://www.amazon.com/gp/aws/cart/add.html?OfferListingId.1={}&Quantity.1={}&add={}&confirmPage={}&SessionId={}'.format(
                    OfferListingId, Quantity, add, confirmPage, SessionId)
                UserAgent = response.request.headers["User-Agent"]
                retries = retries + 1
                if retries >= self.maxRetries:
                    self.logger.warning(f'max retry error. asin:{response.meta.get("asin", "default")}, '
                                        f'url:{response.url}')
                    yield {}
                else:
                    asin = response.meta.get('asin', 'default')
                    request = scrapy.Request(url=url1, callback=self.parse2,
                                             meta={'UserAgent': UserAgent,
                                                   'asin': asin,
                                                   "retries": retries,
                                                   'cookiejar': response.meta.get('cookiejar', asin),'deleteCookies':1,'saveCookies':0})
                    yield request
            elif elument:
                # open_in_browser(response)
                # 页面获取asin
                m = {}
                activeCartViews = response.xpath('id("activeCartViewForm")/div[2]/div')
                self.logger.info(f'activeCartViews count={len(activeCartViews)}')
                for i, activeCart in enumerate(activeCartViews):
                    data_asin = activeCart.xpath('./@data-asin').extract_first()
                    self.logger.info(f'data_asin={data_asin}')
                    data_quantity = activeCart.xpath('./@data-quantity').extract_first()
                    self.logger.info(f'data_auantity={data_quantity}')
                    m[data_asin] = data_quantity

                self.logger.info(f'map count={len(m)}')
                text = response.xpath('//*[@id="sc-subtotal-label-activecart"]/text()').extract_first().strip()
                start = text.find('(')
                end = text.find(' item')
                tatalCount = text[start + 1:end]
                self.logger.info(f'total cart items count ={tatalCount}')
                if len(activeCartViews) > 1:
                    # self.save_to_file(response)
                    # 因为是5, 不准
                    self.logger.info(f'#################cart items count must be 1,count cart count {len(activeCartViews)}###############')
                    yield {}
                else:
                    for key in m:
                        if key != response.meta.get('asin', 'default'):
                            continue
                        inventoryQuantity = m[key] #获取库存
                        if int(inventoryQuantity) >= 999:
                            inventoryQuantity = '1000'
                        item['inventoryQuantity'] = inventoryQuantity
                        self.logger.info(f"item:{item}")
                        yield item
            else:
                # empyt cart
                emptyCart = response.xpath('//*[@id="sc-active-cart"]/div/h1/text()').extract_first()
                infoEnableCookies = response.xpath(
                    '//*[@id="cart-important-message-box"]/div/div/div/p[2]').extract_first()

                if infoEnableCookies and 'Enable Cookies' in infoEnableCookies.strip():
                    self.logger.info('enable cookies in your web Borwser error ,yield empty dict')
                    yield {}

                elif emptyCart and 'Cart is empty' in emptyCart.strip():
                    self.save_to_file(response)  # 确定库存为0
                    self.logger.info("++++++++Your Shopping Cart is empty++++++++++")
                    inventoryQuantity='0'
                    item['inventoryQuantity'] = inventoryQuantity
                    self.logger.info(f"item:{item}")
                    yield item
                else:
                    title = response.xpath('/html/head/title/text()').extract_first()
                    if title and 'Robot Check' in title.strip() :
                        self.logger.info("++++++++amazon Authentication Code,Robot Check++++++++++")
                        # 一旦有这种错误，应该重新拨号
                    else:
                        self.save_to_file(response)  # 发现新错误
                    inventoryQuantity='-1'
                    item['inventoryQuantity'] = inventoryQuantity
                    self.logger.info(f"item:{item}")
                    yield item

        except Exception as e:
            try:
                self.logger.info('cart error %s, %s,%s' % (e.__str__(), response.meta.get('asin', '000'), response.url))
                self.crawler.stats.inc_value('error_count')
                errors = self.crawler.stats.get_value('errors', [])
                error_msg = {'spider_name: ': self.name, 'error_str: ': e.__str__(), 'url: ': response.url}
                errors.append(error_msg)
                self.crawler.stats.set_value('errors', errors)
            except:
                pass
            yield {}
    def save_to_file(self, response):
        """Open the given response in a local web browser, populating the <base>
        tag for external links to work
        """
        from scrapy.http import HtmlResponse, TextResponse
        import os
        import tempfile
        from scrapy.utils.python import to_bytes
        # XXX: this implementation is a bit dirty and could be improved
        body = response.body
        if isinstance(response, HtmlResponse):
            if b'<base' not in body:
                repl = '<head><base href="%s">' % response.url
                body = body.replace(b'<head>', to_bytes(repl))
            ext = '.html'
        elif isinstance(response, TextResponse):
            ext = '.txt'
        else:
            raise TypeError("Unsupported response type: %s" %
                            response.__class__.__name__)
        fd, fname = tempfile.mkstemp(ext)
        self.logger.info(f"file path=file://{fname}")
        os.write(fd, body)
        os.close(fd)


class AmazCartBSR(Amazcart):
    name = 'cart_bsr'
    custom_settings = {
        'COOKIES_ENABLED': True,
        # 'COOKIES_DEBUG':True,
        # 'LOG_LEVEL':'DEBUG',
        'TO_OBTAIN_IP_ADDRESS': 'http://111.204.107.59:5000',
        'TO_OBTAIN_IP_ADDRESS_USER': 'xbniao',
        'TO_OBTAIN_IP_ADDRESS_PWD': 'xbniao123',
        'CART_MAX_RETRY': 5,

        'DOWNLOADER_MIDDLEWARES': {
            'amazon.middlewares.RotateUserAgentDisableCrawleraCookiesMiddleware': 100,
            'amazon.middlewares.SetVPSPorxyMiddlewares': 110,
            # 'amazon.middlewares.DisableCrawleraCookies': 200,
            # 'scrapy_crawlera.CrawleraMiddleware': 600,
            # 'scrapy_crawlera.CrawleraMiddleware': None,
            'amazon.middlewares.CustomSchedulerDownloaderMiddleware': 1000,
            'amazon.middlewares.CustomCookiesMiddleware':500,
            'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
        },
        'ITEM_PIPELINES': {
            'amazon.pipelines.FilterEmptyItemPipeline': 1,
            'amazon.pipelines.KafkaSimulateCartPipelineBSR': 300,
        },
    }
