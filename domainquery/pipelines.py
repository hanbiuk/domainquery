# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import redis
from domainquery.settings import redis_host, redis_port
import codecs
import json


class DomainqueryPipeline(object):
    def __init__(self):
        host = redis_host
        port = redis_port
        self.pool = redis.ConnectionPool(host=host, port=port, decode_responses=True, db=3)
        self.redis = redis.Redis(connection_pool=self.pool)

        self.file = codecs.open('domain_registered.json', mode='a', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(line)

        try:
            if '已注册' in item['domain_state']:
                print(item['domain_name'] + '已经注册了！')
            else:
                self.redis.hset('canget_urls', item['domain_name'], item['domain_state'])
        except TypeError:
            pass
        
        return item
