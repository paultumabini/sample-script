import pytz
from apscheduler.schedulers.twisted import TwistedScheduler
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import defer, reactor

from scrapebucket.urls_crawl import match_spiders, scrapes_model, target_sites_model

configure_logging()
settings = get_project_settings()
runner = CrawlerRunner(settings)


@defer.inlineCallbacks
def crawl():
    """
    Query spiders and target urls from database.
    Run spiders sequentially.
    Spiders are by template to dynamically crawl to their respective target sites.
    Optional: previous scrapes are removed for limited database storage.
    """
    for results in match_spiders(target_sites_model, settings):
        for spider, url, domain in results:
            scrapes_prev = target_sites_model.objects.filter(primary_key__exact=domain).first().scrapes.all()
            if scrapes_prev.count():
                scrapes_prev.delete()
            yield runner.crawl(spider, url=url)
            print(f'Done executing: {spider.__name__}')
    reactor.stop()


if __name__ == '__main__':
    """Optional: scheduling job"""
    scheduler = TwistedScheduler(timezone=pytz.timezone('Asia/Manila'))
    scheduler.add_job(crawl, trigger='cron', hour='2', minute='25')
    scheduler.start()
    reactor.run()
