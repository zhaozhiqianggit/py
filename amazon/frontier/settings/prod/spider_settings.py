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
SPIDER_FEED_TOPIC = 'frontier-todo'
SPIDER_LOG_TOPIC = 'frontier-done'
SCORING_LOG_TOPIC = 'frontier-score'
MESSAGE_BUS = 'frontera.contrib.messagebus.kafkabus.MessageBus'
KAFKA_LOCATION = '10.0.6.65:9092,10.0.6.66:9092,10.0.6.59:9092,10.0.6.53:9092,10.0.6.62:9092,10.0.6.56:9092,10.0.6.58:9092'
