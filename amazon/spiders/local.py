import logging
import datetime

import scrapy
import json
import re
from scrapy.conf import settings
import pymysql


# 获取三级分类下前19页商品链接
class ThreeStageClassificationProductUrls(scrapy.Spider):
    name = "local"

    # db = MongoClient(host=settings['MONGODB_HOST'], port=settings['MONGODB_PORT'])[settings['MONGODB_DBNAME']]
    custom_settings = {
        'ITEM_PIPELINES': {
            'amazon.pipelines.MongoPipeline': 300,
        }
    }
    def start_requests(self):
        list = []
        # 不同分类测试
        urls = [

            #"https://www.amazon.com/s/ref=lp_2474939011_il_ti_fashion-boys-accessories?rh=n%3A7141123011%2Cn%3A7147443011%2Cn%3A2474939011&ie=UTF8&qid=1505193393&lo=fashion-boys-accessories"
            # "https://www.amazon.com/s/ref=lp_6358543011_ex_n_7?rh=n%3A7141123011%2Cn%3A7147440011%2Cn%3A6358543011%2Cn%3A6358545011&bbn=6358543011&ie=UTF8"
            # "https://www.amazon.com/s/ref=lp_1040660_ex_n_4?rh=n%3A7141123011%2Cn%3A7147440011%2Cn%3A1040660%2Cn%3A2368343011&bbn=1040660&ie=UTF8"
            # "https://www.amazon.com/s/ref=lp_9479199011_ex_n_7?rh=n%3A7141123011%2Cn%3A9479199011%2Cn%3A15743231&bbn=9479199011&ie=UTF8"
            # "https://www.amazon.com/s/ref=lp_2617941011_nr_n_7?fst=as%3Aoff&rh=n%3A2617941011%2Cn%3A%212617942011%2Cn%3A2237594011&bbn=2617942011&ie=UTF8&qid=1505293424&rnid=2617942011"
        ]
        db = pymysql.connect("172.16.1.81", "root", "root123", "amazon_category")
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()

        # SQL 查询语句
        sql = "SELECT	PATH_BY_ID  FROM amazon_category WHERE	LEVEL = '3'AND (	PATH_BY_NAME LIKE ('Health & Household%')	OR PATH_BY_NAME LIKE ('Electronics%')	OR PATH_BY_NAME LIKE ('Sports & Outdoors%')	OR PATH_BY_NAME LIKE ('Home & Kitchen%')	OR PATH_BY_NAME LIKE ('Clothing, Shoes & Jewelry%'))"
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            for row in results:
                data = row[0].split(',')
                # print("https://www.amazon.com/s?rh=n:%s,n:!%s,n:%s,n:%s" % (data[0], data[1], data[2], data[3]))
                data = "https://www.amazon.com/s?rh=n:" + data[0] + ",n:!" + data[1] + ",n:" + data[2] + ",n:" + data[3]
                urls.append(data)
                # producer.send('One', str.encode(data) )
        except:
            print("Error: unable to fetch data")

        db.close()

        # posts = self.db[settings['MONGODB_DOCNAME']]
        # for post in posts.find({'level': {'$eq': 3}}):
        #      #print(post['href'])
        #      urls.append(post['href'])

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'pageNum': 1, 'list': list})

            # custom_settings = {
            #     'ITEM_PIPELINES': {
            #         'amazon.pipelines.KafkaSeedPipeline': 300,
            #     }
            # }

    def parse(self, response):
        item = {}
        try:
            pageCount = 5
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
                if url.startswith('https://'):
                    urlList.append(url)
            if len(productUrlLis2) > 0:
                for li1 in productUrlLis2:
                    url1 = li1.xpath('.//a[@class="a-link-normal a-text-normal"]/@href').extract_first()
                    if url1.startswith('https://'):
                        urlList.append(url1)
            if len(productUrlLis3) > 0:
                for li2 in productUrlLis3:
                    url2 = li2.xpath('.//a[@class="a-link-normal a-text-normal"]/@href').extract_first()
                    if url2.startswith('https://'):
                        urlList.append(url2)
            next_page = response.xpath('id("pagnNextLink")/@href').extract_first()

            if next_page and pageNum < pageCount:
                yield response.follow(url="https://www.amazon.com" + next_page,
                                      callback=self.parse,
                                      meta={'pageNum': pageNum + 1, 'list': urlList})
            else:
                item["TSCProductUrls"] = urlList
                # logging.info(item)
            for url in urlList:
                yield response.follow(url=url,
                                      callback=self.product,
                                      )
        except Exception as e:
            logging.info("Error::" + e)

    def product(self, response):
        item = {'asin': '', 'url': "", 'parentasin': '', 'scrapyTime': '', 'marketplace': '', 'reviewsnum': '-1',
                'stars': '-1', 'star5': '-1%',
                'star4': '-1%', 'star3': '-1%', 'star2': '-1%', 'star1': '-1%', 'questionsnum': '-1', 'imgurl': [],
                'brand': '',
                'flag': '', 'asinname': '',
                'price': '-1', 'cur': '', 'bulletpoints': '', 'variationname': '', 'publishedtime': '',
                'sellername': '',
                'sellerid': '',
                'shippingmethod': 'Fulfilled by Manufacturers', 'category': '', 'bsr': '-1', 'subcategory': [],
                'childBsr': [], 'sellerCount': '-1',
                'shipAdress': '',
                'spec': {'dimensions': '', 'weight': ''}}

        try:
            # asin
            asinList = ["//span[@class='a-declarative']/@data-a-modal",
                        "//div[@id='tell-a-friend']//span[@class='a-declarative']/@data-a-modal"]
            item = self.get_value(response, asinList, 'asin', item)
            if item['asin'] is '':
                item['asin'] = response.xpath("//div[@id='averageCustomerReviews']/@data-asin").extract_first()
            if item['asin'] is '' or item['asin'] is None:
                yield {}
            else:
                # 商品详情url
                item['url'] = response.url
                # parent_asin
                parent_asin_b = response.xpath(
                    "//div[@id='tell-a-friend']/@data-dest|//div[@id='tell-a-friend-byline']/@data-dest").extract_first()
                if parent_asin_b:
                    index = parent_asin_b.find('parentASIN')
                    if index:
                        item['parentasin'] = parent_asin_b[index + 11:index + 21]
                    else:
                        item['parentasin'] = "0000000000"
                else:
                    item['parentasin'] = "0000000000"
                # 抓取时间
                item['scrapyTime'] = int(1000 * datetime.datetime.now().timestamp())
                # marketplace
                if item['url'].find('.com') > 0:
                    item['marketplace'] = "ATVPDKIKX0DER"

                # 评论
                review = response.xpath('//*[@id="acrCustomerReviewText"]/text()').extract_first()
                item = self.getReview(response, review, item)
                question = response.xpath('//*[@id= "askATFLink"]/span/text()').extract_first()
                item = self.getQuestion(question, item)
                # 图片
                imgStr = response.xpath('//script[contains(text(),"colorImages")]/text()').extract_first()
                mainImage = response.xpath('//div[@id="mainImageContainer"]/img/@src').extract()
                imgBooks = response.xpath('//div[@id="img-canvas"]/img/@src').extract()

                imglist = []
                if imgStr:
                    imgStr = imgStr[(imgStr.find('[{')):imgStr.find('}]') + 2]  #
                    dict = json.loads(imgStr)
                    for i in dict:
                        if i["large"]:
                            imglist.append(i["large"])
                    item["imgurl"] = imglist
                elif mainImage:
                    if "base64" in mainImage[0]:
                        imgStr1 = response.xpath(
                            '//div[@id="mainImageContainer"]/img/@data-a-dynamic-image').extract_first()
                        imgjson = json.loads(imgStr1)
                        for ij in imgjson.keys():
                            imglist.append(ij)
                        item["imgurl"] = imglist
                    else:
                        item["imgurl"] = mainImage
                elif imgBooks:
                    if "base64" in imgBooks[0]:
                        imgStr1 = response.xpath(
                            '//div[@id="img-canvas"]/img/@data-a-dynamic-image').extract_first()
                        imgjson = json.loads(imgStr1)
                        for ij in imgjson.keys():
                            imglist.append(ij)
                        item["imgurl"] = imglist
                    else:
                        item["imgurl"] = imgBooks
                # 品牌
                brand = response.xpath('//*[@id="brand"]/text()|//a[@id="bylineInfo"]/text()').extract_first()
                if brand:
                    if brand.strip():
                        item['brand'] = brand.strip()
                    else:
                        isImg = response.xpath('//*[@id="brand"]/@href').extract_first()
                        if isImg:
                            item['brand'] = isImg.split("/")[1]
                # 竞品标识
                item['flag'] = '01'  # 竞品

                # 标题
                tileList = ['//*[@id="ProductTitle"]/text()', '//*[@id="productTitle"]/text()',
                            "//div[@id='title_feature_div']/h1/text()"]
                item = self.Xparse(response, tileList, 'asinname', item)
                # 价格
                priceList = ['//*[@id="priceblock_ourprice"]/text()', '//*[@id="priceblock_dealprice"]/text()',
                             '//*[@id="priceblock_saleprice"]/text()',
                             '//span[@class="a-size-medium a-color-price header-price"]/text()',
                             '//span[@class="a-size-medium a-color-price offer-price a-text-normal"]/text()']
                item = self.Xparse(response, priceList, 'price', item)
                if item['price'] is '-1':
                    pt = response.xpath('//span[@class="verticalAlign a-size-large"]/text()').extract_first()
                    pm = response.xpath('//span[@class="buyingPrice"]/text()').extract_first()
                    pl = response.xpath(
                        '//span[@class="verticalAlign a-size-large priceToPayPadding"]/text()').extract_first()
                    if pt and pm and pl:
                        item['price'] = pm + "." + pl
                        item['cur'] = pt
                # 描述
                # description_headList = ['//*[@id="feature-bullets"]//span/text()']
                # item = self.Yparse(response, description_headList, 'description_head', item)
                #
                # descriptionList = ['//*[@id="productDescription_feature_div"]/*[@id="productDescription"]//p/text()']
                # item = self.Yparse(response, descriptionList, 'ptiondesc', item)
                # 商品简介 要点
                bulletpoints = response.xpath('//div[@id="feature-bullets"]//li/span[@class="a-list-item"]')
                bulletpointsStr = ""
                if bulletpoints:
                    for point in bulletpoints:
                        bulletpointsStr = bulletpointsStr + point.xpath('./text()').extract_first().strip() + "\n"
                    item['bulletpoints'] = bulletpointsStr
                # 变体组合名称
                variationname = response.xpath('//form[@id="twister"]//div[contains(@id,"variation")]')
                variationnameStr = ""
                if variationname:
                    for variation in variationname:
                        v = variation.xpath('.//div/label/text()').extract_first()
                        if v:
                            v = v.replace("\n", "").replace(' ', '')
                        else:
                            v = ""
                        vStr = variation.xpath('./div/span/text()').extract_first()
                        if vStr is None:
                            vStr = variation.xpath(
                                '//div[@id="variation_size_name"]//option[@class="dropdownSelect"]/text()').extract_first()
                        if vStr:
                            vStr = vStr.replace("\n", "").replace(' ', '')
                        else:
                            vStr = ""
                        variationnameStr = variationnameStr + v + vStr + "   "
                    item['variationname'] = variationnameStr
                else:
                    item['variationname'] = ""
                    # 规格
                specList = [
                    ['//*[@id="productDetailsTable"]//li', 0],
                    [
                        '//*[@id="productDetails_techSpec_section_1"]//tr|//*[@id="productDetails_techSpec_section_2"]//tr',
                        1],
                    ['//*[@id="technical-details-table"]//tr', 2],
                    ['//*[@id="productDetails_detailBullets_sections1"]//tr', 1]
                    # ['//*[@id="detailBullets_feature_div"]//tr', 1]
                ]
                item = self.Zparse(response, specList, 'spec', item)
                # 刊登时间
                timeList = ['//tr[@class="date-first-available"]/td[@class="value"]/text()',
                            '//th[contains(text(),"Date first available at Amazon.com")]/following-sibling::td/text()',
                            '//th[contains(text(),"Date First Available")]/following-sibling::td/text()']
                item = self.Xparse(response, timeList, 'publishedtime', item)
                sellerATag = response.xpath('//*[@id ="merchant-info"]/a/text()').extract()
                name = response.xpath('//*[@id ="merchant-info"]/text()').extract_first()
                datepat = re.compile('.*seller=(\w*)\w*')
                # amaozn Warehouse Deals
                warehouse = response.xpath(
                    '//div[@class="a-section a-spacing-base"]//div[contains(text(),"Sold by")]/a/text()').extract_first()
                warehouseId = response.xpath(
                    '//div[@class="a-section a-spacing-base"]//div[contains(text(),"Sold by")]/a/@href').extract_first()

                # 卖家名称
                # 卖家id
                # 发货方式
                if len(sellerATag) > 0:
                    sellerATagId = response.xpath('//*[@id ="merchant-info"]/a/@href').extract_first()
                    if len(sellerATag) == 2:
                        item['sellerid'] = datepat.findall(sellerATagId)[0]
                        item['sellername'] = sellerATag[0].strip().replace('\n', '')
                        item['shippingmethod'] = sellerATag[1]
                    elif len(sellerATag) == 1:
                        i = datepat.findall(sellerATagId)
                        if len(i) > 0:
                            item['sellerid'] = i[0]
                        else:
                            item['sellerid'] = 'Amazon'
                        name = response.xpath('//*[@id ="merchant-info"]/text()').extract_first()
                        if name != '' and "sold by Amazon.com" in name:
                            item['sellername'] = 'Amazon'
                            item['shippingmethod'] = 'Fulfilled by Amazon'
                        else:
                            item['sellername'] = sellerATag[0].strip().replace('\n', '')
                elif warehouse:
                    warehouse = warehouse.strip().replace('\n', '')
                    item['sellername'] = warehouse
                    item['sellerid'] = datepat.findall(warehouseId)[0]
                    item['shippingmethod'] = 'Fulfilled by Amazon'
                elif name:
                    if name and name.strip() != "":
                        if 'sold by' in name:
                            item['sellername'] = 'Amazon'
                            item['sellerid'] = 'Amazon'
                            item['shippingmethod'] = 'Fulfilled by Amazon'
                # 获取子分类的第一种方式
                subCategorysItem = []
                childBsrItem = []
                # 取分类和排名的4种方式
                subCategorys = response.xpath('//*[@id="SalesRank"]/text()').extract()
                subCategorysTD = response.xpath('//*[@id="SalesRank"]/td[@class="value"]/text()').extract()
                port = response.xpath('//th[contains(text(),"Best Sellers Rank")]/parent::*/td/span/span')
                subCategorys1 = response.xpath(
                    '//div[@id="wayfinding-breadcrumbs_feature_div"]/ul[@class="a-unordered-list a-horizontal a-size-small"]/li/span[@class="a-list-item"]')
                cgList = []  # [{name='分类1'，bsr='排名1'},{name='分类2'，bsr='排名2'}]
                if len(subCategorys) > 0:
                    mainSubCategory = ""
                    # 分类排名页面结构分为两部分    先取第一部分
                    for i in subCategorys:
                        mainSubCategory = mainSubCategory + i.replace("\n", "")
                    if " in " in mainSubCategory:
                        mainSubCategoryList = mainSubCategory.replace("()", "").strip().split(" in ")
                        cgDict = {}  # {name='分类1'，bsr='排名1'}
                        childBsrItem.append(mainSubCategoryList[0].strip().replace("#", "").replace(",", ""))
                        cgDict['bsr'] = mainSubCategoryList[0].strip().replace("#", "").replace(",", "")
                        subCategorysItem.append(mainSubCategoryList[1].strip())
                        cgDict['name'] = mainSubCategoryList[1].strip()
                        # 存入list 后面取主分类排名用
                        cgList.append(cgDict)
                    # 第二部分
                    _subCategorys = response.xpath(
                        '//*[@id="SalesRank"]/ul[@class="zg_hrsr"]/li[@class="zg_hrsr_item"]')
                    _subCategorysList = _subCategorys.xpath('string(.)').extract()
                    for sg in _subCategorysList:
                        sgs = sg.replace("\xa0", " ").split(" in ")
                        childBsrItem.append(sgs[0].strip().replace("#", "").replace(",", ""))
                        cgDict = {}  # {name='分类1'，bsr='排名1'}
                        cgDict['bsr'] = sgs[0].strip().replace("#", "").replace(",", "")
                        if " (" in sgs[1]:
                            subCategorysItem.append(sgs[1][0:sgs[1].rfind(" (")].strip())
                            cgDict['name'] = sgs[1][0:sgs[1].rfind(" (")].strip()
                        else:
                            subCategorysItem.append(sgs[1].strip())
                            cgDict['name'] = sgs[1].strip()
                        cgList.append(cgDict)
                elif len(subCategorysTD) > 0:
                    mainSubCategory = ""
                    for i in subCategorysTD:
                        mainSubCategory = mainSubCategory + i
                    if " in " in mainSubCategory:
                        mainSubCategoryList = mainSubCategory.replace("()", "").strip().split(" in ")
                        cgDict = {}  # {name='分类1'，bsr='排名1'}
                        childBsrItem.append(mainSubCategoryList[0].strip().replace("#", "").replace(",", ""))
                        cgDict['bsr'] = mainSubCategoryList[0].strip().replace("#", "").replace(",", "")
                        subCategorysItem.append(mainSubCategoryList[1].strip())
                        cgDict['name'] = mainSubCategoryList[1].strip()
                        cgList.append(cgDict)
                    _subCategorys = response.xpath(
                        '//*[@id="SalesRank"]/td/ul[@class="zg_hrsr"]/li[@class="zg_hrsr_item"]')
                    _subCategorysList = _subCategorys.xpath('string(.)').extract()
                    for sg in _subCategorysList:
                        sgs = sg.replace("\xa0", " ").split(" in ")
                        cgDict = {}  # {name='分类1'，bsr='排名1'}
                        cgDict['bsr'] = sgs[0].strip().replace("#", "").replace(",", "")
                        childBsrItem.append(sgs[0].strip().replace("#", "").replace(",", ""))
                        if " (" in sgs[1]:
                            subCategorysItem.append(sgs[1][0:sgs[1].rfind(" (")].strip())
                            cgDict['name'] = sgs[1][0:sgs[1].rfind(" (")].strip()
                        else:
                            cgDict['name'] = sgs[1].strip()
                            subCategorysItem.append(sgs[1].strip())
                        cgList.append(cgDict)
                elif port:
                    _categorys = port.xpath('string(.)').extract()
                    for c in _categorys:
                        categoryList = c.split(" in ")
                        childBsrItem.append(categoryList[0].strip().replace("#", "").replace(",", ""))
                        cgDict = {}  # {name='分类1'，bsr='排名1'}
                        cgDict['bsr'] = categoryList[0].strip().replace("#", "").replace(",", "")
                        if " (" in categoryList[1]:
                            subCategorysItem.append(categoryList[1][0:categoryList[1].rfind(" (")].strip())
                            cgDict['name'] = categoryList[1][0:categoryList[1].rfind(" (")].strip()
                        else:
                            subCategorysItem.append(categoryList[1].strip())
                            cgDict['name'] = categoryList[1].strip()
                        cgList.append(cgDict)
                elif subCategorys1:
                    category = ""
                    for s in subCategorys1:
                        category = category + s.xpath("./a/text()").extract_first() + ">"
                    category = category.replace(" ", "").replace("\n", "")[0:-1]
                    childBsrItem.append("")
                    subCategorysItem.append(category)
                    cgDict = {}  # {name='分类1'，bsr='排名1'}
                    cgDict['name'] = category
                    cgList.append(cgDict)
                if len(cgList) > 0:
                    for cgs in cgList:
                        if '>' not in cgs['name']:
                            if item['bsr'] is not '-1':
                                if int(cgs['bsr']) < int(item['bsr']):
                                    item['bsr'] = cgs['bsr']
                            else:
                                item['bsr'] = cgs['bsr']
                            item['category'] = cgs['name']
                            break
                        else:
                            ##分类
                            categorys = response.xpath(
                                '//*[@id="wayfinding-breadcrumbs_feature_div"]/ul/li/span/a[@class="a-link-normal a-color-tertiary"]/text()').extract()
                            if len(categorys) > 0:
                                for ca in categorys:
                                    item['category'] = ca.strip().replace("\n", "")
                                    break
                                break
                item['subcategory'] = subCategorysItem
                item['childBsr'] = childBsrItem
                # 黄金购物车信息
                olp = response.xpath(
                    '//div[@id="olp_feature_div"]//a/@href|//div[@id="moreBuyingChoices_feature_div"]//div[@class="a-box"]//a/@href').extract_first()
                # 跟卖数量
                sellerCount = response.xpath(
                    '//div[@id="olp_feature_div"]//a/text()|//div[@id="moreBuyingChoices_feature_div"]//div[@class="a-box"]//a/text()').extract_first()
                if sellerCount:
                    sellerCount = sellerCount[sellerCount.find("(") + 1:sellerCount.find(")")]
                    sellerCount = re.findall(r"\d+\.?\d*", sellerCount)[0]
                    item['sellerCount'] = sellerCount
                # logging.info(item)
                # 跟卖页面
                if olp:
                    list = []
                    yield scrapy.Request(url="https://www.amazon.com" + olp, callback=self.buyBoxinfo,
                                         meta={'list': list, 'item': item})
                else:
                    yield item
        except Exception as e:
            # raise  e
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

    def buyBoxinfo(self, response):
        try:
            list = response.meta['list']
            item = response.meta['item']
            olpOfferList = response.xpath('//div[@class="a-row a-spacing-mini olpOffer"]')
            for rows in olpOfferList:
                buyBoxdict = {}
                # 发货地点
                shipAdress = rows.xpath('.//span[contains(text(),"Ships from")]/text()').extract_first()
                if shipAdress:
                    buyBoxdict['shipAdress'] = shipAdress
                else:
                    buyBoxdict['shipAdress'] = ""
                # 卖家名称 id
                sellerId = rows.xpath(
                    './/h3[@class="a-spacing-none olpSellerName"]/span[@class="a-size-medium a-text-bold"]//a/@href').extract_first()
                sellerName = rows.xpath(
                    './/h3[@class="a-spacing-none olpSellerName"]/span[@class="a-size-medium a-text-bold"]//a/text()').extract_first()
                datepat = re.compile('.*seller=(\w*)\w*')
                if sellerId:
                    buyBoxdict['sellerid'] = datepat.findall(sellerId)[0].strip()
                    buyBoxdict['sellerName'] = sellerName
                else:
                    buyBoxdict['sellerid'] = "Amazon"
                    buyBoxdict['sellerName'] = "Amazon"
                list.append(buyBoxdict)
            nextPageUrl = response.xpath(
                '//div[@class="a-text-center a-spacing-large"]//li[@class="a-last"]/a/@href').extract_first()
            if nextPageUrl:
                yield scrapy.Request(url="https://www.amazon.com" + nextPageUrl, callback=self.buyBoxinfo,
                                     meta={'list': list, 'item': item})
            else:
                for l in list:
                    buyBoxSellerId = l['sellerid']
                    baseSellerId = item['sellerid']
                    # 在跟卖页面取得商品发货地址
                    if buyBoxSellerId and baseSellerId:
                        if baseSellerId == buyBoxSellerId:
                            item['shipAdress'] = l['shipAdress'].replace("\n", "").strip()
                    else:
                        item['shipAdress'] = ''
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

    def getReview(self, response, xpath, item):
        if xpath is not None:
            reviews = xpath.split(' ')
            if reviews:
                item['reviewsnum'] = reviews[0].replace(',', '')
            else:
                item['reviewsnum'] = ""
            starts = response.xpath('//*[@id="reviewSummary"]/div[2]/span/a/span/text()').extract_first()
            if starts:
                item['stars'] = starts.split(' ')[0]
            # 5星评论
            fstarList = ['//*[@id="histogramTable"]//tr[1]/td[3]/a/text()',
                         '//*[@id="histogramTable"]//tr[1]/td[3]/span[1]/text()']
            item = self.Xparse(response, fstarList, 'star5', item)

            # 4星评论
            fourStarList = ['//*[@id="histogramTable"]//tr[2]/td[3]/span[1]/text()',
                            '//*[@id="histogramTable"]//tr[2]/td[3]/a/text()']
            item = self.Xparse(response, fourStarList, 'star4', item)

            # 3星评论
            threeStarList = ['//*[@id="histogramTable"]/tr[3]/td[3]/span[1]/text()',
                             '//*[@id="histogramTable"]/tr[3]/td[3]/a/text()']
            item = self.Xparse(response, threeStarList, 'star3', item)

            # 2星评论
            twoStarList = ['//*[@id="histogramTable"]//tr[4]/td[3]/span[1]/text()',
                           '//*[@id="histogramTable"]//tr[4]/td[3]/a/text()']
            item = self.Xparse(response, twoStarList, 'star2', item)

            # 1星评论
            oneStarList = ['//*[@id="histogramTable"]/tr[5]/td[3]/span[1]/text()',
                           '//*[@id="histogramTable"]/tr[5]/td[3]/a/text()']
            item = self.Xparse(response, oneStarList, 'star1', item)

        return item

    def getQuestion(self, question, item):

        if question is not None:
            item['questionsnum'] = question.lstrip().split(' ')[0]
        return item

    def Xparse(self, response, xpath, key, item):
        for i in xpath:
            val = response.xpath(i).extract_first()
            if val:
                if key is "price":
                    val = val.replace(',', '')
                    val = val.replace(' ', '')
                    val = val.replace('\n', '')
                    val = val.replace('\t', '')
                    priceList = re.findall(r"\d+\.?\d*", val)
                    listCount = len(priceList)
                    if listCount > 1:
                        for p in priceList:
                            item[key] = p
                    elif listCount > 0:
                        item[key] = priceList[0]
                    if val is not '' and not None:
                        item['cur'] = re.findall(r"\D", val)[0]
                else:
                    item[key] = val.strip()
                return item
        return item

    def Yparse(self, response, xpath, key, item):
        for i in xpath:
            valList = response.xpath(i)
            lens = len(valList)
            flag = 0 if lens == 0 else 1
            num = 1
            for j in range(lens):
                val = valList[j].extract().strip()
                if len(val) and not val == '\x9b':
                    item[key] = item.get(key, '') + str(num) + ':' + val + '\n'
                    num = num + 1
            if flag:
                item[key] = ""
                return item
        return item

    def Iparse(self, response, xpath, key, item):
        for i in xpath:
            valList = response.xpath(i)
            lens = len(valList)
            flag = 0 if lens == 0 else 1
            num = 1
            for j in range(lens):
                val = valList[j].extract().strip()
                if len(val) and not val == '\x9b':
                    if val.find('.jpg') > 0:
                        item[key] = item.get(key, '') + str(num) + ':' + val + '\n'
                        num = num + 1
            if flag:
                return item
        return item

    def Zparse(self, response, xpath, key, item):

        ruleList = [
            ['./b/text()', './text()'],
            ['./th/text()', './td/text()'],
            ['./td[1]/text()', './td[2]/text()'],
        ]
        innerItem = {}
        for i in xpath:
            valList = response.xpath(i[0])
            lens = len(valList)
            flag = 0 if lens == 0 else 1
            for j in range(len(valList)):
                try:
                    k = valList[j].xpath(ruleList[i[1]][0]).extract_first().replace(' ', '').strip()
                    v = valList[j].xpath(ruleList[i[1]][1]).extract_first().strip()
                    if (k and v):
                        if k.find("Dimensions") > -1:
                            innerItem["dimensions"] = v.replace("(", "")
                        elif k.find("Weight") > -1:
                            innerItem["weight"] = v.replace("(", "")
                except:
                    continue
            if innerItem:
                item[key] = innerItem
            if flag:
                return item
        return item

    def get_value(self, response, xpath, key, item):
        for i in xpath:
            val = response.xpath(i).extract_first()
            if val:
                hjson = json.loads(val)
                if key in hjson.keys():
                    item[key] = hjson[key]
                    return item
        return item

