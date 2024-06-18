from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, re, json

def scroll(driver, element):
    """
    Scroll down until the end of the page is reached
    """
    while True:
        # Get the current height of the element
        current_height = driver.execute_script("return arguments[0].scrollHeight", element)

        # Scroll down to the bottom of the element
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)

        # Wait for the page to load
        time.sleep(3)

        # Get the new height of the element
        new_height = driver.execute_script("return arguments[0].scrollHeight", element)

        # If the new height is the same as the current height, we have reached the end of the element
        if new_height == current_height:
            break


def parse(data_html):
    """
    Parse the data and store it in a JSON file
    """
    selected_data = data_html.find_all("div", class_="fontBodyMedium")
    end_data = []

    for item in selected_data:
        name = item.find('div', class_='fontHeadlineSmall')
        if not name:
            continue
        
        rating, reviews, cost = None, None, None
        rating_reviews_cost = item.find_all('span', attrs={'role': 'img'})

        if rating_reviews_cost:
            rating = float(rating_reviews_cost[0].get_text(separator=" ", strip=True)[:3])
            reviews = rating_reviews_cost[0].get_text(separator=" ", strip=True)
            reviews = int(re.search(r'\(([\d,]+)\)', reviews).group(1).replace(",", ""))
            if len(rating_reviews_cost) > 1:
                cost = rating_reviews_cost[1].get_text(separator=" ", strip=True)

        data = {
            'name': name.get_text(separator=" ", strip=True),
            'rating': rating,
            'reviews': reviews,
            'cost': cost
        }

        end_data.append(data)

    # add hiperlinks
    links = data_html.find_all('a')
    for i, link in enumerate(links[1:]):
        end_data[i]['link'] = link.get('href')

    # order by rating and reviews
    end_data = sorted(end_data, key=lambda x: x['reviews'] or 0, reverse=True)

    # save
    with open('output.json', 'w') as file:
        json.dump(end_data, file, indent=4)
    

def main():
    # set up
    options = Options()
    options.binary_location = '/usr/bin/brave-browser'
    service = Service(executable_path='/usr/local/bin/chromedriver-linux64/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)

    # url to scrape
    url = 'https://www.google.com/maps/search/gimnasio/@-31.5321897,-68.5461097,14z'

    # connect to url
    driver.get(url)
    element = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@role='feed']")))

    # scroll down the list
    scroll(driver, element)

    # retrieve html
    data_html = BeautifulSoup(element.get_attribute('innerHTML'), 'html.parser')
    parse(data_html)

    # close
    driver.close()


if __name__ == "__main__":
    main()