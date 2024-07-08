import scrapy


class MLSearchItem(scrapy.Item):
    title = scrapy.Field()
    stars = scrapy.Field()
    reviews = scrapy.Field()
    price_ars = scrapy.Field()
    link = scrapy.Field()

class MLSearchSpider(scrapy.spiders.CrawlSpider):
    name = "MLsearch"
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    allowed_domains = ["listado.mercadolibre.com.ar"]
    item_scraped = 0
    
    rules = (
        scrapy.spiders.Rule(
            scrapy.linkextractors.LinkExtractor(allow=r'_Desde_'),
            callback='parse',
            follow=True
        ),
    )

    def __init__(self, product="", stars=4.5, reviews=1000, *args, **kwargs):
        super(MLSearchSpider, self).__init__(*args, **kwargs)
        self.stars = float(stars)
        self.reviews = int(reviews)
        self.start_urls = ["https://listado.mercadolibre.com.ar/" + product]

    def parse(self, response):
        items_list = response.css("li.ui-search-layout__item")
        self.item_scraped += len(items_list)

        for item_data in items_list:
            review_score_element = item_data.css("div.ui-search-reviews span.andes-visually-hidden::text").get()

            if not review_score_element:
                continue

            review_score_parts = review_score_element.split()
            try:
                reviews = int(review_score_parts[-2].replace(",", ""))
                score = float(review_score_parts[1])
            except (ValueError, IndexError):
                continue

            if reviews < self.reviews or score < self.stars:
                continue

            item = MLSearchItem()
            item['title'] = item_data.css("h2.ui-search-item__title::text").get()
            item['reviews'] = reviews
            item['stars'] = score
            item['link'] = item_data.css("a.ui-search-link::attr(href)").get()
            price = item_data.css("span.andes-money-amount__fraction::text").get()
            item['price_ars'] = float(price)
            yield item
