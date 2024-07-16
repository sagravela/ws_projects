import argparse
import json
import csv
import logging
from scrapy.crawler import CrawlerProcess
from scrapy_linkedin import JobSpider

class JobSearch:
    def __init__(self) -> None:
        # Initialize logging configuration
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        parser = argparse.ArgumentParser(description="Filter jobs based on the search term and optional additional keywords and save them.")
        parser.add_argument('-s', '--search', type=str, help='Job search keyword')
        parser.add_argument('-l', '--location', type=str, default='Argentina', help='Location to search jobs')
        parser.add_argument('-k', '--keywords', nargs= '+', help='Keywords to filter jobs')

        args = parser.parse_args()
        self.job = args.search
        self.location = args.location
        self.keywords = args.keywords

        # Scrape job links
        self.logger.info(f"Scraping job links for '{self.job}' in '{self.location}'...")
        # self.run_spider()

        # Filter jobs
        self.logger.info(f"Filtering jobs based on keywords: {', '.join(self.keywords)}...")
        self.filter_jobs()

    def run_spider(self):
        process = CrawlerProcess(settings={
            'FEEDS': {
                'output.json': {
                    'format': 'json',
                    'encoding': 'utf8',
                    'store_empty': False,
                    'fields': ['title', 'company', 'description', 'url'],
                    'indent': 4,
                },
            },
            # in order to see the performance of the spider 
            'LOG_LEVEL': 'INFO',  # Set the global log level

            'LOGGING': {
                'version': 1,
                'disable_existing_loggers': False,
                'loggers': {
                    'scrapy.core.scraper': {
                        'level': 'WARNING',
                    },
                },
            },
        })
        process.crawl(JobSpider, job=self.job, location=self.location)
        process.start()
        self.logger.info("Job scraping completed. Output saved to 'output.json'.")
        
    def filter_jobs(self):
        self.logger.info("Filtering jobs...")
        with open('output.json', 'r') as file:
            jobs = json.load(file)
        
        def filter_offer(x):
            return any(word.lower() in f"{x['title']} {x['description']}".lower() for word in self.keywords + [self.job])

        filtered_jobs = filter(filter_offer, jobs)

        with open('output_filtered.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['title', 'company', 'description', 'url'])
            writer.writeheader()
            for job in filtered_jobs:
                writer.writerow(job)
        
        self.logger.info(f"Filtered jobs saved to 'output_filtered.csv'.")
            
if __name__ == '__main__':
    JobSearch()
