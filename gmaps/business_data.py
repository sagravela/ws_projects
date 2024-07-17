import argparse
import csv
import re
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BusinessData:
    def __init__(self, weight_reviews: float = 0.5, weight_stars: float = 0.5):
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Initializing the Business Data Scraper")
        
        self.parser = argparse.ArgumentParser(description="Get Business Data from Google Maps")
        self.parser.add_argument('-s', '--search', type=str, required=True, help='Search term')
        self.parser.add_argument('-a', '--url_area', type=str, required=True, help='URL with searching area')
        self.args = self.parser.parse_args()

        # Set up the Selenium WebDriver
        self.setup_driver()

        try:
            self.area = re.search(r'@([^z]+)z', self.args.url_area).group(1)
        except:
            self.logger.error("Invalid URL")
            exit(1)
        
        self.url = f'https://www.google.com/maps/search/{self.args.search}/@{self.area}z'
        self.logger.info(f"URL set to: {self.url}")

        self.weight_reviews = weight_reviews # popularity
        self.weight_stars = weight_stars # quality
        self.data = []

    def setup_driver(self):
        """Set up the Selenium WebDriver with Chrome options."""
        self.logger.info("Setting up the Selenium WebDriver")
        self.options = Options()
        self.options.binary_location = '/usr/bin/brave-browser'
        self.options.add_argument('--headless')
        self.service = Service(executable_path='/usr/local/bin/chromedriver-linux64/chromedriver')
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.wait = WebDriverWait(self.driver, 10)

    def scroll_to_end(self, element):
        """Scroll down until the end of the element is reached."""
        self.logger.info("Getting data")
        
        previous_height = self.driver.execute_script("return arguments[0].scrollHeight", element)
        
        while True:
            # Scroll to the bottom of the element
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)
            
            time.sleep(1) # for polite scrolling
            # Wait for the scroll height to change
            try:
                WebDriverWait(self.driver, 3).until(lambda driver: driver.execute_script("return arguments[0].scrollHeight", element) != previous_height)
            except:
                break

            # Update the previous height
            current_height = self.driver.execute_script("return arguments[0].scrollHeight", element)
            
            previous_height = current_height

    def parse_data(self, data_html):
        """Parse the HTML data and store it in a CSV file."""
        self.logger.info("Parsing the HTML data")
        anchors = data_html.find_all('a')

        for anchor in anchors:
            # discard any social media links
            if "https://www.google.com/maps/place/" not in anchor.get('href'):
                continue
            stars, reviews = None, None
            feedback = anchor.parent.find('span', attrs={'role': 'img'})
            if feedback:
                feedback = re.search(r'(\d+\.\d+)\s[a-zA-Z]+\s(\d+(?:,\d+)*)\s[a-zA-Z]+', feedback.get('aria-label'))
                try:
                    stars = float(feedback.group(1))
                    reviews = int(feedback.group(2).replace(',', ''))
                except:
                    pass
                
            business_data = {
                'name': anchor.get('aria-label'),
                'stars': stars,
                'reviews': reviews,
                'link': anchor.get('href')
            }

            self.data.append(business_data)

    def sort(self):
        """Calculate a weighted score for sorting businesses."""
        self.logger.info("Sorting the data")
        unsorted_data = self.data.copy()
        filtered_data = [x for x in unsorted_data if x['reviews'] is not None]
        max_reviews = max(filtered_data, key=lambda x: x['reviews'])['reviews']
        # avoid division by zero
        if max_reviews == 0:
            max_reviews = 1
        
        for i in range(len(unsorted_data)):
            unsorted_data[i]['score'] = 0
            stars = unsorted_data[i]['stars']
            reviews = unsorted_data[i]['reviews']
            if reviews and stars:
                unsorted_data[i]['score'] = ((reviews * self.weight_reviews) + (stars * self.weight_stars)) / max_reviews
        
        self.data = sorted(unsorted_data, key=lambda x: x['score'], reverse=True)

    def save(self):
        """Sort the data and save it to a CSV file."""
        csv_filename = f'{self.args.search}_{self.area}.csv'
        self.logger.info(f"Writing data to {csv_filename}")
        with open(csv_filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=self.data[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(self.data)
        self.logger.info(f"Data written to {csv_filename} successfully")

    def main(self):
        """Main method to scrape data and save it."""
        self.logger.info("Starting the main scraping process")
        try:
            self.driver.get(self.url)
            element = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@role='feed']")))
            
            self.scroll_to_end(element)

            # retrieve html, parse, sort and save
            data_html = BeautifulSoup(element.get_attribute('innerHTML'), 'html.parser')
            self.parse_data(data_html)
            self.sort()
            self.save()

            self.driver.close()
        except Exception as e: 
            self.logger.error(f"Error occurred: {e}")
            self.driver.close()


if __name__ == "__main__":
    # Initialize BusinessData class. Change weights parameters for customize sorting priority.
    run = BusinessData(weight_reviews=0.5, weight_stars=0.5)
    run.main()
