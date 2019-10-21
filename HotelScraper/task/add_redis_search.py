# -*- coding: utf-8 -*-
import json
import redis

try:
    from urllib.parse import quote
except ImportError:
    from six.moves.urllib.parse import quote


class TaskManage(object):
    REDIS_HOST = '123.206.22.148'
    REDIS_PORT = 6379
    REDIS_PASSWD = 'kCTfifGCx7aD'

    def __init__(self):
        # redis connect conf
        self.redis_client = redis.ConnectionPool(host=self.REDIS_HOST, port=self.REDIS_PORT, password=self.REDIS_PASSWD)
        self.redis_db = redis.StrictRedis(connection_pool=self.redis_client)
        self.redis_pipe = self.redis_db.pipeline()

    def item_parse(self, items, key, base_url, encode='utf-8'):
        redis_key = 'start_urls:%s' % key
        for item in items:
            city = quote(item['Destination'], encoding=encode, errors='ignore')
            state = quote(item["State"], encoding=encode, errors='ignore')
            check_in = quote(items['Check_In'], encoding=encode, errors='ignore')
            check_out = quote(items['Check_Out'], encoding=encode, errors='ignore')
            adult_room = quote(items['Adult_Room'], encoding=encode, errors='ignore')
            children_room = quote(items['Children_Room'], encoding=encode, errors='ignore')

            init_url = base_url.format(city, state, check_in, check_out, adult_room, children_room)

            task = dict(
                url = init_url,
                raw = item
            )
            print(init_url)
            self.redis_write_item(key=redis_key, score=int(item['Priority']), dict_data=task)

    def redis_write_item(self, key, score, dict_data):
        # 向redis中写入数据
        try:
            self.redis_pipe.zadd(key, score, json.dumps(dict_data, ensure_ascii=False)).execute()
        except BaseException as e:
            print("add redis %s" % e)

    def redis_get_item(self, ):
        pass


if __name__ == '__main__':
    base_url = 'https://www.hotels.com/search.do?q-destination={},%20{},%20United%20States%20of%20America&q-check-in={}&q-check-out={}&q-rooms=1&q-room-0-adults={}&q-room-0-children={}'
    key_name = 'hotel_init_spider'
    # 调用管理对象，添加任务
    obj = TaskManage()
    items = []
    obj.item_parse(items, key_name, base_url)
