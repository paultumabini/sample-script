from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from ..items import ScrapebucketItem


class CustomDrivenationSpider(CrawlSpider):
    name = 'custom_drivenation'
    allowed_domains = ['drivenation.ca']
    domain_name = ''

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543},
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])
        yield scrapy.Request(url=f'{self.url}vehicles')

    # vehicle urls
    link_extractor = LinkExtractor(restrict_xpaths='//div[@class="fwpl-item el-59qkfx"]/a')

    rules = (
        Rule(
            link_extractor,
            callback='parse_item',
            follow=True,
            process_request=lambda req, res: (req.meta.update({'page': res.url}), req)[1],
        ),
    )

    def parse_item(self, response):
        page = response.meta['page']

        images = response.xpath('//div[contains(@class,"wpgs_image")]/img/@data-large_image').getall()

        loader = ItemLoader(item=ScrapebucketItem(), selector=response)
        loader.add_value('vehicle_url', response.url)
        loader.add_xpath('year', 'normalize-space((//i[@class="far fa-calendar-alt"]/../text())[2])')
        loader.add_xpath(
            'model',
            'normalize-space(//div[@class="elementor-element elementor-element-e428650 elementor-widget elementor-widget-text-editor"]/div/text())',
        )
        loader.add_xpath(
            'trim',
            'normalize-space(//div[@class="elementor-element elementor-element-e428650 elementor-widget elementor-widget-text-editor"]/following::div/div/text())',
        )

        loader.add_xpath('stock_number', '//div[@data-id="6bb7827"]/div/text()')
        loader.add_xpath('vin', '//div[@data-id="d8244a1"]/div/text()')
        loader.add_xpath('price', '(//span[contains(@class,"woocommerce-Price-amount")]/bdi/span/../text())[1]')
        loader.add_value('image_urls', images)
        loader.add_value('images_count', len(images))
        loader.add_value('page', page)
        loader.add_value('domain', self.domain_name)
        yield loader.load_item()
