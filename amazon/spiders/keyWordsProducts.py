import logging

import scrapy
from scrapy.conf import settings


# 根据keyword获取商品asin 信息
class KeyWordsProducts(scrapy.Spider):
    name = "keyWordsProducts"

    custom_settings = {
        'ITEM_PIPELINES': {
            'amazon.pipelines.FilterEmptyItemPipeline': 1,
            'amazon.pipelines.KafkaKeywordPipeline': 300,
        }
    }

    # def start_requests(self):
    #     urls = [
    #         #"https://www.amazon.com/s/ref=nb_sb_ss_c_1_300?url=search-alias%3Daps&field-keywords=toilet+paper"
    #         #"https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=toilet+paper&rh=i%3Aaps%2Ck%3Atoilet+paper"
    #         #"https://www.amazon.com/s/ref=nb_sb_ss_ime_c_1_2?url=search-alias%3Daps&field-keywords=keyboard&sprefix=ke%2Caps%2C401&crid=3TWJOTIAFQTNS"
    #         #"https://www.amazon.com/s/ref=nb_sb_ss_c_1_13?url=search-alias%3Daps&field-keywords=iphone+6+case&sprefix=iphone+6+case%2Caps%2C2300&crid=N46B7YVXYLOM&rh=i%3Aaps%2Ck%3Aiphone+6+case"
    #         #"https://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords=iphone+7+case&sprefix=iphone+6+case%2Caps%2C2300&crid=N46B7YVXYLOM&rh=i%3Aaps%2Ck%3Aiphone+7+case"
    #         #"https://www.amazon.com/s/ref=nb_sb_ss_c_1_5?url=search-alias%3Daps&field-keywords=torras&sprefix=torra%2Caps%2C451&crid=2H4ZO3XVFZNHF&rh=i%3Aaps%2Ck%3Atorras"
    #         "https://www.amazon.com/s/ref=nb_sb_ss_c_1_1?url=search-alias%3Daps&field-keywords=toilet+paper&sprefix=t%2Caps%2C1342&crid=FEF1COSUSN7I&rh=i%3Aaps%2Ck%3Atoilet+paper"
    #     ]
    #
    #     for url in urls:
    #         yield scrapy.Request(url=url, callback=self.parse, meta={'asin': "B06Y3Z6PTF", 'keyword': 'Atoiletpaper', 'uuid': "123"})
    #
    #         # yield scrapy.Request(url, self.parse, meta={
    #         #     'splash': {
    #         #         'args': {
    #         #             # set rendering arguments here
    #         #             'html': 1,
    #         #             'wait': 500
    #         #             #'png': 1,
    #         #
    #         #             # 'url' is prefilled from request url
    #         #             # 'http_method' is set to 'POST' for POST requests
    #         #             # 'body' is set to request body for POST requests
    #         #         },
    #         #
    #         #         # optional parameters
    #         #         #'endpoint': 'render.json',  # optional; default is render.json
    #         #         #'splash_url': '<url>',  # optional; overrides SPLASH_URL
    #         #         #'slot_policy': scrapy_splash.SlotPolicy.PER_DOMAIN,
    #         #         'splash_headers': {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'}
    #         #         # 'dont_process_response': True,  # optional, default is False
    #         #         # 'dont_send_headers': True,  # optional, default is False
    #         #         # 'magic_response': False,  # optional, default is True
    #         #     }
    #         # })
    #
    #         #logging.info("start!!!!!!!!!!!!!!!!!!!!!!")
    #        # yield SplashRequest(url=url, callback=self.parse, args={'wait': 0.5}, meta={'count': 0 , 'list': list},splash_headers={'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1'})

    def parse(self, response):
        item = {}
        try:
            # asinList = response.meta.get('list')
            count = response.meta.get('count')
            rasin = response.meta.get('asin')
            keyword = response.meta.get('keyword')
            url = response.meta.get('keyurl')
            uuid = response.meta.get('uuid')
            # assert (keyword is not None)
            # assert (uuid is not None)
            # assert (rasin is not None)
            if url is None:
                url = response.url
            if count is None:
                count = 0
            # logging.info(count)
            keyWordsCount = settings['KEYWORDS_COUNT']
            atfResultsLis = response.xpath('//*[@id="atfResults"]/ul/li')
            btfResultsLis = response.xpath('//*[@id="btfResults"]/ul/li')
            rankingNum = -1
            # a1 = response.xpath('//*[@id="atfResults"]/ul/li//div[@class="a-fixed-left-grid-col a-col-right"]/h5')

            for ali in atfResultsLis:
                asin = ali.xpath('./@data-asin').extract_first()
                if asin == rasin:
                    sponsored = ali.xpath('./div[@class="a-fixed-left-grid-col a-col-right"]/h5').extract_first()
                    # logging.info("-----")
                    # logging.info(sponsored)
                    if sponsored is None:
                        idStr = ali.xpath('./@id').extract_first()
                        rankingNum = idStr.split('_')[1].strip()
                        rankingNum = int(rankingNum) + 1
                        break
                    else:
                        count = count + 1
                        if count >= keyWordsCount:
                            break
                else:
                    count = count + 1
                    if count >= keyWordsCount:
                        break

            for bli in btfResultsLis:
                asins = bli.xpath('./@data-asin').extract_first()
                if asins == rasin:
                    # logging.info(bli)
                    sponsored = bli.xpath('./div[@class="a-fixed-left-grid-col a-col-right"]/h5').extract_first()
                    # logging.info("+++++")
                    # logging.info(sponsored)
                    if sponsored is None:
                        idStr = bli.xpath('./@id').extract_first()
                        rankingNum = idStr.split('_')[1].strip()
                        rankingNum = int(rankingNum) + 1
                        break
                    else:
                        count = count + 1
                        if count >= keyWordsCount:
                            break
                else:
                    count = count + 1
                    if count >= keyWordsCount:
                        break
            if rankingNum == -1 and count < keyWordsCount:
                next_page = response.xpath('id("pagnNextLink")/@href').extract_first()
                if next_page:
                    yield response.follow(url="https://www.amazon.com" + next_page,
                                          callback=self.parse,
                                          meta={'count': count, 'asin': rasin, 'keyword': keyword, 'keyurl': url,
                                                'uuid': uuid})
            else:
                logging.info("--------:排名")
                logging.info(rankingNum)
                # assert(int(rankingNum) <= int(keyWordsCount))
                item['rankingNum'] = rankingNum
                item['url'] = url
                item['asin'] = rasin
                item['keyword'] = keyword
                item['uuid'] = uuid
                logging.info(item)
                if item.get('asin') and item.get('keyword') and item.get('uuid'):
                    yield item
                else:
                    self.logger.warning(f'keyword spider yield empty. item:{item}')
                    yield {}
        except Exception as e:
            try:
                self.logger.info('cart error %s' % e.__str__())
                self.crawler.stats.inc_value('error_count')
                errors = self.crawler.stats.get_value('errors', [])
                error_msg = {'spider_name: ': self.name, 'error_str: ': e.__str__(), 'url: ': response.url}
                errors.append(error_msg)
                self.crawler.stats.set_value('errors', errors)
            except:
                pass
            yield {}
