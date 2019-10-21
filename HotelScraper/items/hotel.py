#!/usr/bin/python3
# -*- coding: utf-8 -*-

from scrapy import Item, Field
from HotelScraper.items.item import Common


class HotelItem(Common, Item):
    collection = 'hotel'

    # Basic
    hotel_name = Field()
    hotel_address = Field()

    # Primary
    hotel_level = Field()
    hotel_type = Field()

    # Primary
    hotel_price = Field()

    # Primary
    hotel_score = Field()
    hotel_rating = Field()

    hotel_feature = Field()
    hotel_family_friendly = Field()
    hotel_supplier_points_of_interest = Field()
