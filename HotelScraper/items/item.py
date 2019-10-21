#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author      : Xinyu Zhang
# @File        : items.py
# @Software    : PyCharm
# @description : Define the data that want to grab

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SpidercoreItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class CommonItem(scrapy.Item):
    """
        公共字段。所有 Item 都必须继承这个 类
    """
    raw = scrapy.Field()        # 用来保存原始数据
    site = scrapy.Field()       # 标识属于哪个网站(以网站名作为数据库名)
    collect = scrapy.Field()    # 标识属于 MongoDB 中哪个集合(即哪张表)
    finish = scrapy.Field()     # 标识这个任务是否已经结束 0:没有结束，1:任务结束s
    _id = scrapy.Field()        # mongodb id去重


class Common(CommonItem):
    """
        直接继承 CommonItem 时，报 Cannot create a consistent method resolution 错误
        所以 写个 类 Common 继承 CommonItem ，Common 当一个中间传递类
        继承 Common 这个类时，必须放在第一个位置，因为 python MRO (python3 继承是 "广度优先")
    """
    pass
