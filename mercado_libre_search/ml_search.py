import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from ml_spider import MLSearchSpider

def main():
    parser = argparse.ArgumentParser(description="Search for a product in Mercado Libre and save the results.")
    parser.add_argument('-p', '--product', type=str, required=True, help='Product to search for')
    parser.add_argument('-s', '--stars', type=float, default=4.5, help='Minimum stars')
    parser.add_argument('-r', '--reviews', type=int, default=1000, help='Minimum number of reviews')
    parser.add_argument('-f', '--format', type=str, default='json', help='Output format available in Scrapy')

    args = parser.parse_args()

    settings = get_project_settings()
    settings.set('FEEDS', {
        f'output.{args.format}': {
            'format': args.format,
            'encoding': 'utf8',
            'fields': ['title', 'stars', 'reviews', 'price_ars', 'link'],
            'overwrite': True,
            'store_empty': True,
            'indent': 4,
        },
    })

    process = CrawlerProcess(settings)
    process.crawl(MLSearchSpider, product=args.product, score=args.stars, reviews=args.reviews)
    process.start()

if __name__ == "__main__":
    main()
