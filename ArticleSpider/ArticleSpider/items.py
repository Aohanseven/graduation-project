# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join

class JobBoleArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def date_convert(value):
        try:
            create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()

        return create_date


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def return_value(value):
    return  value


def remove_comment_tages(value):
    if "评论" in value:
        return ""
    else:
        return value


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):

    title = scrapy.Field()           # 标题
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )     # 创建时间
    url = scrapy.Field()             # 每个文章的url
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()  # 文章封面
    front_image_path = scrapy.Field(
        output_processor=MapCompose(return_value)
    )  # 文章封面存放地址
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )    # 点赞
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )       # 收藏
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )   # 评论
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tages),
        output_processor=Join(",")
    )
    content = scrapy.Field()        # 正文

