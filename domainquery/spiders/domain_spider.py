# -*- coding: utf-8 -*-
import time

import scrapy
from scrapy import Request
from scrapy.http import HtmlResponse
from selenium import webdriver
from domainquery.items import DomainqueryItem
from domainquery.settings import redis_host, redis_port
import redis


class DomainSpiderSpider(scrapy.Spider):

    def __init__(self):
        host = redis_host
        port = redis_port
        self.pool = redis.ConnectionPool(host=host, port=port, decode_responses=True, db=2)
        self.redis = redis.Redis(connection_pool=self.pool)

    name = 'domain_spider'
    allowed_domains = ['www.xinnet.com']
    start_urls = ['http://www.ipshi.com']

    # allowed_domains = ['www.22.com']
    # start_urls = ['https://www.22.cn/ym/search.aspx?domains=a.com']

    def parse(self, response):
        print(response.xpath('//div[@id="ownip"]/text()').extract())
        base_url = 'http://www.xinnet.com/domain/domainQueryResult.html?suffix=.com&prefix='
        # 获取url
        if self.redis.llen('urls') == 0:
            self.get_url_type1()
        while True:
            if self.redis.llen('urls') > 0:
                url = self.redis.rpoplpush('urls', 'used_urls')
                request = Request(url=base_url + url, dont_filter=True)
                # 获取异步请求的响应
                htmlresponse = self.use_elenium_phatomjs(request)
                # 解析响应
                domain_item = self.parse_items(htmlresponse)
                self.redis.rpoplpush('urls', 'used_urls')
                yield domain_item
            else:
                break

    def get_url_type1(self):

        base_code = ['', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
                     'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        # base_code = ['', '0', '1']
        for i_code_1 in base_code:
            for i_code_2 in base_code:
                for i_code_3 in base_code:
                    # for i_code_4 in base_code:
                    #     url = i_code_1 + i_code_2 + i_code_3 + i_code_4
                    url = i_code_1 + i_code_2 + i_code_3
                    if len(url) > 2:
                        self.redis.lpush('urls', url)

    def use_elenium_phatomjs(self, request):
        driver = webdriver.PhantomJS(executable_path='/usr/local/Cellar/phantomjs/2.1.1/bin/phantomjs')
        driver.get(request.url)
        time.sleep(1)
        content = driver.page_source
        driver.quit()
        return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)

    def parse_items(self, htmlresponse):
        domain_item = DomainqueryItem()
        domain_item['domain_name'] = htmlresponse.xpath(
            '//div[@class="secQueryResult"]//strong/text()').extract_first()
        domain_item['domain_state'] = htmlresponse.xpath(
            '//div[@class="secQueryResult"]//span/text()').extract_first()
        try:
            print('～～～～～～～～' + domain_item['domain_name'] + domain_item['domain_state'])
        except TypeError:
            print('没获取的到')

        return domain_item
