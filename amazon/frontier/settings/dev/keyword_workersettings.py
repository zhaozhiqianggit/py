# -*- coding: utf-8 -*-
from frontera.settings.default_settings import MIDDLEWARES
from frontera.settings.default_settings import SQLALCHEMYBACKEND_MODELS

MAX_NEXT_REQUESTS = 512
SPIDER_FEED_PARTITIONS = 1
SPIDER_LOG_PARTITIONS = 1

#--------------------------------------------------------
# Url storage
#--------------------------------------------------------

BACKEND = 'amazon.frontier.backend.KeywordBackend'

MESSAGE_BUS = 'frontera.contrib.messagebus.kafkabus.MessageBus'
KAFKA_LOCATION = 'localhost:9092'
SPIDER_FEED_TOPIC = 'frontier-todo-keyword'
SPIDER_LOG_TOPIC = 'frontier-done-keyword'
SCORING_LOG_TOPIC = 'frontier-score-keyword'
SEEDS_TOPIC = 'frontier-seeds-keyword'

SEEDS_GROUP = 'seeds-group-keyword'
SEEDS_INTERVAL = 5

SQLALCHEMYBACKEND_ENGINE = 'mysql+mysqlconnector://root:19830602@localhost:3306/frontera_keyword'
SQLALCHEMYBACKEND_ENGINE_ECHO = False
SQLALCHEMYBACKEND_DROP_ALL_TABLES = False
SQLALCHEMYBACKEND_CLEAR_CONTENT = False
from datetime import timedelta
# SQLALCHEMYBACKEND_REVISIT_INTERVAL = timedelta(days=3)
SQLALCHEMYBACKEND_REVISIT_INTERVAL = timedelta(minutes=1)
# 从种子库中生成Request的间隔
LOOPINTERVAL = 10
# 从revisiting_queue表中拿下一批数据的间隔
NEW_BATCH_DELAY = 10.0

MIDDLEWARES = [
    'amazon.frontier.middlewares.CustomUrlFingerprintMiddleware',
    'frontera.contrib.middlewares.domain.DomainMiddleware',
    'frontera.contrib.middlewares.fingerprint.DomainFingerprintMiddleware',
    'amazon.frontier.middlewares.KeyWordSeedsMiddleware',
]

SQLALCHEMYBACKEND_MODELS.update({
    'SeedsModel': 'amazon.frontier.models.KeywordSeedsModel',
})

LOGGING_CONFIG='amazon/logging.conf'

SPIDER_LOG_DBW_GROUP = "dbw-spider-log-keyword"
SPIDER_LOG_SW_GROUP = "sw-spider-log-keyword"
SCORING_LOG_DBW_GROUP = "dbw-scoring-log-keyword"
SPIDER_FEED_GROUP = "fetchers-spider-feed-keyword"
