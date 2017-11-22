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
SPIDER_FEED_PARTITIONS = 1
SPIDER_FEED_TOPIC = 'frontier-todo-simulatecart2'
SPIDER_LOG_TOPIC = 'frontier-done-simulatecart2'
SCORING_LOG_TOPIC = 'frontier-score-simulatecart'
MESSAGE_BUS = 'frontera.contrib.messagebus.kafkabus.MessageBus'
KAFKA_LOCATION = 'localhost:9092'

SPIDER_LOG_DBW_GROUP = "dbw-spider-log-simulatecart"
SPIDER_LOG_SW_GROUP = "sw-spider-log-simulatecart"
SCORING_LOG_DBW_GROUP = "dbw-scoring-log-simulatecart"
SPIDER_FEED_GROUP = "fetchers-spider-feed-simulatecart"
SEEDS_GROUP = 'seeds-group-simulatecart'
