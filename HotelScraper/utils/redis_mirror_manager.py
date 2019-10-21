import HotelScraper.settings as settings
import redis
import json


redis_server = settings.REDIS_HOST
redis_port = settings.REDIS_PORT
params = settings.REDIS_PARAMS
pw = params['password']


class RedisQueue(object):
    """
        redis queue operate
    """
    def __init__(self):
        """
            初始化 redis 队列类型 和 redis db
        """
        self.__redis_pool = redis.ConnectionPool(host=redis_server, port=redis_port, password=pw)
        self.__redis_db = redis.StrictRedis(connection_pool=self.__redis_pool)
        self.__redis_pipeline = self.__redis_db.pipeline()
        self.__r_pipe = self.__redis_pipeline
        pass

    def __del__(self):
        """
            析构，释放 redis 连接
        :return:
        """
        # ConnectionPool.disconnect() does in fact close all the connections opened from that connection pool.
        # It does not prevent new connections from being opened however
        self.__redis_pool.disconnect()

    def add_task(self, key, dict_data, score=1000):
        """
            向 redis 添加任务
        :param key:       redis_key
        :param dict_data: Python dict
        :param score:     优先级。默认是0
        :return:          0: 成功。 1: 失败。-1: 函数没有执行
        """
        ret = -1
        try:
            self.__r_pipe.zadd(key, score, json.dumps(dict_data, ensure_ascii=False)).execute()
            ret = 0
            pass
        except BaseException as e:
            ret = 1
        pass
        return ret

    def add_fail_tasks(self, mirror_key=None):
        """
            添加失败的 队列
        :param mirror_key:
        :return:
        """
        ret = -1
        try:
            fail_sets = self.__r_pipe.zrange(mirror_key, 0, 9999999999, withscores=True).execute()[0]
            self.__r_pipe.delete(mirror_key).execute()
            if fail_sets:
                for d in fail_sets:
                    value, score = d
                    d_string = value.decode('utf-8')
                    d_dict = json.loads(d_string)
                    self.add_task('start_urls:{0}'.format(mirror_key.split(':')[1]), d_dict)
            ret = 0
        except BaseException as e:
            ret = 1
        return ret

    def write_log(self, spider_name, log_info):
        self.__r_pipe.lpush('log:{0}'.format(spider_name), log_info).execute()
        pass

    def leave_tasks_num(self, key):
        num = self.__r_pipe.zcard(key).execute()
        return num[0]

    def delete_task(self, key, dict_data):
        remove_num = self.__r_pipe.zrem(key, dict_data).execute()
        self.__redis_pool.disconnect()
        return remove_num[0]

