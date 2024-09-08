# tg_channel_search

Парсер на Scrapy, который ищет телеграм-каналы на tlgrm.ru и tgramsearch.ru, по ключевому слову и сохраняет в CSV файл название канала, ссылку и количество подписчиков.


Например:

```scrapy crawl tlgrm -a keyword=новости```
```scrapy crawl tgramsearch -a keyword=новости```

_Todo: добавить больше источников._
