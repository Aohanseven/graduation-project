# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from urllib import parse
from ..items import JobBoleArticleItem, ArticleItemLoader
from ..utils.common import get_md5
from scrapy.loader import ItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        获取文章表页的所有url交给scrapy下载后进行解析
        获取下一文章表页的url
        :param response:
        :return:
        """
        post_nodes = response.xpath('//div[@id="archive"]/div[@class="post floated-thumb"]/div[@class="post-thumb"]')
        for post_node in post_nodes:
            image_url = post_node.css('img').xpath('@src').extract()
            post_url = post_node.xpath('a/@href').extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url}, callback=self.parse_detail)

        #提取下一页url
        next_urls= response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
        if next_urls:
            yield Request(url=parse.urljoin(response.url, next_urls), callback=self.parse)

    def parse_detail(self, response):
        # article_item = JobBoleArticleItem()
        # front_image_url = response.meta['front_image_url']
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        # create_time = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace("·", "").strip()
        # praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
        # # 抓取收藏数
        # fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        # match_re = re.match(".*?(\d+).*", fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        # # 抓取评论数
        # comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract_first()
        # match_re = re.match(".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        #
        # content = response.xpath('//div[@class="entry"]').extract_first()
        # # 去重
        # tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ','.join(tag_list)
        #
        # article_item['url_object_id'] = get_md5(response.url)
        # article_item['title'] = title
        # try:
        #     create_time =datetime.datetime.strptime(create_time, "%Y/%m/%d").date()
        # except Exception as e:
        #     create_time = datetime.datetime.now().date()
        # article_item['create_time'] = create_time
        # article_item['url'] = response.url
        # article_item['front_image_url'] = front_image_url
        # article_item['praise_nums'] = praise_nums
        # article_item['fav_nums'] = fav_nums
        # article_item['comment_nums'] = comment_nums
        # article_item['tags'] = tags
        # article_item['content'] = content

        # 通过item_loader 加载item

        front_image_url = response.meta['front_image_url']
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_xpath("title", '//div[@class="entry-header"]/h1/text()')
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_xpath("create_date", '//p[@class="entry-meta-hide-on-mobile"]/text()')
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_xpath("praise_nums", '//span[contains(@class,"vote-post-up")]/h10/text()')
        item_loader.add_xpath("fav_nums", '//span[contains(@class,"bookmark-btn")]/text()' )
        item_loader.add_xpath("comment_nums", '//span[contains(@class,"vote-post-up")]/h10/text()')
        item_loader.add_xpath("content", '//div[@class="entry"]')
        item_loader.add_xpath("tags", '//p[@class="entry-meta-hide-on-mobile"]/a/text()')

        article_item = item_loader.load_item()
        yield article_item


