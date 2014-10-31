__author__ = 'couldtt'
import threading
from config import crawl_config, crawl_container, debug_container, remark_config
from bottle import route, run, jinja2_view
from storage import MongoStorage

DEBUG = True


class Crawl(threading.Thread):

    def __init__(self, type):
        crawler_name = type.capitalize() + "Crawler"
        crawler_module = __import__('LimitFreeCrawler')
        crawler_concrete = getattr(crawler_module, crawler_name)
        self.crawler = crawler_concrete(crawl_config[type])

    def run(self):
        try:
            res = self.crawler.start()
        except:
            res = {}
        return res

if DEBUG:
    crawl_container = debug_container

@route('/')
@jinja2_view('index.html', template_lookup=['views'])
def index():
    ms = MongoStorage()
    platforms = []
    for site in crawl_container:
        record = ms.get_today(site)
        if record:
            platform = record['platform']
            platforms.append(platform)
        else:
            crawl = Crawl(site)
            platform = crawl.run()
            ms.save(site, platform)
            platforms.append(platform)

    return {
        'platforms': platforms,
        'remarks': remark_config
    }

run(host='localhost', port=8080)