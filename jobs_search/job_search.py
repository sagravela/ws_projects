import argparse
import json
import csv
import logging
from scrapy.crawler import CrawlerProcess
from linkedin_spider import LinkedinSpider

class JobSearch:
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(description="Filter jobs based on a role and optionally additional keywords. Then save it as 'filtered_jobs_offers.csv'.")
        parser.add_argument('-s', '--search', type=str, required=True, help='Job search keyword')
        parser.add_argument('-l', '--location', type=str, required=True, help='Location to search jobs')
        parser.add_argument(
            '-k',
            '--keywords', 
            nargs= '+',
            help='Additional keywords to filter offers. It will select offers if ANY of the job + keywords are in the title + description job offer.'
        )

        args = parser.parse_args()
        self.job = args.search
        self.location = args.location
        self.keywords = args.keywords

        # Set up Scrapy process
        process = CrawlerProcess(settings={
            'FEEDS': {
                'jobs_offers.json': {
                    'format': 'json',
                    'encoding': 'utf8',
                    'overwrite': True,
                    'store_empty': False,
                    'fields': ['title', 'company', 'place', 'description', 'url'],
                    'indent': 4,
                },            
            },
            'LOG_LEVEL': 'INFO',  # Set the global log level to INFO
        })

        # Linkedin spider
        process.crawl(LinkedinSpider, job=self.job, location=self.location)
        # Add more spiders ...

        # Start the crawler
        process.start()
        
        # Filter jobs
        logging.info(f"Filtering jobs based on keywords: {self.job}, {', '.join(self.keywords)}.")
        self.save_filtered_jobs(self.filter_jobs())
        
    def filter_jobs(self):
        with open('jobs_offers.json', 'r') as file:
            jobs = json.load(file)
        
        def filter_offer(x):
            return any(word.lower() in f"{x['title']} {x['description']}".lower() for word in self.keywords + [self.job])

        return filter(filter_offer, jobs)

    def save_filtered_jobs(self, filtered_jobs):
        with open('filtered_jobs_offers.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['title', 'company', 'place', 'description', 'url'])
            writer.writeheader()
            for job in filtered_jobs:
                writer.writerow(job)
        
        logging.info(f"Filtered jobs saved to filtered_jobs_offers.csv")
            
if __name__ == '__main__':
    JobSearch()