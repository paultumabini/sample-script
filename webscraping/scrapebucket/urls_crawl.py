import os
import sys
from pathlib import Path

import django
from scrapy import spiderloader

sys.path.append(os.path.join(Path(__file__).parents[2], 'webscraping'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'webscraping.settings'
django.setup()

from project.models import Scrape, SpiderLog, TargetSite

target_sites_model, scrapes_model, spiderlogs_model = (TargetSite, Scrape, SpiderLog)


def get_urls(sites, classes):
    """prepare crawlers with their corresponding target urls into a list i.e,  [<spider>, <url>]"""
    for spider, class_name in classes:
        objects = sites.objects.filter(spider=spider).all()
        for obj in objects:
            if obj.spider == spider:
                yield [class_name, obj.site_url, obj.primary_key]


def match_spiders(target_sites, settings):
    """get all spiders and spider classes"""
    spider_loader = spiderloader.SpiderLoader.from_settings(settings)
    spiders = spider_loader.list()
    spider_classes = [[name, spider_loader.load(name)] for name in spiders]
    yield get_urls(target_sites, spider_classes)
