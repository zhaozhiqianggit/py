# -*- coding: utf-8 -*-
from frontera.settings.default_settings import MIDDLEWARES
from frontera.settings.default_settings import SQLALCHEMYBACKEND_MODELS

MAX_NEXT_REQUESTS = 512
SPIDER_FEED_PARTITIONS = 3
SPIDER_LOG_PARTITIONS = 1

#--------------------------------------------------------
# Url storage
#--------------------------------------------------------

# BACKEND = 'frontera.contrib.backends.sqlalchemy.SQLAlchemyBackend'
#BACKEND = 'frontera.contrib.backends.sqlalchemy.Distributed'
# BACKEND = 'frontera.contrib.backends.sqlalchemy.revisiting.Backend'
BACKEND = 'amazon.frontier.backend.BSRSimulateCartBackend'

MESSAGE_BUS = 'frontera.contrib.messagebus.kafkabus.MessageBus'
KAFKA_LOCATION = '10.0.6.65:9092,10.0.6.66:9092,10.0.6.59:9092,10.0.6.53:9092,10.0.6.62:9092,10.0.6.56:9092,10.0.6.58:9092'
SPIDER_FEED_TOPIC = 'frontier-todo-simulatecart-bsr'
SPIDER_LOG_TOPIC = 'frontier-done-simulatecart-bsr'
SCORING_LOG_TOPIC = 'frontier-score-simulatecart-bsr'
SEEDS_TOPIC = 'frontier-seeds-simulatecart-bsr'

SEEDS_GROUP = 'seeds-group-simulatecart-bsr'
SEEDS_INTERVAL = 5

# SQLALCHEMYBACKEND_ENGINE = 'sqlite:///url_storage_dist.sqlite'
SQLALCHEMYBACKEND_ENGINE = 'mysql+mysqlconnector://root:root123@xbn-crawler-db:3306/frontera_simulatecart_bsr'
SQLALCHEMYBACKEND_ENGINE_ECHO = False
SQLALCHEMYBACKEND_DROP_ALL_TABLES = False
SQLALCHEMYBACKEND_CLEAR_CONTENT = False
from datetime import timedelta
# SQLALCHEMYBACKEND_REVISIT_INTERVAL = timedelta(days=3)
SQLALCHEMYBACKEND_REVISIT_INTERVAL = timedelta(days=1)
# 从种子库中生成Request的间隔
LOOPINTERVAL = 10
# 从revisiting_queue表中拿下一批数据的间隔
NEW_BATCH_DELAY = 10.0



MIDDLEWARES.extend([
    'frontera.contrib.middlewares.domain.DomainMiddleware',
    'frontera.contrib.middlewares.fingerprint.DomainFingerprintMiddleware',
    'amazon.frontier.middlewares.BSRSimulateCartSeedsMiddleware',
])

SQLALCHEMYBACKEND_MODELS.update({
    'SeedsModel': 'amazon.frontier.models.BSRSimulateCartSeedsModel',
})

LOGGING_CONFIG='amazon/logging.conf'

SPIDER_LOG_DBW_GROUP = "dbw-spider-log-simulatecart-bsr"
SPIDER_LOG_SW_GROUP = "sw-spider-log-simulatecart-bsr"
SCORING_LOG_DBW_GROUP = "dbw-scoring-log-simulatecart-bsr"
SPIDER_FEED_GROUP = "fetchers-spider-feed-simulatecart-bsr"
