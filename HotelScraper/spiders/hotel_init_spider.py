# -*- coding: utf-8 -*-
import scrapy
import datetime
import json
import re
from HotelScraper.items.hotel import HotelItem
from HotelScraper.scrapy_redis.spiders import RedisSpider
from HotelScraper.task.add_redis_search import TaskManage
from HotelScraper.utils.redis_mirror_manager import delete_task


class HotelInitSpiderSpider(RedisSpider):
    name = 'hotel_init_spider'
    redis_key = 'start_urls:{}'.format(name)

    task = TaskManage()

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Pragma': 'no-cache',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': 1,
        }
    }

    def parse(self, response):
        meta = response.meta
        task = meta['task']
        var = json.loads(task)
        var = var['raw']

        info_dict = dict()
        info_dict['status'] = var['Status']

        # Get the hotel search results
        hotel_list = response.xpath('//div[@class="h-listing"]/ol//li')
        if not hotel_list:
            self.logger.debug('There is no hotel in {}'.format(info_dict['Desination']))
            delete_task('mirror:{}'.format(self.name), task)  # 删除mirror表数据
        else:
            # Get each hotel obj
            for hotel in hotel_list:
                if not hotel.xpath('//aside'):
                    continue
                else:
                    hotel_item = HotelItem()

                    hotel_item["hotel_name"] = hotel.xpath('@data-title').extract_first()
                    hotel_item["hotel_id"] = hotel.xpath('@data-hotel-id').extract_first()

                    hotel_description = hotel.xpath('//div[@class="description resp-module"]')
                    hotel_item["hotel_address"] = hotel_description.xpath('//address/span/text()')[0]
                    hotel_item["hotel_telephone"] = hotel_description.xpath('//address/span/text()')[1]

                    hotel_aside = hotel.xpath('//aside')
                    try:
                        hotel_item["hotel_price"] = hotel_aside.xpath('//div[@class="price"]//ins').extract_first()
                    except:
                        hotel_item["hotel_price"] = hotel_aside.xpath('//div[@class="price"]//strong/text()').extract_first()

                    yield hotel_item

    def save_task(self, add_redis_key, info_dict):
        if 'http:' in info_dict['url']:
            info_dict['url'] = info_dict['url'].replace('http:', '')
        if 'https:' not in info_dict['url']:
            info_dict['url'] = 'https:' + info_dict['url']
        data_dict = {
            'url': info_dict['url'],
            'raw': info_dict
        }
        self.task.redis_write_item(add_redis_key, 1000, data_dict)

