import scrapy

class JobItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    place  = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()


class LinkedinSpider(scrapy.spiders.CrawlSpider):
    name = 'Linkedin Spider'
    custom_settings = {
        # PERFORMANCE SETTINGS
        # Tune this parameters in order to accelerate the crawling process.
        # More information: https://docs.scrapy.org/en/latest/topics/settings.html
        'DOWNLOAD_DELAY': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'AUTOTHROTTLE_DEBUG': False,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [429], # 429: Too Many Requests
        'METAREFRESH_ENABLED': False, # Disable MetaRefresh to avoid redirections

        # LOGGING SETTINGS
        'LOG_LEVEL': 'INFO',

        # FEED SETTINGS
        'FEED_EXPORT_FIELDS': ['title', 'company', 'place', 'description', 'url'],
    }
    allowed_domains = ['linkedin.com']
    rules = (
        scrapy.spiders.Rule(
            scrapy.linkextractors.LinkExtractor(restrict_css='a.base-card__full-link', allow= r'/jobs'),
            callback='parse',
        ),
    )

    def __init__(self, job: str = None, location: str =None, *args, **kwargs):
        super(LinkedinSpider, self).__init__(*args, **kwargs)
        url = f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={job.replace(" ", "%20")}&location={location}&geoId=&trk=public_jobs_jobs-search-bar_search-submit&start='
        self.start_urls = [url + str(i) for i in range(0, 1000, 25)] # 1000 is the limit of offers showed by Linkedin

    def parse(self, response):
        # scrapy.shell.inspect_response(response, self)
        items = JobItem()
        items['title'] = response.css('h1.top-card-layout__title::text').get(default='').strip()
        items['company'] = response.css('a.topcard__org-name-link::text').get(default='').strip() 
        items['place'] = response.css('span.topcard__flavor--bullet::text').get(default='').strip() 
        items['description'] = response.xpath('string(//div[contains(@class, "show-more-less-html__markup")])').get(default='').strip()
        items['url'] = response.url
        yield items
