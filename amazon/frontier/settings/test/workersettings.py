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
BACKEND = 'amazon.frontier.backend.CustomBackend'

MESSAGE_BUS = 'frontera.contrib.messagebus.kafkabus.MessageBus'
KAFKA_LOCATION = '192.168.30.159:9092,192.168.30.160:9092,192.168.30.161:9092,192.168.30.162:9092,192.168.30.180:9092'
SPIDER_FEED_TOPIC = 'frontier-todo'
SPIDER_LOG_TOPIC = 'frontier-done'
SCORING_LOG_TOPIC = 'frontier-score'
SEEDS_TOPIC = 'frontier-seeds'

SEEDS_GROUP = 'seeds-group'
SEEDS_INTERVAL = 5

# SQLALCHEMYBACKEND_ENGINE = 'sqlite:///url_storage_dist.sqlite'
SQLALCHEMYBACKEND_ENGINE = 'mysql+mysqlconnector://root:root123@172.16.1.81:3306/frontera'
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
    'amazon.frontier.middlewares.SeedsMiddleware',
])

SQLALCHEMYBACKEND_MODELS.update({
    'SeedsModel': 'amazon.frontier.models.SeedsModel',
})

LOGGING_CONFIG='amazon/logging.conf'

