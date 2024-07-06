import scrapy
from collections import OrderedDict

class MLSearchItem(scrapy.Item):
    fields = OrderedDict([
        ('title', scrapy.Field()),
        ('price', scrapy.Field()),
        ('reviews', scrapy.Field()),
        ('score', scrapy.Field()),
        ('link', scrapy.Field())
    ])

class MLSearchSpider(scrapy.Spider):
    name = "MLsearch"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    next_page_start = 0

    def __init__(self, product="", number_of_items=1000, score=4.5, reviews=1000, *args, **kwargs):
        super(MLSearchSpider, self).__init__(*args, **kwargs)
        self.number_of_items = int(number_of_items)
        self.score = float(score)
        self.reviews = int(reviews)
        self.start_urls = ["https://listado.mercadolibre.com.ar/" + product]

    def parse(self, response):
        items_list = response.css("li.ui-search-layout__item")
        self.next_page_start += len(items_list)

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

            if reviews < self.reviews or score < self.score:
                continue

            item = MLSearchItem()
            item['title'] = item_data.css("h2.ui-search-item__title::text").get()
            item['reviews'] = reviews
            item['score'] = score
            item['link'] = item_data.css("a.ui-search-link::attr(href)").get()
            price = item_data.css("span.andes-money-amount__fraction::text").get()
            item['price'] = float(price)
            yield item

        if self.next_page_start < self.number_of_items:
            next_page = f"{self.start_urls[0]}_Desde_{self.next_page_start}_NoIndex_True"
            yield response.follow(next_page, callback=self.parse)

