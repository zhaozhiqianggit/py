# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

import msgpack
from kafka import KafkaProducer
import logging

from scrapy.exceptions import DropItem, NotConfigured

logger = logging.getLogger(__name__)
from scrapy.conf import settings
import pymongo

class AmazonPipeline(object):
    def process_item(self, item, spider):
        return item

class FilterEmptyItemPipeline(object):
    def process_item(self, item, spider):
        if len(item):
            return item
        raise DropItem('Item is empty, drop it')


class KafkaPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        k_hosts = crawler.settings.get('ITEM_OUTPUT_KAFKA_LOCATION')
        topic = crawler.settings.get('ITEM_OUTPUT_KAFKA_TOPIC')
        if not k_hosts or not topic:
            logger.warning('ITEM_OUTPUT_KAFKA_LOCATION or ITEM_OUTPUT_KAFKA_TOPIC is null , raise notconfigured')
            raise NotConfigured
        producer = KafkaProducer(bootstrap_servers=k_hosts,
                                 retries=5,
                                 value_serializer=lambda m: json.dumps(m).encode('utf-8'))
        return cls(producer, topic)

    def __init__(self, producer, topic):
        self.producer = producer
        self.topic = topic

    def process_item(self, item, spider):
        # logger.info('KafkaPipeline-> process_item')
        # 异步
        self.producer.send(self.topic, item)
        # 同步
        # send_future = self.producer.send(self.topic, item)
        # from kafka.errors import KafkaError
        # try:
        #     record_metadata = send_future.get(timeout=10)
        # except KafkaError:
        #     pass
        return item


class KafkaPipelineBSRSimulateSeed(object):
    @classmethod
    def from_crawler(cls, crawler):
        k_hosts = crawler.settings.get('ITEM_OUTPUT_KAFKA_LOCATION_SIMULATECART_SEED')
        topic = crawler.settings.get('ITEM_OUTPUT_KAFKA_TOPIC_SIMULATECART_SEED')
        if not k_hosts or not topic:
            logger.warning('ITEM_OUTPUT_KAFKA_LOCATION_SIMULATECART_SEED or topic is null , raise notconfigured')
            raise NotConfigured
        producer = KafkaProducer(bootstrap_servers=k_hosts,
                                 retries=5,
                                 value_serializer=lambda m: json.dumps(m).encode('utf-8'))
        return cls(producer, topic)

    def __init__(self, producer, topic):
        self.producer = producer
        self.topic = topic

    def process_item(self, item, spider):
        asin = item.get('asin')
        if not asin:
            raise DropItem(f"item's asin is invalid, asin:{asin}")
        self.producer.send(self.topic, ['a', asin])
        return item


class KafkaSimulateCartPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        k_hosts = crawler.settings.get('SIMULATECART_ITEM_OUTPUT_KAFKA_LOCATION')
        topic = crawler.settings.get('SIMULATECART_ITEM_OUTPUT_KAFKA_TOPIC')
        if not k_hosts or not topic:
            logger.warning('SIMULATECART_ITEM_OUTPUT_KAFKA_LOCATION or topic is null, raise notconfigured')
            raise NotConfigured
        producer = KafkaProducer(bootstrap_servers=k_hosts,
                                 retries=5,
                                 value_serializer=lambda m: json.dumps(m).encode('utf-8'))
        return cls(producer, topic)

    def __init__(self, producer, topic):
        self.producer = producer
        self.topic = topic

    def process_item(self, item, spider):
        logger.warning('KafkaSimulateCartPipeline-> process_item')
        # 异步
        self.producer.send(self.topic, item)
        # 同步
        # send_future = self.producer.send(self.topic, item)
        # from kafka.errors import KafkaError
        # try:
        #     record_metadata = send_future.get(timeout=10)
        # except KafkaError:
        #     pass
        return item


class KafkaSimulateCartPipelineBSR(object):
    '''BSR的模拟下单'''
    @classmethod
    def from_crawler(cls, crawler):
        k_hosts = crawler.settings.get('SIMULATECART_ITEM_OUTPUT_KAFKA_LOCATION_BSR')
        topic = crawler.settings.get('SIMULATECART_ITEM_OUTPUT_KAFKA_TOPIC_BSR')
        if not k_hosts or not topic:
            logger.warning('SIMULATECART_ITEM_OUTPUT_KAFKA_LOCATION_BSR or topic is null, raise notconfigured')
            raise NotConfigured
        producer = KafkaProducer(bootstrap_servers=k_hosts,
                                 retries=5,
                                 value_serializer=lambda m: json.dumps(m).encode('utf-8'))
        return cls(producer, topic)

    def __init__(self, producer, topic):
        self.producer = producer
        self.topic = topic

    def process_item(self, item, spider):
        logger.warning('KafkaSimulateCartPipelineBSR-> process_item')
        self.producer.send(self.topic, item)
        return item


class KafkaKeywordPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        k_hosts = crawler.settings.get('KEYWORD_OUTPUT_KAFKA_LOCATION')
        topic = crawler.settings.get('KEYWORD_OUTPUT_KAFKA_TOPIC')
        if not k_hosts or not topic:
            logger.warning('KEYWORD_OUTPUT_KAFKA_LOCATION or topic is null, raise notconfigured')
            raise NotConfigured
        producer = KafkaProducer(bootstrap_servers=k_hosts,
                                 retries=5,
                                 value_serializer=lambda m: json.dumps(m).encode('utf-8'))
        return cls(producer, topic)

    def __init__(self, producer, topic):
        self.producer = producer
        self.topic = topic

    def process_item(self, item, spider):
        self.producer.send(self.topic, item)
        return item

class KafkaCompetingPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        k_hosts = crawler.settings.get('COMPETING_OUTPUT_KAFKA_LOCATION')
        topic = crawler.settings.get('COMPETING_OUTPUT_KAFKA_TOPIC')
        if not k_hosts or not topic:
            logger.warning('COMPETING_OUTPUT_KAFKA_LOCATION or topic is null, raise notconfigured')
            raise NotConfigured
        producer = KafkaProducer(bootstrap_servers=k_hosts,
                                 retries=5,
                                 value_serializer=lambda m: json.dumps(m).encode('utf-8'))
        return cls(producer, topic)

    def __init__(self, producer, topic):
        self.producer = producer
        self.topic = topic

    def process_item(self, item, spider):
        self.producer.send(self.topic, item)
        return item


class KafkaCategoryPipeline(object):
    """用来生成三级目录的, 现在直接从mysql拿, 所以这个暂时不用了
    """
    @classmethod
    def from_crawler(cls, crawler):
        k_hosts = crawler.settings.get('CATEGORY_SEED_KAFKA_LOCATION')
        topic = crawler.settings.get('CATEGORY_SEED_KAFKA_TOPIC')
        if not k_hosts or not topic:
            logger.warning('CATEGORY_SEED_KAFKA_LOCATION or topic is null, raise notconfigured')
            raise NotConfigured
        producer = KafkaProducer(bootstrap_servers=k_hosts,
                                 retries=5,
                                 value_serializer=msgpack.dumps)
        return cls(producer, topic)

    def __init__(self, producer, topic):
        self.producer = producer
        self.topic = topic

    def process_item(self, item, spider):
        logger.info('KafkaCategoryPipeline -> process_item %s' % item.get('href', "default"))
        if item.get('href', None):
            url = item.get('href')
            self.producer.send(self.topic, ['a', url, '0'])
        return item


class KafkaSeedPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        k_hosts = crawler.settings.get('SEED_OUTPUT_KAFKA_LOCATION')
        topic = crawler.settings.get('SEED_OUTPUT_KAFKA_TOPIC')
        if not k_hosts or not topic:
            logger.warning('SEED_OUTPUT_KAFKA_LOCATION or topic is null, raise notconfigured')
            raise NotConfigured
        producer = KafkaProducer(bootstrap_servers=k_hosts,
                                 retries=5,
                                 value_serializer=msgpack.dumps)
        return cls(producer, topic)

    def __init__(self, producer, topic):
        self.producer = producer
        self.topic = topic

    def process_item(self, item, spider):
        if item.get('TSCProductUrls', None):
            urls = item.get('TSCProductUrls')
            logger.info(f'TSC产出seed:{urls}')
            for url in urls:
                self.producer.send(self.topic, ['a', url, '0'])
        return item


class MongoPipeline(object):
    def __init__(self):
        db = pymongo.MongoClient(host=settings['MONGODB_HOST'],
                                 port=settings['MONGODB_PORT'])[settings['MONGODB_DBNAME']]
        self.post = db[settings['MONGODB_DOCNAME']]

    def process_item(self, item, spider):
        Info = dict(item)
        self.post.insert(Info)
        return item
