#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from frontera.contrib.scrapy.schedulers.frontier import FronteraScheduler
from scrapy import Request

logger = logging.getLogger(__name__)

class CustomFronteraScheduler(FronteraScheduler):
    pass
    # def process_spider_output(self, response, result, spider):
    #     links = []
    #     for element in result:
    #         if isinstance(element, Request):
    #             links.append(element)
    #         else:
    #             yield element
    #     frontier_request = response.meta.get(b'frontier_request','')
    #     self.frontier.page_crawled(response)  # removed frontier part from .meta
    #     # putting it back, to persist .meta from original request
    #     if frontier_request:
    #         response.meta[b'frontier_request'] = frontier_request
    #     self.frontier.links_extracted(response.request, links)
    #     self.stats_manager.add_crawled_page(response.status, len(links))


