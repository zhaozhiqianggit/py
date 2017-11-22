import logging

import scrapy
from scrapy.conf import settings


# 获取三级分类下前19页商品链接
class ThreeStageClassificationProductUrls(scrapy.Spider):
    name = "TSCProductUrls"
    # db = MongoClient(host=settings['MONGODB_HOST'], port=settings['MONGODB_PORT'])[settings['MONGODB_DBNAME']]
    # def start_requests(self):
    #     list = []
    #     #不同分类测试
    #     urls = [
    #
    #         #"https://www.amazon.com/s/ref=lp_2474939011_il_ti_fashion-boys-accessories?rh=n%3A7141123011%2Cn%3A7147443011%2Cn%3A2474939011&ie=UTF8&qid=1505193393&lo=fashion-boys-accessories"
    #         #"https://www.amazon.com/s/ref=lp_6358543011_ex_n_7?rh=n%3A7141123011%2Cn%3A7147440011%2Cn%3A6358543011%2Cn%3A6358545011&bbn=6358543011&ie=UTF8"
    #         #"https://www.amazon.com/s/ref=lp_1040660_ex_n_4?rh=n%3A7141123011%2Cn%3A7147440011%2Cn%3A1040660%2Cn%3A2368343011&bbn=1040660&ie=UTF8"
    #         #"https://www.amazon.com/s/ref=lp_9479199011_ex_n_7?rh=n%3A7141123011%2Cn%3A9479199011%2Cn%3A15743231&bbn=9479199011&ie=UTF8"
    #         "https://www.amazon.com/s/ref=lp_2617941011_nr_n_7?fst=as%3Aoff&rh=n%3A2617941011%2Cn%3A%212617942011%2Cn%3A2237594011&bbn=2617942011&ie=UTF8&qid=1505293424&rnid=2617942011"
    #     ]
    #
    #     # posts = self.db[settings['MONGODB_DOCNAME']]
    #     # for post in posts.find({'level': {'$eq': 3}}):
    #     #     #print(post['href'])
    #     #     urls.append(post['href'])
    #
    #     for url in urls:
    #         yield scrapy.Request(url=url, callback=self.parse, meta={'pageNum': 1, 'list': list})

    custom_settings = {
        'ITEM_PIPELINES': {
            'amazon.pipelines.FilterEmptyItemPipeline': 1,
            'amazon.pipelines.KafkaSeedPipeline': 300,
        }
    }

    def parse(self, response):
        item = {}
        try:
            pageCount = settings['TSCPRODUCTURLS_PAGECOUNT']
            # logging.info("======="+str(pageCount))
            pageNum = response.meta.get('pageNum', 1)
            urlList = response.meta.get('list', [])
            # 从第二页开始后由于js加载 产生不同的商品div （atfResults，btfPreResults，btfResults） 所有分三部分提取商品url
            if pageNum == 1:
                productUrlLis = response.xpath('//*[@id="mainResults"]/ul/li')
                productUrlLis2 = []
                productUrlLis3 = []
            else:
                productUrlLis = response.xpath('//*[@id="atfResults"]/ul/li')
                productUrlLis2 = response.xpath('//*[@id="btfPreResults"]/ul/li')
                productUrlLis3 = response.xpath('//*[@id="btfResults"]/ul/li')
            # logging.info(len(_list))
            for li in productUrlLis:
                url = li.xpath('.//a[@class="a-link-normal a-text-normal"]/@href').extract_first()
                if url is None:
                    logging.info(li)
                    continue
                else:
                    if url.startswith('https://'):
                        urlList.append(url)
            if len(productUrlLis2) > 0:
                for li1 in productUrlLis2:
                    url1 = li1.xpath('.//a[@class="a-link-normal a-text-normal"]/@href').extract_first()
                    if url1 is None:
                        logging.info(li1)
                        continue
                    else:
                        if url1.startswith('https://'):
                            urlList.append(url1)
            if len(productUrlLis3) > 0:
                for li2 in productUrlLis3:
                    url2 = li2.xpath('.//a[@class="a-link-normal a-text-normal"]/@href').extract_first()
                    if url2 is None:
                        logging.info(li2)
                        continue
                    else:
                        if url2.startswith('https://'):
                            urlList.append(url2)
            next_page = response.xpath('id("pagnNextLink")/@href').extract_first()

            if next_page and pageNum < pageCount:
                yield response.follow(url="https://www.amazon.com" + next_page,
                                      callback=self.parse,
                                      meta={'pageNum': pageNum + 1, 'list': urlList})
            else:
                item["TSCProductUrls"] = urlList
                logging.info(item)
                yield item
        except Exception as e:
            try:
                self.logger.info('cart error %s' % e.__str__())
                self.crawler.stats.inc_value('error_count')
                errors = self.crawler.stats.get_value('errors', [])
                error_msg = {'spider_name': self.name, 'error_str': e.__str__(), 'url': response.url}
                errors.append(error_msg)
                self.crawler.stats.set_value('errors', errors)
            except:
                pass
            yield {}
