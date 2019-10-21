from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from scrapy.spiders import Spider, CrawlSpider

from . import connection, defaults
from .utils import bytes_to_str
import json
from scrapy.utils.project import get_project_settings
from redis import WatchError


class RedisMixin(object):
    """Mixin class to implement reading urls from a redis queue."""
    redis_key = None
    redis_batch_size = None
    redis_encoding = None
    task_string = None

    # Redis client placeholder.
    server = None

    def start_requests(self):
        """Returns a batch of start requests from redis."""
        return self.next_requests()

    def setup_redis(self, crawler=None):
        """Setup redis connection and idle signal.

        This should be called after the spider has set its crawler object.
        """
        if self.server is not None:
            return

        if crawler is None:
            # We allow optional crawler argument to keep backwards
            # compatibility.
            # XXX: Raise a deprecation warning.
            crawler = getattr(self, 'crawler', None)

        if crawler is None:
            raise ValueError("crawler is required")

        settings = crawler.settings

        if self.redis_key is None:
            self.redis_key = settings.get(
                'REDIS_START_URLS_KEY', defaults.START_URLS_KEY,
            )

        self.redis_key = self.redis_key % {'name': self.name}

        if not self.redis_key.strip():
            raise ValueError("redis_key must not be empty")

        if self.redis_batch_size is None:
            # TODO: Deprecate this setting (REDIS_START_URLS_BATCH_SIZE).
            self.redis_batch_size = settings.getint(
                'REDIS_START_URLS_BATCH_SIZE',
                settings.getint('CONCURRENT_REQUESTS'),
            )

        try:
            self.redis_batch_size = int(self.redis_batch_size)
        except (TypeError, ValueError):
            raise ValueError("redis_batch_size must be an integer")

        if self.redis_encoding is None:
            self.redis_encoding = settings.get('REDIS_ENCODING', defaults.REDIS_ENCODING)

        self.logger.info("Reading start URLs from redis key '%(redis_key)s' "
                         "(batch size: %(redis_batch_size)s, encoding: %(redis_encoding)s",
                         self.__dict__)

        self.server = connection.from_settings(crawler.settings)
        # The idle signal is called when the spider has no requests left,
        # that's when we will schedule new requests from redis queue
        crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)

    def return_url(self, task=None):
        """
        :param task: 从 redis 读取的原始数据
        :return:
        """
        return None

    def __custom_get_task(self):
        row_str = None
        row_score = None
        pipe = self.server.pipeline()
        loop = True
        while loop:
            try:
                pipe.zrevrange(self.redis_key, 0, 0, withscores=True)[0]
                row_value_score = pipe.execute()[0][0]  # <class 'tuple'>: (b'99', 99.0)
                row_str, row_score = row_value_score
                pipe.watch(self.redis_key)
                pipe.multi()
                results = pipe.zrem(self.redis_key, row_str.decode('utf-8')).execute()
                pipe.unwatch()
                if results[0]:  # results 是一个 list, 第一个元素代表成功与失败。1：成功。0:失败
                    # 删除成功。退出循环
                    loop = False  # 没有出现异常，说明不同线程或进程操作正确，跳出循环
                    break
                else:
                    # 删除失败，说明数据已经被别的进程取到并且删除，需要继续取任务和删除任务
                    continue
            except WatchError as watch_error:
                # 释放锁，继续下次循环
                pipe.unwatch()
                continue
            except IndexError as i_e:
                # 当 redis 里面 没有任务时，再操作 redis 时报 IndexError 异常
                # 没有任务时，结束循环，令 row_str=None
                loop = False
                row_str = None
            except BaseException as e:
                row_str = None
                break
        return row_str, row_score

    def next_requests(self):
        """Returns a request to be scheduled or none."""
        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        # fetch_one = self.server.spop if use_set else self.server.lpop
        all_settings = get_project_settings()
        flag = all_settings.getbool('REDIS_START_URLS_AS_SET_TAG')
        # XXX: Do we need to use a timeout here?
        found = 0
        # TODO: Use redis pipeline execution.
        while found < self.redis_batch_size:
            if flag:
                row_str, row_score = self.__custom_get_task()
            else:
                fetch_one = self.server.spop if use_set else self.server.lpop

            json_data = fetch_one(self.redis_key) if not flag else row_str
            if json_data:
                task_string = json_data.decode('utf-8')   # 字节类型
                self.task_string = task_string
                dict_data = json.loads(task_string)

                if dict_data.get('url'):
                    data = dict_data['url']
                else:
                    data = self.return_url(task = task_string)
            else:
                data = None

            if not data:
                # Queue empty.
                break
            try:
                self.server.zadd('mirror:{0}'.format(self.name), row_score, task_string)
            except BaseException as e:
                pass
            req = self.make_request_from_data(data)
            req.meta['task'] = task_string
            if req:
                yield req
                found += 1
            else:
                self.logger.debug("Request not made from data: %r", data)

        if found:
            self.logger.debug("Read %s requests from '%s'", found, self.redis_key)

    def make_request_from_data(self, data):
        """Returns a Request instance from data coming from Redis.

        By default, ``data`` is an encoded URL. You can override this method to
        provide your own message decoding.

        Parameters
        ----------
        data : bytes
            Message from redis.

        """
        url = bytes_to_str(data, self.redis_encoding)
        return self.make_requests_from_url(url)

    def schedule_next_requests(self):
        """Schedules a request if available"""
        # TODO: While there is capacity, schedule a batch of redis requests.
        for req in self.next_requests():
            self.crawler.engine.crawl(req, spider=self)

    def spider_idle(self):
        """Schedules a request if available, otherwise waits."""
        # XXX: Handle a sentinel to close the spider.
        self.schedule_next_requests()
        raise DontCloseSpider


