# -*- coding: utf-8 -*-

# Scrapy settings for amazon project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'amazon'

SPIDER_MODULES = ['amazon.spiders']
NEWSPIDER_MODULE = 'amazon.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'amazon (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 50

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 0.0
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 10
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

CRAWLERA_ENABLED = True
CRAWLERA_APIKEY = '10ee6d095b0c4a5d89939f80428469e9'

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
#    'amazon.middlewares.AmazonSpiderMiddleware': 543,
#     'frontera.contrib.scrapy.middlewares.schedulers.SchedulerSpiderMiddleware': 1000,
    'scrapy.spidermiddleware.depth.DepthMiddleware': None,
    'scrapy.spidermiddleware.offsite.OffsiteMiddleware': None,
    'scrapy.spidermiddleware.referer.RefererMiddleware': None,
    'scrapy.spidermiddleware.urllength.UrlLengthMiddleware': None,
}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
#    'amazon.middlewares.MyCustomDownloaderMiddleware': 543,
#     'frontera.contrib.scrapy.middlewares.schedulers.SchedulerDownloaderMiddleware': 1000,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'amazon.middlewares.RotateUserAgentMiddleware': 100,
    'scrapy_crawlera.CrawleraMiddleware': 600,
    # 'amazon.middlewares.PhantomJSMiddleware':700
}

TO_OBTAIN_IP_ADDRESS = 'http://111.204.107.59:5000'
TO_OBTAIN_IP_ADDRESS_USER = 'xbniao'
TO_OBTAIN_IP_ADDRESS_PWD = 'xbniao123'

ERROR_LOGSTATS_INTERVAL=2
# WEBHOOK='https://oapi.dingtalk.com/robot/send?access_token=704884156d9e86f0e06ada7d6b3c2af069ae395a18583990151de7dd22229822'
WEBHOOK='https://oapi.dingtalk.com/robot/send?access_token=a2f6a826190492d9bfb5d944af48f6fad06aea305b6d826a6dfbbfd90f11cff7'

# scheduler
# SCHEDULER = 'frontera.contrib.scrapy.schedulers.frontier.FronteraScheduler'

# crawlera setting
# CRAWLERA_ENABLED = 60
# CRAWLERA_APIKEY = '10ee6d095b0c4a5d89939f80428469e9'

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#     'amazon.extensions.ErrorLogStats': 100,
    # 'amazon.extensions.InfluxStats': 100,
}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # 'amazon.pipelines.AmazonPipeline': 300,
   #  'amazon.pipelines.KafkaPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 0.25
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 3.0
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False
# RANDOMIZE_DOWNLOAD_DELAY = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = False
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# DOWNLOAD_TIMEOUT = 240
# RETRY_ENABLE = False
# DOWNLOAD_MAXSIZE = 10*1024*1024
LOG_LEVEL = 'DEBUG'
# REACTOR_THREADPOOL_MAXSIZE = 32
# DNS_TIMEOUT = 180


# influxdb
# INFLUXDB_HOST = '192.168.30.77'
# INFLUXDB_HOST = 'localhost'
# INFLUXDB_PORT = 8086
# INFLUXDB_USERNAME = 'admin'
# INFLUXDB_PASSWORD = 'admin'
# INFLUXDB_DATABASE = 'crawlerstats'
# INFLUXDB_INTERVAL = 30

# kafka pipeline
# ITEM_OUTPUT_KAFKA_LOCATION = ['192.168.30.159:9092','192.168.30.160:9092', '192.168.30.161:9092', '192.168.30.162',
#                               '192.168.30.180:9092']
# ITEM_OUTPUT_KAFKA_LOCATION = ['[fe80::f816:3eff:fe6a:7c92]']
# ITEM_OUTPUT_KAFKA_LOCATION = ['[192.168.30.159]']
# ITEM_OUTPUT_KAFKA_LOCATION = '192.168.30.159:9092'
# ITEM_OUTPUT_KAFKA_TOPIC = 'scrapy-items2'
#
# CATEGORY_SEED_KAFKA_LOCATION = ITEM_OUTPUT_KAFKA_LOCATION
# CATEGORY_SEED_KAFKA_TOPIC = 'scrapy-categories'
#
# SEED_OUTPUT_KAFKA_LOCATION = ITEM_OUTPUT_KAFKA_LOCATION
# SEED_OUTPUT_KAFKA_TOPIC = 'frontier-seeds'
#
# KEYWORD_OUTPUT_KAFKA_LOCATION = ITEM_OUTPUT_KAFKA_LOCATION
# KEYWORD_OUTPUT_KAFKA_TOPIC = 'scrapy-items-keyword'
#
# # SIMULATECART_ITEM_OUTPUT_KAFKA_LOCATION = ITEM_OUTPUT_KAFKA_LOCATION
# SIMULATECART_ITEM_OUTPUT_KAFKA_LOCATION = '192.168.30.159:9092'
# SIMULATECART_ITEM_OUTPUT_KAFKA_TOPIC = 'scrapy-items-simulatecart2'
#
# ERROR_OUTPUT_KAFKA_LOCATION=ITEM_OUTPUT_KAFKA_LOCATION
# ERROR_OUTPUT_KAFKA_TOPIC='error-seeds'


MONGODB_HOST = '192.168.30.163'
MONGODB_PORT = 27017
MONGODB_DBNAME = 'amzcartDB'
MONGODB_DOCNAME = 'cartInfo'
TSCPRODUCTURLS_PAGECOUNT = 1
KEYWORDS_COUNT = 21
#SPLASH_URL = 'http://xbn-cdh-05:8050'
