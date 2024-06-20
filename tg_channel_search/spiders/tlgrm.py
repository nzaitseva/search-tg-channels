import re
import json
import urllib.parse

import scrapy
from tg_channel_search.items import TgChannelItem


# scrapy crawl tlgrm -a keyword=новости

class TlgrmRu(scrapy.Spider):
    name = 'tlgrm'
    start_urls = ['https://tlgrm.ru/channels']

    def __init__(self, keyword=None, *args, **kwargs):
        super(TlgrmRu, self).__init__(*args, **kwargs)
        self.keyword = keyword  # явно присваиваем ключевое слово
        self.typesense_api_key = ""

    def parse(self, response):
        # парсим ключ для запросов к api из html, возвращаемый на первый запрос
        typesense_api_key = re.search('typesense_api_key":"(.*=)"', response.text).groups()[0]
        self.typesense_api_key = typesense_api_key
        url = 'https://typesense.tlgrm.app/collections/channels/documents/search?'
        query_params = {'q': self.keyword,
                        'query_by': 'name,tags,link',
                        'per_page': 8,
                        'page': 1,
                        }
        url = url + urllib.parse.urlencode(query_params)
        request = scrapy.Request(url,
                                 callback=self.parse_search_results,
                                 headers={'x-typesense-api-key': self.typesense_api_key},

                                 )

        yield request

    def parse_search_results(self, response):
        json_res = json.loads(response.text)
        # парсим результаты в json
        channels = json_res['hits']
        for channel in channels:
            item = TgChannelItem(
                link=f'https://t.me/{channel['document']['link']}',
                name=channel['document']['name'],
                subscribers=channel['document']['subscribers']
            )
            yield item

        # если это первая страница с результатами, считаем сколько ещё страниц и запрашиваем остальные
        page_num = json_res['page']
        if page_num == 1:
            res_total = json_res['found']
            res_per_page = json_res['request_params']['per_page']
            for page in range(2, round(res_total / res_per_page) + 1):
                url = re.sub('&page=\d{1}', f'&page={page}', response.request.url)
                request = scrapy.Request(url,
                                         callback=self.parse_search_results,
                                         headers={'x-typesense-api-key': self.typesense_api_key},
                                         )
                yield request



