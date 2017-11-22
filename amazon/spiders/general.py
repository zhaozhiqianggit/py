# -*- coding: utf-8 -*-
import scrapy


class GeneralSpider(scrapy.Spider):
    name = 'general'

    def parse(self, response):
        self.logger.info(f"开始处理: {response.url}")
        self.logger.info(f"meta:{response.meta}")
