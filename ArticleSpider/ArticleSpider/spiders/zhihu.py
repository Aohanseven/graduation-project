# -*- coding: utf-8 -*-
import scrapy
import re
from PIL import Image
import time
import json
from urllib import parse

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    headers={
        "User-Agent": 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
        "HOST": 'www.zhihu.com',
        "Referer": 'https://www.zhihu.com/'
    }

    def parse(self, response):
        '''提取html 页面中的所有URl 并跟踪这些url进行下一步爬去
        如果提取的url中格式为 /question/ xxx 就下载之后进行解析函数
        '''
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        for  url in all_urls:
            pass

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
            "phone_num": 'you_pthon_num',
            "password": '************',
            # "captcha_type": 'cn',
            "captcha": response.meta['captcha']
        }
        return [scrapy.FormRequest(url=post_url, formdata=post_data, headers=self.headers, callback=self.check_login)]

    def check_login(self, response):
        text_json = json.loads(response.text)
        if "msg" in text_json and  text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True,headers=self.headers)
