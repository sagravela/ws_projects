from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from tqdm import tqdm
import os, time

# login credentials
load_dotenv()

# Access the environment variables
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

# job to search
SEARCH = ["data scientist", "data science", "ciencia de datos", "científico de datos"]

# set up
options = Options()
options.binary_location = '/usr/bin/brave-browser'
service = Service(executable_path='/usr/local/bin/chromedriver-linux64/chromedriver')
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

def main():
    # login
    login()

    # scrape job links
    job_links_scrapping()

    # read job links
    jobs_links = list()
    with open('links.txt', 'r') as file:
        for link in file:
            jobs_links.append(link[:-2])            

    # offer scrapping
    offers_y, offers_n, offers_e = offer_selection(jobs_links)

    print("offers saved:", len(offers_y), "from ", len(jobs_links))
    print("offers not saved:", len(offers_n), "from ", len(jobs_links))
    print("error offers:", f"[{len(offers_e)}]", offers_e)
    
    # close
    driver.close()


def login():
    # connect to linkedin
    driver.get('https://www.linkedin.com/home')

    # login
    user_login = wait.until(EC.visibility_of_element_located((By.NAME, "session_key")))
    user_pass = wait.until(EC.visibility_of_element_located((By.NAME, "session_password")))
    user_login.send_keys(USERNAME)
    user_pass.send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR,'button[data-id="sign-in-form__submit-btn"]').click()


def job_links_scrapping() -> list:
    jobs = "https://www.linkedin.com/jobs/"

    driver.get(jobs)

    input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input.jobs-search-box__text-input')))
    input.send_keys(SEARCH[0])
    input.send_keys(Keys.ENTER)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.scaffold-layout__list-container')))
    url = driver.current_url
    url = url.replace('refresh=true', 'refresh=false')
    driver.get(url)
    # loop along all the jobs pages
    links = list()

    while True:
        try:
            links_len_before = len(links)
            search = BeautifulSoup(driver.page_source, 'html.parser')

            for link in search.select('a.job-card-container__link'):
                links.append("https://www.linkedin.com" + link.get('href'))

            # if no new links were added then break
            if len(links) == links_len_before:
                break

            # go to next page
            driver.get(url + '&start=' + str(len(links)))
        except Exception as e:
            print("An error occurred", e)
            break
    
        time.sleep(2)

    # save job links
    with open('links.txt', 'w') as file:
        for link in links:
            file.write(link.split('?')[0] + '\n')


def offer_selection(links: list):
    no_offers, yes_offers, error_offers = list(), list(), list()

    for link in tqdm(links):
        try:
            driver.get(link)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.jobs-box__html-content")))
            offer = BeautifulSoup(driver.page_source, 'html.parser')
            description = offer.find('div', class_="jobs-box__html-content").get_text()

            # check conditions within description to ensure you want to apply to this offer
            if any(word in description.lower() for word in SEARCH):
                save_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.mt5 button.jobs-save-button")))
                
                # if it's already saved, skip
                if "Saved" in save_button.text:
                    continue
                # save offer clicking on Save button
                driver.execute_script("arguments[0].click();", save_button)
                yes_offers.append(link)
            else:
                no_offers.append(link)

        except:
            error_offers.append(link)
            continue

        time.sleep(2)
    
    return yes_offers, no_offers, error_offers
 

if __name__ == '__main__':
    main()