class RedisSpider(RedisMixin, Spider):
    """Spider that reads urls from redis queue when idle.

    Attributes
    ----------
    redis_key : str (default: REDIS_START_URLS_KEY)
        Redis key where to fetch start URLs from..
    redis_batch_size : int (default: CONCURRENT_REQUESTS)
        Number of messages to fetch from redis on each attempt.
    redis_encoding : str (default: REDIS_ENCODING)
        Encoding to use when decoding messages from redis queue.

    Settings
    --------
    REDIS_START_URLS_KEY : str (default: "<spider.name>:start_urls")
        Default Redis key where to fetch start URLs from..
    REDIS_START_URLS_BATCH_SIZE : int (deprecated by CONCURRENT_REQUESTS)
        Default number of messages to fetch from redis on each attempt.
    REDIS_START_URLS_AS_SET : bool (default: False)
        Use SET operations to retrieve messages from the redis queue. If False,
        the messages are retrieve using the LPOP command.
    REDIS_ENCODING : str (default: "utf-8")
        Default encoding to use when decoding messages from redis queue.

    """

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(RedisSpider, self).from_crawler(crawler, *args, **kwargs)
        obj.setup_redis(crawler)
        return obj


class RedisCrawlSpider(RedisMixin, CrawlSpider):
    """Spider that reads urls from redis queue when idle.

    Attributes
    ----------
    redis_key : str (default: REDIS_START_URLS_KEY)
        Redis key where to fetch start URLs from..
    redis_batch_size : int (default: CONCURRENT_REQUESTS)
        Number of messages to fetch from redis on each attempt.
    redis_encoding : str (default: REDIS_ENCODING)
        Encoding to use when decoding messages from redis queue.

    Settings
    --------
    REDIS_START_URLS_KEY : str (default: "<spider.name>:start_urls")
        Default Redis key where to fetch start URLs from..
    REDIS_START_URLS_BATCH_SIZE : int (deprecated by CONCURRENT_REQUESTS)
        Default number of messages to fetch from redis on each attempt.
    REDIS_START_URLS_AS_SET : bool (default: True)
        Use SET operations to retrieve messages from the redis queue.
    REDIS_ENCODING : str (default: "utf-8")
        Default encoding to use when decoding messages from redis queue.

    """

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(RedisCrawlSpider, self).from_crawler(crawler, *args, **kwargs)
        obj.setup_redis(crawler)
        return obj
