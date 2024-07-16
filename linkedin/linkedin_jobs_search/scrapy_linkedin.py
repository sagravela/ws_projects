import scrapy

class JobItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()


class JobSpider(scrapy.spiders.CrawlSpider):
    name = 'job'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 0.5,
        "AUTOTHROTTLE_DEBUG": True,

        "FEED_EXPORT_FIELDS ": ['title', 'company', 'description', 'url'],
    }
    allowed_domains = ['linkedin.com']
    rules = (
        scrapy.spiders.Rule(
            scrapy.linkextractors.LinkExtractor(restrict_css='a.base-card__full-link'),
            callback='parse',
            follow=True
        ),
    )


    def __init__(self, job: str = None, location: str =None, *args, **kwargs):
        super(JobSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://www.linkedin.com/jobs/search?keywords={job.replace(" ", "%20")}&location={location}']


    def parse(self, response):
        items = JobItem()
        items['title'] = response.css('h1.top-card-layout__title::text').get()
        items['company'] = response.css('a.topcard__org-name-link::text').get().strip()
        items['description'] = response.xpath('string(//div[contains(@class, "show-more-less-html__markup")])').get().strip()
        items['url'] = response.url
        yield items
