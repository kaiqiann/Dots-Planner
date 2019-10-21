# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import datetime
import os
import copy
import json
from HotelScraper.items.hotel import HotelItem
from scrapy.utils.project import get_project_settings
from HotelScraper.scrapy_redis.connection import get_redis_from_settings


# save to mysql
class MysqlPipeline(object):
    def __init__(self, mysql_url, mysql_db):
        self.mysql_url = mysql_url
        self.mysql_db = mysql_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_url = crawler.settings.get('MYSQL_URL'),
            mysql_db = crawler.settings.get('MYSQL_DB')
        )

    def open_spider(self, spider):
        connection = pymysql.connect(host='localhost',
                                     user='user',
                                     password='passwd',
                                     db='db',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        self.db = self.client[self.mongo_db]
        self.server = get_redis_from_settings(get_project_settings())

    def process_item(self, item, spider):
        print(item)
        return item

        # redis_key = 'mirror:{0}'.format(spider.name)
        # task = item['raw']
        #
        # del item['raw']
        #
        # if isinstance(item, HotelItem):
        #     album_id = item.get('album_id')
        #     # 查找条件
        #     condition = {'album_id': album_id}
        #     item['modify_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #
        #     result = self.db[item.collection].find_one(condition)
        #     if not result:
        #         # 数据不存在，直接插入
        #         self.db[item.collection].insert(dict(item))
        #     else:
        #         # 数据存在，开始更新
        #         for key, val in item.items():
        #             result[key] = val
        #         # 更新新数据
        #         self.db[item.collection].update_one(condition, {'$set': result})
        #
        # self.delete_mirror_queue(redis_key, task)
        # print('已保存到mongodb'.center(50, '='))
        # return item

    def delete_mirror_queue(self, k, v):
        try:
            self.server.zrem(k, v)
            print('delete mirror success')
        except BaseException as e:
            print('delete mirror failure{0}\t{1}'.format(os.linesep, v))
            print(e)
        pass

    def close_spider(self, spider):
        self.client.close()


class HotelPipeline(object):
    def process_item(self, item, spider):
        return item
