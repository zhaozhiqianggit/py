# -*- coding: utf-8 -*-
from frontera.settings.default_settings import MIDDLEWARES
from frontera.settings.default_settings import SQLALCHEMYBACKEND_MODELS

MAX_NEXT_REQUESTS = 512
SPIDER_FEED_PARTITIONS = 1
SPIDER_LOG_PARTITIONS = 1

#--------------------------------------------------------
# Url storage
#--------------------------------------------------------

BACKEND = 'amazon.frontier.backend.SimulateCartBackend'

MESSAGE_BUS = 'frontera.contrib.messagebus.kafkabus.MessageBus'
KAFKA_LOCATION = 'localhost:9092'
SPIDER_FEED_TOPIC = 'frontier-todo-simulatecart2'
SPIDER_LOG_TOPIC = 'frontier-done-simulatecart2'
SCORING_LOG_TOPIC = 'frontier-score-simulatecart'
SEEDS_TOPIC = 'frontier-seeds-competing'

SEEDS_GROUP = 'seeds-group-simulatecart'
SEEDS_INTERVAL = 5

SQLALCHEMYBACKEND_ENGINE = 'mysql+mysqlconnector://root:19830602@localhost:3306/frontera_simulatecart'
SQLALCHEMYBACKEND_ENGINE_ECHO = False
SQLALCHEMYBACKEND_DROP_ALL_TABLES = False
SQLALCHEMYBACKEND_CLEAR_CONTENT = False
from datetime import timedelta
SQLALCHEMYBACKEND_REVISIT_INTERVAL = timedelta(minutes=2)
# 从种子库中生成Request的间隔
LOOPINTERVAL = 10
# 从revisiting_queue表中拿下一批数据的间隔
NEW_BATCH_DELAY = 10.0



MIDDLEWARES.extend([
    'frontera.contrib.middlewares.domain.DomainMiddleware',
    'frontera.contrib.middlewares.fingerprint.DomainFingerprintMiddleware',
    'amazon.frontier.middlewares.SimulateCartSeedsMiddleware',
])

SQLALCHEMYBACKEND_MODELS.update({
    'SeedsModel': 'amazon.frontier.models.SimulateCartSeedsModel',
})

LOGGING_CONFIG='amazon/logging.conf'

SPIDER_LOG_DBW_GROUP = "dbw-spider-log-simulatecart"
SPIDER_LOG_SW_GROUP = "sw-spider-log-simulatecart"
SCORING_LOG_DBW_GROUP = "dbw-scoring-log-simulatecart"
SPIDER_FEED_GROUP = "fetchers-spider-feed-simulatecart"
