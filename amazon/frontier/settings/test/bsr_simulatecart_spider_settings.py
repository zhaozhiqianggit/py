# -*- coding: utf-8 -*-
from frontera.settings.default_settings import MIDDLEWARES

MAX_NEXT_REQUESTS = 256
DELAY_ON_EMPTY = 5.0

MIDDLEWARES.extend([
    'frontera.contrib.middlewares.domain.DomainMiddleware',
    'frontera.contrib.middlewares.fingerprint.DomainFingerprintMiddleware',
])

#--------------------------------------------------------
# Crawl frontier backend
#--------------------------------------------------------
BACKEND = 'frontera.contrib.backends.remote.messagebus.MessageBusBackend'
SPIDER_FEED_PARTITIONS = 3
SPIDER_FEED_TOPIC = 'frontier-todo-simulatecart-bsr'
SPIDER_LOG_TOPIC = 'frontier-done-simulatecart-bsr'
SCORING_LOG_TOPIC = 'frontier-score-simulatecart-bsr'
MESSAGE_BUS = 'frontera.contrib.messagebus.kafkabus.MessageBus'
# KAFKA_LOCATION = '192.168.30.159:9092'
KAFKA_LOCATION = '192.168.30.159:9092,192.168.30.160:9092,192.168.30.161:9092,192.168.30.162:9092,192.168.30.180:9092'

SPIDER_LOG_DBW_GROUP = "dbw-spider-log-simulatecart-bsr"
SPIDER_LOG_SW_GROUP = "sw-spider-log-simulatecart-bsr"
SCORING_LOG_DBW_GROUP = "dbw-scoring-log-simulatecart-bsr"
SPIDER_FEED_GROUP = "fetchers-spider-feed-simulatecart-bsr"
SEEDS_GROUP = 'seeds-group-simulatecart-bsr'
