# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from PIL import Image
import time
import json
from urllib import parse
from scrapy.loader import ItemLoader
from..items import ZhihuAnswerItem, ZhihuQuestionItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    # question的第一页answer的请求的url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B*%5D.mark_infos%5B*%5D.url%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={1}&limit={2}&sort_by=default"
    headers={
        "User-Agent": 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
        "HOST": 'www.zhihu.com',
        "Referer": 'https://www.zhihu.com/'
    }

    def parse(self, response):
        '''
        深度优先
        提取html 页面中的所有URl 并跟踪这些url进行下一步爬去
        如果提取的url中格式为 /question/ xxx 就下载之后进行解析函数
        '''
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match('.*zhihu.com/question/(\d+)/answer/.*', url)
            if match_obj:
                request_url = match_obj.group(0)
                question_id = match_obj.group(1)

                yield scrapy.Request(request_url, headers=self.headers, meta={"question_id": question_id},callback=self.parse_question)
            else:
                yield scrapy.Request(url , headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        # 处理question页面, 从页面中提取出具体的question item
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css("title", 'h1.QuestionHeader-title::text')
        item_loader.add_css("content", '.QuestionHeader-detail')
        item_loader.add_value("url", response.url)
        item_loader.add_value("zhihu_id", int(response.meta['question_id']))
        item_loader.add_css("answer_num", '.List-headerText span::text')
        item_loader.add_css("comments_num", '.QuestionHeader-Comment button::text')
        item_loader.add_css("watch_user_num", '.NumberBoard-itemValue::text')
        item_loader.add_css("topics", '.QuestionHeader-topics .Popover div::text')

        question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(int(response.meta['question_id']), 0, 20), headers=self.headers, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        answer_json = json.loads(response.text)
        is_end = answer_json["paging"]["is_end"]
        next_url = answer_json["paging"]["next"]

        #提取answer的内容
        for answer in  answer_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] =answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["parise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["updated_time"] = datetime.datetime.now()
            yield answer_item



        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

    def start_requests(self):
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + '&type=login&lang=en'
        return [scrapy.Request(url=captcha_url, headers=self.headers, callback=self.parse_captcha)]

    def parse_captcha(self, response):
        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)
            f.close()
        try:
            img = Image.open('captcha.jpg')
            img.show()
        except:
            pass
        # 中文倒立验证码
        # captcha = {
        #     'img_size': [200, 44],
        #     'input_points': []
        # }
        #
        # points = [[18.7969,27],[45.7969,25],[69.7969,24],[98.7969,28],[126.797,25],[150.797,26],[178.797,28]]
        # seq = input('请输入倒立文字的位置\n')
        # for i in seq:
        #     captcha['input_points'].append(points[(int(i) - 1)])

        captcha = input("请输入验证码:")

        return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, meta={'captcha':captcha}, callback=self.login)]

    def login(self, response):
        response_text = response.text
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        xsrf=''
        if match_obj:
            xsrf = match_obj.group(1)
        post_url = 'https://www.zhihu.com/login/phone_num'
        post_data = {
            "_xsrf": xsrf,
            "phone_num": '15501967360',
            "password": 'a2577811',
            # "captcha_type": 'cn',
            "captcha": response.meta['captcha']
        }
        return [scrapy.FormRequest(url=post_url, formdata=post_data, headers=self.headers, callback=self.check_login)]

    def check_login(self, response):
        text_json = json.loads(response.text)
        if "msg" in text_json and  text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)
