import json
import math
from urllib.parse import urlparse

import scrapy
from scrapy.loader import ItemLoader

from ..items import ScrapebucketItem


class TadvantageSpider(scrapy.Spider):
    name = 'tadvantage'
    base_url_api = f'wp-content/plugins/convertus-vms/include/php/ajax-vehicles.php?endpoint=https%3A%2F%2Fvms.prod.convertus.rocks%2Fapi%2Ffiltering%2F%3Fcp%3D2509%26ln%3Den%26pg%3D'
    new_query_params_ext = f'%26pc%3D15%26dc%3Dtrue%26qs%3D%26im%3D%26svs%3D%26sc%3Dnew%26v1%3DPassenger%2520Vehicles%26st%3Dyear%252Casc%26ai%3Dtrue%26oem%3DFord%26mk%3D%26md%3D%26tr%3D%26od%3D%26bs%3D%26tm%3D%26dt%3D%26cy%3D%26ec%3D%26mc%3D%26ic%3D%26pa%3D%26ft%3D%26eg%3D%26v2%3D%26v3%3D%26fp%3D%26fc%3D%26fn%3D%26tg%3DInventoryTagSale%26pnpi%3Dmsrp%26pnpm%3Dnone%26pnpf%3Dinte%26pupi%3Dnone%26pupm%3Dnone%26pupf%3Dinte%26nnpi%3Dnone%26nnpm%3Dnone%26nnpf%3Dnone%26nupi%3Dnone%26nupm%3Dnone%26nupf%3Dnone%26po%3Dfixed&action=vms_data'
    used_query_params_ext = f'%26pc%3D15%26dc%3Dtrue%26qs%3D%26im%3D%26svs%3D%26sc%3Dused%26v1%3DPassenger%2520Vehicles%26st%3Dyear%252Cdesc%26ai%3Dtrue%26oem%3DFord%26mk%3D%26md%3D%26tr%3D%26od%3D%26bs%3D%26tm%3D%26dt%3D%26cy%3D%26ec%3D%26mc%3D%26ic%3D%26pa%3D%26ft%3D%26eg%3D%26v2%3D%26v3%3D%26fp%3D%26fc%3D%26fn%3D%26tg%3D%26pnpi%3Dmsrp%26pnpm%3Dnone%26pnpf%3Dinte%26pupi%3Dnone%26pupm%3Dnone%26pupf%3Dinte%26nnpi%3Dnone%26nnpm%3Dnone%26nnpf%3Dnone%26nupi%3Dnone%26nupm%3Dnone%26nupf%3Dnone%26po%3Dfixed&action=vms_data'
    page = 1
    domain_name = ''

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543},
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])
        yield scrapy.Request(
            url=f'{self.url}{self.base_url_api}{self.page}{self.new_query_params_ext}',
            callback=self.parse,
        )
        yield scrapy.Request(
            url=f'{self.url}{self.base_url_api}{self.page}{self.used_query_params_ext}',
            callback=self.parse,
        )

    def parse(self, response):
        json_res = json.loads(response.body)
        parsed_data = json_res.get('results')

        for result in parsed_data:
            loader = ItemLoader(ScrapebucketItem())
            images = [image.get('image_original') for image in result.get('image')]
            loader.add_value('category', result.get('sale_class'))
            loader.add_value('year', result.get('year'))
            loader.add_value('make', result.get('make'))
            loader.add_value('model', result.get('model'))
            loader.add_value('trim', result.get('trim'))
            loader.add_value('stock_number', result.get('stock_number'))
            loader.add_value('vin', result.get('vin'))
            loader.add_value('vehicle_url', result.get('vdp_url'))
            loader.add_value('price', result.get('asking_price'))
            loader.add_value('image_urls', images)
            loader.add_value('images_count', len(images))
            loader.add_value('domain', self.domain_name)
            yield loader.load_item()

        pages = json_res.get('summary').get('total_vehicles')
        page_limit = math.ceil(pages / 15)

        if not self.page > page_limit:
            self.page += 1
            yield scrapy.Request(
                url=f'{self.url}{self.base_url_api}{self.page}{self.new_query_params_ext}',
                callback=self.parse,
            )

            yield scrapy.Request(
                url=f'{self.url}{self.base_url_api}{self.page}{self.used_query_params_ext}',
                callback=self.parse,
            )
