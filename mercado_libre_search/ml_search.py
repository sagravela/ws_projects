import scrapy
import json

class MLSearchSpider(scrapy.Spider):
    """
    Scrape Mercado Libre Search

    Example of usage:
    scrapy runspider ml_search.py -a start_url='https://listado.mercadolibre.com.ar/belleza-cuidado-personal/artefactos-cabello/cortadoras-pelo/maquina-cortar-pelo' -a number_of_items=1000 -a score=4.5 -a reviews=1000
    """
    name = "MLsearch"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    next_page_start = 0
    scraped_data = []

    def __init__(self, start_url="", number_of_items=1000, score=4.5, reviews=1000, *args, **kwargs):
        """
        Args:
            start_url (str): URL to start scraping from
            number_of_items (int): Number of items to scrape
            score (float): Minimum score
            reviews (int): Minimum number of reviews
        """
        super(MLSearchSpider, self).__init__(*args, **kwargs)
        self.number_of_items = int(number_of_items)
        self.score = float(score)
        self.reviews = int(reviews)
        self.start_urls = [start_url]

    
    def scrape_data(self, data):
        """
        Args:
            data (list): List of items to scrape
        """
        if not data:
            return
        for item in data:  
            review_score_element = item.css("div.ui-search-reviews span.andes-visually-hidden::text").get()

            if not review_score_element:
                continue

            reviews = int(review_score_element.split()[-2].replace(",", ""))
            score = float(review_score_element.split()[1])
            if reviews < self.reviews or score < self.score:
                continue
            
            data = {
                "reviews": reviews,
                "score": score,
                "link": item.css("a.ui-search-link::attr(href)").get()
            }

            self.scraped_data.append(data)

    
    def clean_save(self):
        """
        Clean and save data
        """
        indexes = list()
        items = self.scraped_data.copy()
        score_reviews = [(x['score'], x['reviews']) for x in items]
        for i, item in enumerate(self.scraped_data):
            if i in indexes:
                continue
            for j, next_item in enumerate(score_reviews):
                if (item['score'], item['reviews']) == next_item and j > i:
                    indexes.append(j)

        items = [item for i, item in enumerate(items) if i not in indexes]

        items.sort(key=lambda x: (x['score'], x['reviews']), reverse=True)

        # Save results
        with open('output.json', 'w') as f:
            json.dump(items, f, indent=4)


    def parse(self, response):
        """
        Args:
            response (Response): Response object
        """
        items_list = response.css("li.ui-search-layout__item")
        self.next_page_start += len(items_list)

        self.scrape_data(items_list)

        # Go to next page
        next_page = f"{self.start_urls[0]}_Desde_{self.next_page_start}_NoIndex_True"
        
        if self.next_page_start < self.number_of_items:
            yield response.follow(next_page, callback=self.parse)
        
        self.clean_save()
            