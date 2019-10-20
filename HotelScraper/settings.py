# -*- coding: utf-8 -*-

# Scrapy settings for tencent project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'hotel'

SPIDER_MODULES = ['hotel.spiders']
NEWSPIDER_MODULE = 'hotel.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tencent (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# 线程控制
CONCURRENT_REQUESTS = 200
CONCURRENT_REQUESTS_PER_DOMAIN = 100   # 对单个网站进行并发请求的最大值。
CONCURRENT_REQUESTS_PER_IP = 100       # 对单个IP进行并发请求的最大值。

COOKIES_ENABLED = False  # 禁用cookies
DOWNLOAD_TIMEOUT = 5    # 下载超时
REDIRECT_ENABLED = False   # 禁用重定向
DOWNLOAD_DELAY = 0.3   # 设置下载延迟

REACTOR_THREADPOOL_MAXSIZE = 20  # DNS线程池

AUTOTHROTTLE_ENABLED = True  # 开启节流算法
AUTOTHROTTLE_START_DELAY = 3    # 初始下载延迟（以秒为单位）
AUTOTHROTTLE_MAX_DELAY = 5  # 在高延迟的情况下要设置的最大下载延迟（以秒为单位）。
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0   # Scrapy应该与远程网站并行发送的平均请求数。

# 状态码设置
HTTPERROR_ALLOWED_CODES = [414, 302]
RETRY_ENABLED = True
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408]
RETRY_TIMES = 5

# scrapy-redis 相关配置
# 1 过滤器  （必须） 使用 scrapy_redis 的去重组件， 在redis数据库里面做去重
# DUPEFILTER_CLASS = "iqiyi.scrapy_redis.dupefilter.RFPDupeFilter"
# 2 (必须). 使用了scrapy_redis的调度器，在redis里分配请求
# SCHEDULER = "iqiyi.scrapy_redis.scheduler.Scheduler"
# 3 在redis中保持scrapy-redis用到的各个队列，从而允许暂停和暂停后恢复，也就是不清理redis queues
# SCHEDULER_PERSIST = True
# 4通过配置RedisPipeline将item写入key为 spider.name : items 的redis的list中，供后面的分布式处理item
# 这个已经由 scrapy-redis 实现，不需要我们写代码，直接使用即可

ITEM_PIPELINES = {
   'HotelScraper.pipelines.MongoPipeline': 301,  # 保存文件
}

DOWNLOADER_MIDDLEWARES = {
   'HotelScraper.middlewares.middlewares.RotateUserAgentMiddleware': 90,  # 随机动态配置user-agent
}

# REDIS_URL = 'redis://:xiaojun0p-0p-0p-@123.206.22.148:6379'
REDIS_URL = 'redis://:@127.0.0.1:6379'
REDIS_START_URLS_AS_SET_TAG = True

# mysql conf
MYSQL_URL = 'mongodb://rootsa:ent_mongo_admin_!%40*@210.14.158.216:27017'
MYSQL_DB = 'HotelScraper'

# 日志配置
import os
import datetime
# LOG_FILE = os.path.join(os.getcwd(), 'tencent', 'log', 'spider_{}.log'.format(datetime.datetime.now().strftime('%Y-%m-%d')))
# LOG_LEVEL = 'INFO'

# 自定制命令
COMMANDS_MODULE = 'hotelscraper.run'

# 用于pipelines删除mirror数据
REDIS_PORT = 6379
REDIS_HOST = '127.0.0.1'
REDIS_PARAMS = {'password': ''}

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'tencent.middlewares.TencentSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'tencent.middlewares.TencentDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'tencent.pipelines.TencentPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
