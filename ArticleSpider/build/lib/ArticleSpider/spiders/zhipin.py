# -*- coding: utf-8 -*-

from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.spiders import Rule
from ..items import ZhipinItemLoader, ZhipinItem
from ..utils.common import get_md5



class LagouSpider(RedisCrawlSpider):
    name = 'zhipin_redis'
    allowed_domains = ['www.zhipin.com']
    redis_key = 'zhipinCrawler:starturls'

    rules = (
        Rule(LinkExtractor(allow=r'job_detail/\d+.html'), callback='parse_job', follow=True),
    )


    def parse_job(self, response):
        item_loader = ZhipinItemLoader(item=ZhipinItem(), response=response)
        item_loader.add_css("title", "h1.name::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("salary", "h1.name span::text")
        item_loader.add_css("job_city", ".job-primary .info-primary p::text")
        item_loader.add_css("work_years", ".job-primary .info-primary p::text")
        item_loader.add_css("degree_need", ".job-primary .info-primary p::text")
        item_loader.add_css("publish_time", ".job-author span::text")
        item_loader.add_css("tags", ".job-tags span::text")
        item_loader.add_css("job_sec", ".job-sec .text::text")
        item_loader.add_css("company_name", ".info-company .name a::text")
        item_loader.add_xpath("company_url", "//*[@id='main']/div[1]/div/div/div[3]/p[2]/text()")
        item_loader.add_css("job_location", ".location-address::text")


        job_item = item_loader.load_item()
        yield job_item
