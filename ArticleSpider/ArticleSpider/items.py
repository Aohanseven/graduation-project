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
from .utils.common import extract_nums
from .settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT

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

    def get_insert_sql(self):
        insert_sql = """INSERT INTO jobbole_data(title, url, url_object_id, create_date, front_image_url, praise_nums, fav_nums, comment_nums, content, tags)VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"""
        params = (self['title'], self['url'], self['url_object_id'], self['create_date'], self['front_image_url'], self['praise_nums'], self['fav_nums'], self['comment_nums'], self['content'], self['tags'] )
        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    # 知乎问题item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
        INSERT INTO zhihu_question(zhihu_id, topics, url, title, content,  comments_num, watch_user_num, click_num, crawl_time)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        
    """
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"]
        title = "".join(self["title"])
        content = "".join(self["content"])
        # answer_num = extract_nums("".join(self["answer_num"]))
        comments_num = extract_nums("".join(self["comments_num"]))
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0].replace(',', ''))
            click_num = int(self["watch_user_num"][1].replace(',', ''))
        else:
            watch_user_num = int(self["watch_user_num"][0].replace(',', ''))
            click_num = 0

        params = (zhihu_id, topics, url, title, content,  comments_num, watch_user_num, click_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    updated_time = scrapy.Field()
