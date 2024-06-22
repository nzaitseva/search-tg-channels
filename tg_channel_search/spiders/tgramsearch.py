import re
from urllib.parse import urljoin

import scrapy
from tg_channel_search.items import TgramsearchItem


# scrapy crawl tlgrm -a keyword=новости -o дизайн.csv

class TgramsearchSpider(scrapy.Spider):
    name = "tgramsearch"
    custom_settings = {
        'FEED_EXPORT_FIELDS': ['name', 'link', 'subscribers']
    }

    def __init__(self, keyword=None, *args, **kwargs):
        super(TgramsearchSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f"https://tgramsearch.com/?q={keyword}"]

    def parse(self, response):
        if not response.css('div.search-notfound'): # если есть результаты
            for link in response.css('div.tg-channel-link a::attr(href)'):
                url =  urljoin(response.url, link.get())
                yield scrapy.Request(url, callback=self.parse_channel_info)

            # если мы на первой странице с результатами и есть пагинация, обойти пагинацию
            current_page = int(response.css('.tg-pager-wrapper .tg-pager .tg-pager-li.is-current::text').get())
            if current_page == 1:
                pages_total = int(response.css('ul.tg-pager li a::text')[-1].get())
                if len(pages_total) > 1:
                    for page in range(2,pages_total+1):
                        url = f'{response.url}&page={page}'
                        yield scrapy.Request(url, callback=self.parse)


    def parse_channel_info(self,response):
        link = response.css('.tg-channel-link a::attr(href)').get()
        link = re.sub('.*domain=', 'https://t.me/', link)
        name = response.css('.tg-channel-header a::text').get()
        description = response.css('.tg-channel-description::attr(title)').get()
        categories = ','.join(list(set(response.css('div.tg-channel-categories a::text').getall())))
        subscribers = response.css('span.tg-user-count::text').get()

        item = TgramsearchItem(
            link = link,
            name = name,
            description = description,
            categories = categories,
            subscribers = subscribers
        )
        yield item
