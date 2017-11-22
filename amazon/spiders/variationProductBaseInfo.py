
import scrapy
import json
import re
import logging
from scrapy import Spider
import time
class BaseInfo(Spider):

    name = 'variationProductBaseInfo'
    start_urls = [
        #"https://www.amazon.com/dp/B01E3SNO1G"   # Home & Kitchen › Furniture › Bedroom Furniture › Mattresses & Box Springs › Mattresses
        # "https://www.amazon.com/gp/product/B01AVSHQAW" # Home & Kitchen › Bedding › Sheets & Pillowcases › Sheet & Pillowcase Sets
        # "https://www.amazon.com/dp/B01BH83OOM"   #Echo & Alexa > Amazon Echo
        # "https://www.amazon.com/dp/B01BH83OOM" # Echo & Alexa > Amazon Tap
        # "https://www.amazon.com/dp/032119991X"  # Echo & Alexa > Amazon Tap
        # "https://www.amazon.com/dp/B001ICYB2M"   #Appliances
        # "https://www.amazon.com/dp/B01ICSIUQ2"  # Arts, Crafts & Sewing
        "https://www.amazon.com/dp/B00JKSXD02"  # Automotive Parts & Accessories

    ]
    def parse(self, response):
        variation = response.xpath('//script[contains(text(),"asinVariationValues")]/text()').extract_first()
        if variation:
            print('多规格商品')
            #amazon多规格商品信息写在了js里，下面是通过js截取，取得规格商品的asin码
            variation = variation[(variation.find('"asinVariationValues" :') + 24):variation.rfind(
                '"dimensionValuesData" :') - 14]  # 去掉首尾的圆括号前后部分
            dicts = json.loads(variation)
            print(dicts)
            for i in dicts:
                logging.info("=++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                logging.info(i)
                yield scrapy.Request(url="https://www.amazon.com/dp/product/" + i, callback=self.singleProduct)
        else:
            print('单规格商品')
            self.singleProduct(response)
    def singleProduct(self, response):
        item = {}
        # asin
        asinList = ["//div[@id='tell-a-friend']//span[@class='a-declarative']/@data-a-modal"]
        item = self.get_marketplace(response, asinList, 'asin', item)
        # 商品详情url
        item['url'] = "https://www.amazon.com/dp/%s" % item.get('asin')
        # parent_asin
        parent_asin_b = response.xpath("//div[@id='tell-a-friend']/@data-dest").extract_first()
        if parent_asin_b:
            index = parent_asin_b.find('parentASIN')
            item['parentasin'] = parent_asin_b[index + 11:index + 21]
        else:
            item['parentasin'] = "0000000000"
        # 抓取时间
        item['scrapyTime'] =  int(time.time())
        # marketplace
        marketplaceList = ['//div[@id="session-sims-feature"]/div/@data-p13n-global',
                           '//div[@id="sims-fbt-container"]/@data-p13n-global']
        item = self.get_marketplace(response, marketplaceList, 'marketplace', item)
        # marketplaceId
        item = self.get_marketplace(response, marketplaceList, 'marketplaceId', item)
        # 评论
        review = response.xpath('//*[@id="acrCustomerReviewText"]/text()').extract_first()
        item = self.getReview(response, review, item)
        question = response.xpath('//*[@id= "askATFLink"]/span/text()').extract_first()
        item = self.getQuestion(question, item)
        # 图片
        imgStr = response.xpath('//script[contains(text(),"colorImages")]/text()').extract_first()
        imgStr1 = response.xpath('//div[@id="mainImageContainer"]/img/@src').extract()
        # 品牌
        brand = response.xpath('//*[@id="brand"]/text()').extract_first()
        if brand:
            item['brand'] = brand.strip()
        else:
            item['brand'] = ''
        #竞品标识
        item['flag'] = '01'
        imglist = []
        if imgStr :
            imgStr = imgStr[(imgStr.find('[{')):imgStr.rfind('}]') + 2]  #
            dict = json.loads(imgStr)
            for i in dict:
                if i["large"]:
                    imglist.append(i["large"])
            item["imgurl"] = imglist
        elif imgStr1:
            item["imgurl"] = imgStr1

        # 标题
        tileList = ['//*[@id="ProductTitle"]/text()', '//*[@id="productTitle"]/text()']
        item = self.Xparse(response, tileList, 'asinname', item)
        # 价格
        priceList = ['//*[@id="priceblock_ourprice"]/text()', '//*[@id="priceblock_dealprice"]/text()',
                     '//*[@id="priceblock_saleprice"]/text()']
        item = self.Xparse(response, priceList, 'price', item)
        # 描述
        # description_headList = ['//*[@id="feature-bullets"]//span/text()']
        # item = self.Yparse(response, description_headList, 'description_head', item)
        #
        # descriptionList = ['//*[@id="productDescription_feature_div"]/*[@id="productDescription"]//p/text()']
        # item = self.Yparse(response, descriptionList, 'ptiondesc', item)
        # 商品简介 要点
        bulletpoints = response.xpath('//div[@id="feature-bullets"]//li/span[@class="a-list-item"]')
        bulletpointsStr = ""
        for point in bulletpoints:
            bulletpointsStr  =  bulletpointsStr + point.xpath('./text()').extract_first().strip()+"\n"
        item['bulletpoints'] = bulletpointsStr
        # 变体组合名称
        variationname = response.xpath('//form[@id="twister"]//div[contains(@id,"variation")]')
        variationnameStr = ""
        for variation in variationname:
            v = variation.xpath('.//div/label/text()').extract_first()
            if v :
                v = v.replace("\n", "").replace(' ', '')
            else:
                v=""
            vStr = variation.xpath('./div/span/text()').extract_first()
            if vStr:
                vStr = vStr.replace("\n", "").replace(' ', '')
            else:
                vStr = ""
            variationnameStr  =  variationnameStr + v + vStr + "   "
        item['variationname'] = variationnameStr
        #规格
        specList = [
            ['//*[@id="productDetailsTable"]//li', 0],
            ['//*[@id="productDetails_techSpec_section_1"]//tr|//*[@id="productDetails_techSpec_section_2"]//tr', 1],
            ['//*[@id="technical-details-table"]//tr', 2],
            ['//*[@id="productDetails_detailBullets_sections1"]//tr', 1]
            # ['//*[@id="detailBullets_feature_div"]//tr', 1]
        ]
        item = self.Zparse(response, specList, 'spec', item)
        # 刊登时间
        timeStr = response.xpath('//tr[@class="date-first-available"]/td[@class="value"]/text()').extract_first()
        if timeStr is not None:
            item['publishedtime'] = timeStr.strip()
        else:
            item['publishedtime'] = ''
        # GMT_FORMAT = '%B %d, %Y'
        # item['publishedtime'] = datetime.datetime.strptime(time.strip(), GMT_FORMAT)

        sellerATag = response.xpath('//*[@id ="merchant-info"]/a/text()').extract()
        datepat = re.compile('.*seller=(\w*)\w*')

        # 卖家名称
        # 卖家id
        # 发货方式
        if len(sellerATag) > 0:
            sellerATagId = response.xpath('//*[@id ="merchant-info"]/a/@href').extract_first()

            if len(sellerATag) == 2:
                item['sellerid'] = datepat.findall(sellerATagId)[0]
                item['sellername'] = sellerATag[0]
                item['shippingmethod'] = sellerATag[1]
            elif len(sellerATag) == 1:
                i = datepat.findall(sellerATagId)
                if len(i) > 0:
                    item['sellerid'] = i
                else:
                    item['sellerid'] = 'amazon.com'
                name = response.xpath('//*[@id ="merchant-info"]/text()').extract_first()
                if name != '' and "sold by Amazon.com " in name:
                    item['sellername'] = 'amazon.com'
                else:
                    item['sellername'] = sellerATag[0]
                item['shippingmethod'] = 'seller'
        else:
            name = response.xpath('//*[@id ="merchant-info"]/text()').extract_first()

            if name:
                sellername = name.strip().replace('sold by', '##').split('##')[1].strip()
                item['sellername'] = sellername
                item['sellerid'] = 'amazon.com'
                item['shippingmethod'] = 'FBA'
            else:
                item['sellername'] = ''
                item['sellerid'] = ''
                item['shippingmethod'] = ''
        ##分类
        categorys = response.xpath(
            '//*[@id="wayfinding-breadcrumbs_feature_div"]/ul/li/span/a[@class="a-link-normal a-color-tertiary"]/text()').extract()
        if len(categorys) > 0:
            category = categorys[-1].strip()
        else:
            category = ''
        item['category'] = category
        # 获取子分类的第一种方式
        subCategorysItem = []
        childBsrItem = []
        subCategorys = response.xpath('//*[@id="SalesRank"]/text()').extract()
        if len(subCategorys) > 0:
            mainSubCategory = ""
            for i in subCategorys:
                mainSubCategory = mainSubCategory + i

            mainSubCategoryList = mainSubCategory.replace("()", "").strip().split(" in ")

            childBsrItem.append(mainSubCategoryList[0].strip())

            subCategorysItem.append(mainSubCategoryList[1].strip())
            _subCategorys = response.xpath('//*[@id="SalesRank"]/ul[@class="zg_hrsr"]/li[@class="zg_hrsr_item"]')

            _subCategorysList = _subCategorys.xpath('string(.)').extract()
            for sg in _subCategorysList:
                # logging.info(sg)
                sgs = sg.replace("\xa0", " ").split(" in ")
                childBsrItem.append(sgs[0].strip())

                subCategorysItem.append(sgs[1].strip())

        else:
            # 第二种取分类方式
            port = response.xpath('//th[contains(text(),"Best Sellers Rank")]/parent::*/td/span/span')
            _categorys = port.xpath('string(.)').extract()
            for c in _categorys:
                categoryList = c.split(" in ")
                childBsrItem.append(categoryList[0].strip())

                subCategorysItem.append(categoryList[1].strip())
        item['subcategory'] = subCategorysItem
        item['chilbsr'] = childBsrItem
        # 黄金购物车信息
        olp = response.xpath('//div[@id="olp_feature_div"]//a/@href').extract_first()
        if olp:
            print('有黄金购物车')
            list = []
            yield scrapy.Request(url="https://www.amazon.com" + olp, callback=self.buyBoxinfo, meta={'list': list,'item':item})
        else:
            logging.info(item)
            print('无黄金购物车')
    def buyBoxinfo(self, response):
        list = response.meta['list']
        item = response.meta['item']
        olpOfferList = response.xpath('//div[@class="a-row a-spacing-mini olpOffer"]')
        isfrist = 1
        for rows in olpOfferList:
            buyBoxdict = {}
            if isfrist is 1:
                buyBoxdict['isBuyBox'] = "01"
            else:
                buyBoxdict['isBuyBox'] = "02"
            # 价格
            price = rows.xpath(
                './/span[@class="a-size-large a-color-price olpOfferPrice a-text-bold"]/text()').extract_first()
            buyBoxdict['price'] = price.replace(' ', '')
            # 发货地点
            shipAdress = rows.xpath('.//span[contains(text(),"Ships from")]/text()').extract_first()
            if shipAdress:
                buyBoxdict['shipAdress'] = shipAdress
            else:
                buyBoxdict['shipAdress'] = ""
            # condition
            condition = rows.xpath('.//span[@class="a-size-medium olpCondition a-text-bold"]/text()').extract_first()
            buyBoxdict['condition'] = condition.strip()
            # 卖家名称 id
            sellerId = rows.xpath(
                './/h3[@class="a-spacing-none olpSellerName"]/span[@class="a-size-medium a-text-bold"]//a/@href').extract_first()
            sellerName = rows.xpath(
                './/h3[@class="a-spacing-none olpSellerName"]/span[@class="a-size-medium a-text-bold"]//a/text()').extract_first()

            datepat = re.compile('.*seller=(\w*)\w*')
            if sellerId:
                buyBoxdict['sellerId'] = datepat.findall(sellerId)[0].strip()
                buyBoxdict['sellerName'] = sellerName
            else:
                buyBoxdict['sellerId'] = "Amazon"
                buyBoxdict['sellerName'] = "Amazon"
            # 卖家评分
            star = rows.xpath('.//p[@class="a-spacing-small"]//span[@class="a-icon-alt"]/text()').extract_first()
            if star:
                buyBoxdict['star'] = star
            else:
                buyBoxdict['star'] = ""
            list.append(buyBoxdict)
            isfrist += 1
        nextPageUrl = response.xpath(
            '//div[@class="a-text-center a-spacing-large"]//li[@class="a-last"]/a/@href').extract_first()
        if nextPageUrl:
            #scrapy.Request(url="https://www.amazon.com" + nextPageUrl, callback=self.buyBoxinfo,meta={'list': list, 'item': item})
            yield scrapy.Request(url="https://www.amazon.com" + nextPageUrl, callback=self.buyBoxinfo,meta={'list': list, 'item': item})
        else:
            item['buyBox'] = list
            logging.info(item)
            #return item







    def getReview(self, response, xpath, item):
        if xpath is None:
            # 评论数量
            item['reviewsnum'] = 0
            # 评论评分
            item['stars'] = 0
            # 5星评论百分比
            item['star5'] = 0
            item['star4'] = 0
            item['star3'] = 0
            item['star2'] = 0
            item['star1'] = 0
        else:
            reviews = xpath.split(' ')
            item['reviewsnum'] = reviews[0]
            starts = response.xpath('//*[@id="reviewSummary"]/div[2]/span/a/span/text()').extract_first()
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

        if question is None:
            item['questionsnum'] = 0
        else:

            item['questionsnum'] = question.lstrip().split(' ')[0]

        return item

    def Xparse(self, response, xpath, key, item):
        for i in xpath:
            val = response.xpath(i).extract_first()
            if val:
                if key is "price":
                    val = val.replace(',', '')
                    priceList = re.findall(r"\d+\.?\d*", val)
                    listCount = len(priceList)
                    if listCount > 1:
                        pStr = ""
                        for p in priceList:
                            pStr = pStr + p + "-"
                    else:
                        item[key] = priceList[0]
                    item[key] = pStr
                    item['cur'] = re.findall(r"\D", val)[0]
                else:
                    item[key] = val.strip()
                    return item
            else:
                item[key] = ""
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
                        innerItem[k] = v
                except:
                    continue
            if innerItem:
                item[key] = innerItem
            if flag:
                return item
        return item

    def get_marketplace(self, response, xpath, key, item):
        for i in xpath:
            val = response.xpath(i).extract_first()
            if val:
                hjson = json.loads(val)
                item[key] = hjson[key]
                return item
        return item


