from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import os, time
import argparse


# set up
options = Options()
options.binary_location = '/usr/bin/brave-browser'
options.add_argument("--start-maximized")
options.add_argument("--headless")
service = Service(executable_path='/usr/local/bin/chromedriver-linux64/chromedriver')
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)


def main():
    parser = argparse.ArgumentParser(description="Filter Linkedin jobs based on keywords and save them in your Linkedin account.")
    parser.add_argument('-u', '--user', type=str, required=True, help='Linkedin User')
    parser.add_argument('-p', '--password', type=str, required=True, help='Linkedin Password')
    parser.add_argument('-s', '--search', type=str, help='Job search keyword')
    parser.add_argument('-l', '--location', type=str, default='Argentina', help='Location to search jobs')
    parser.add_argument('-k', '--keywords', nargs= '+', required=True, help='Keywords to filter jobs')

    args = parser.parse_args()

    # login
    login(user= args.user, password= args.password)

    # scrape job links
    job_links_scrapping(args.search, args.location)

    # read job links
    jobs_links = list()
    with open('links.txt', 'r') as file:
        for link in file:
            jobs_links.append(link[:-2])            

    # offer scrapping
    offers_y, offers_n, offers_e = offer_selection(jobs_links, args.keywords)

    print("offers saved:", len(offers_y), "from ", len(jobs_links))
    print("offers not saved:", len(offers_n), "from ", len(jobs_links))
    print("error offers:", f"[{len(offers_e)}]", offers_e)
    
    # close
    driver.close()


def login(user: str, password: str):
    # connect to linkedin
    driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')

    # login
    user_login = wait.until(EC.visibility_of_element_located((By.NAME, "session_key")))
    user_pass = wait.until(EC.visibility_of_element_located((By.NAME, "session_password")))
    user_login.send_keys(user)
    user_pass.send_keys(password)
    driver.find_element(By.CSS_SELECTOR,'button[type="submit"]').click()


def job_links_scrapping(search: str, location: str) -> list:
    jobs = "https://www.linkedin.com/jobs/"

    driver.get(jobs)

    search_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Search by title, skill, or company"]')))
    search_input.clear()
    search_input.send_keys(search)
    search_input.send_keys(Keys.ENTER)

    location_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[aria-label="City, state, or zip code"]')))
    location_input.clear()
    location_input.send_keys(location)
    location_input.send_keys(Keys.ENTER)

    # loop along all the jobs pages
    links = list()
    while True:
        try:
            links_len_before = len(links)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.job-card-container__link')))
            source = BeautifulSoup(driver.page_source, 'html.parser')
  
            for link in source.select('a.job-card-container__link'):
                links.append("https://www.linkedin.com" + link.get('href'))

            break
            # if no new links were added then break
            if len(links) == links_len_before or len(links) > 5:
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


def offer_selection(links: list, keywords: list):
    no_offers, yes_offers, error_offers = list(), list(), list()

    for link in tqdm(links):
        try:
            driver.get(link)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.jobs-box__html-content")))
            offer = BeautifulSoup(driver.page_source, 'html.parser')
            description = offer.find('div', class_="jobs-box__html-content").get_text()

            # check conditions within description to ensure you want to apply to this offer
            if any(word in description.lower() for word in keywords):
                save_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.mt5 button.jobs-save-button")))
                
                # if it's already saved, skip
                if "Saved" in save_button.text:
                    continue
                # save offer clicking on Save button
                # driver.execute_script("arguments[0].click();", save_button)
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
