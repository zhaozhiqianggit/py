#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time
from influxdb import InfluxDBClient
from kafka import KafkaProducer
from scrapy import signals
from scrapy.exceptions import NotConfigured
from twisted.internet import task
import msgpack
from amazon.dtrobot import DtalkRobot

__author__ = "sunwei"
import logging

from twisted.internet import task

from scrapy.exceptions import NotConfigured
from scrapy import signals


logger = logging.getLogger(__name__)


class InfluxStats(object):
    @classmethod
    def from_crawler(cls, crawler):
        influxdb_host = crawler.settings.get('INFLUXDB_HOST')
        influxdb_port = crawler.settings.getint('INFLUXDB_PORT')
        influxdb_username = crawler.settings.get('INFLUXDB_USERNAME')
        influxdb_password = crawler.settings.get('INFLUXDB_PASSWORD')
        influxdb_database = crawler.settings.get('INFLUXDB_DATABASE')
        influxdb_interval = crawler.settings.getint('INFLUXDB_INTERVAL')

        logger.info("host:{}, port:{}, username:{}, password:{}, database:{}, interval:{}".format(
            influxdb_host, influxdb_port, influxdb_username, influxdb_password, influxdb_database, influxdb_interval
        ))
        logger.info("spider_partition_id: {}".format(crawler.settings.get('SPIDER_PARTITION_ID')))

        o = cls(crawler.settings.get('SPIDER_PARTITION_ID'),
                crawler.stats,
                influxdb_host,
                influxdb_port,
                influxdb_username,
                influxdb_password,
                influxdb_database,
                influxdb_interval)

        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def __init__(self, id, stats, host, port, username, password, database, interval):
        self.id = id
        self.stats = stats
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.interval = interval
        self.multipier = 60.0 / self.interval
        self.task = None
        self.influx_client = InfluxDBClient(host=self.host,
                                            port=self.port,
                                            username=self.username,
                                            password=self.password,
                                            database=self.database)
        self.influx_client.create_database(self.database)

    def spider_opened(self, spider):
        self.pagesprev = 0
        self.itemsprev = 0
        self.task = task.LoopingCall(self.log, spider)
        self.task.start(self.interval)

    def log(self, spider):
        items = self.stats.get_value('item_scraped_count', 0)
        pages = self.stats.get_value('response_received_count', 0)
        irate = (items - self.itemsprev) * self.multipier
        prate = (pages - self.pagesprev) * self.multipier
        self.pagesprev, self.itemsprev = pages, items
        self.influx_client.write_points([
            {
                "measurement": "status",
                "tags": {
                    "id": self.id
                },
                # "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime()),
                "fields": {
                    "items": items,
                    "pages": pages,
                    "irate": irate,
                    "prate": prate
                }
            }
        ])

    def spider_closed(self, spider):
        if self.task and self.task.running:
            self.task.stop()

class ErrorLogStats(object):
    webhook = "" #钉钉地址
    def __init__(self, stats,webhook, producer,topic,interval=60.0):
        self.stats = stats
        self.interval = interval
        self.webhook=webhook
        self.task = None
        self.producer = producer
        self.topic = topic

    @classmethod
    def from_crawler(cls, crawler):
        interval = crawler.settings.getfloat('ERROR_LOGSTATS_INTERVAL')
        webhook = crawler.settings.get('WEBHOOK')
        if not webhook:
            raise NotConfigured

        if not interval:
            raise NotConfigured

        k_hosts = crawler.settings.get('SEED_OUTPUT_KAFKA_LOCATION', ['localhost:9092'])
        topic = crawler.settings.get('ERROR_OUTPUT_KAFKA_TOPIC', 'error-seeds')
        producer = KafkaProducer(bootstrap_servers=k_hosts,
                                 retries=5,
                                 value_serializer=lambda m: json.dumps(m).encode('utf-8'))
        o = cls(crawler.stats,webhook,producer,topic,interval)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.task = task.LoopingCall(self.log, spider)
        self.task.start(self.interval)


    def log(self, spider):
        errors=spider.crawler.stats.get_value('errors', [])
        error_len = len(errors)
        if error_len>0 :
            for x in range(error_len):
                error=errors.pop()
                self.producer.send(self.topic, error)
        error_count=spider.crawler.stats.get_value('error_count', 0)

        error_total_count=spider.crawler.stats.get_value('error_total_count', 0)

        if error_count//100>1:

            error_msg={}
            error_msg['msg']='spider has errors'
            error_msg['error_total_count']=error_total_count
            robot = DtalkRobot(self.webhook)
            robot.sendText(str(error_msg))
            logger.info('error msg send to dingTalk:'+str(error_msg))

            spider.crawler.stats.set_value('error_total_count', error_total_count + error_count)
            spider.crawler.stats.set_value('error_count', 0)

    def spider_closed(self, spider, reason):
        if self.task and self.task.running:
            self.task.stop()
