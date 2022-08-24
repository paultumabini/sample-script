# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter import ItemAdapter

from scrapebucket.urls_crawl import scrapes_model, target_sites_model


class ScrapebucketPipeline:
    def process_item(self, item, spider):
        """save scraped items to database"""
        items = ItemAdapter(item)
        domain_name = items.get('domain').split('.')[0]
        target_site_pk = target_sites_model.objects.filter(primary_key__iexact=domain_name).first().pk

        scrape_data = {
            'target_site_id': target_site_pk,
            'spider': spider.name,
            'category': items.get('category'),
            'unit': items.get('unit'),
            'year': items.get('year'),
            'make': items.get('make'),
            'model': items.get('model'),
            'trim': items.get('trim'),
            'stock_number': items.get('stock_number'),
            'vin': items.get('vin'),
            'vehicle_url': items.get('vehicle_url'),
            'msrp': items.get('msrp'),
            'price': items.get('price'),
            'selling_price': items.get('selling_price'),
            'rebate': items.get('rebate'),
            'image_urls': items.get('image_urls'),
            'images_count': items.get('images_count'),
            'page': items.get('page'),
        }
        scrapes = scrapes_model(**scrape_data)
        scrapes.save()

        return item
