from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from ..items import ScrapebucketItem
from ..selenium_helpers import SeleniumHelper


class D2cmediaSpider(CrawlSpider):
    name = 'd2cmedia'
    domain_name = ''

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])
        pagination_selector = '//li[@class="divPaginationBox "]/@item-value'
        wait_until_selector = '//li[@class="divPaginationBox "]'
        pages = SeleniumHelper(f'{self.url}inventory.html?filterid=a1b13q0-10x0-0-0', pagination_selector, wait_until_selector).get_pagination()

        for page in range(pages):
            yield scrapy.Request(
                url=f'{self.url}inventory.html?filterid=a1b13q{page}-10x0-0-0',
                meta={'page': page + 1},
            )

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths='//div[@class="divSpan divSpan12 carBasics"]/a'),
            callback='parse_item',
            follow=True,
            process_request=lambda req, res: (req.meta.update({'page': res.meta['page']}), req)[1],
        ),
    )

    def parse_item(self, response):
        page = response.meta['page']
        vin1 = response.xpath('//span[@id="specsVin"]/text()').get()
        vin2 = response.xpath('//input[@id="expresscarvin"]/@value').get()
        vin = vin1 if vin1 else vin2

        loader = ItemLoader(item=ScrapebucketItem(), selector=response)
        loader.add_value('category', response.url)
        loader.add_value('vehicle_url', response.url)
        loader.add_xpath('year', '//input[@name="year"]/@value')
        loader.add_xpath('make', '//input[@name="make"]/@value')
        loader.add_xpath('model', '//input[@name="model"]/@value')
        loader.add_xpath('trim', '//input[@name="trim"]/@value')
        loader.add_xpath('unit', 'normalize-space(translate(//div[@class="makeModelYear"]/text(),"\u00A0",""))')
        loader.add_xpath('stock_number', '//span[@id="specsNoStock"]/text()')
        loader.add_value('vin', vin)
        loader.add_xpath('vin', '//input[@id="expresscarvin"]/@value')
        loader.add_xpath('price', '//input[@name="vehiclePrice"]/@value')
        loader.add_xpath('image_urls', '//li[@class="slide"]/a/@href')
        loader.add_value('images_count', len(response.xpath('//li[@class="slide"]/a/@href').getall()))
        loader.add_value('page', f'page {page}')
        loader.add_value('domain', self.domain_name)
        yield loader.load_item()
