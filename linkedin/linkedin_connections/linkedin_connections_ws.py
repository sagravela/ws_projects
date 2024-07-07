from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import time
import csv
from dotenv import load_dotenv
import urllib.parse

# login credentials
load_dotenv()

# Access the environment variables
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

# set up
options = Options()
options.binary_location = '/usr/bin/brave-browser'
service = Service(executable_path='/usr/local/bin/chromedriver-linux64/chromedriver')
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

def main():
    # login
    user_url = login()

    # get connections
    first_contacts = get_first_connections(user_url)
    
    # get second connections
    second_connections = []
    for name, _, link in tqdm(first_contacts):
        second_connections.append({name : get_second_connections(link)})
    
    # save
    with open('first_connections.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        for name, occ, link in first_contacts:
            writer.writerow([name, occ, link])
    
    with open('second_connections.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        for c in second_connections:
            owner = list(c.keys())[0]
            writer.writerow(["Owner", "Name", "Occupation", "Link profile", "Place"])
            for dic in c[owner]:
                writer.writerow([owner, dic['name'], dic['occupation'], dic['link_profile'], dic['place']])
    
    # close
    driver.close()


def login() -> str:
    # connect to linkedin
    driver.get('https://www.linkedin.com/home')
    driver.implicitly_wait(5)

    # login
    user_login = driver.find_element(By.NAME, "session_key")
    user_pass = driver.find_element(By.NAME, "session_password")
    user_login.send_keys(USERNAME)
    user_pass.send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, 
                        'button.btn-md.btn-primary.flex-shrink-0[data-id="sign-in-form__submit-btn"]').click()

    # retrive user url
    path = "div.scaffold-layout__sidebar div.feed-identity-module__actor-meta a"
    element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, path)))
    user_url = element.get_attribute("href")

    return user_url


def to_connections_page(url: str) -> None:
    # search linkedin profile
    driver.get(url)

    # get connections
    profile_loc = 'ul.pv-top-card--list-bullet li.text-body-small a'
    profile = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,profile_loc)))
    profile.click()


def scroll():
    # Scroll down until the end of the page is reached
    while True:
        # Get the current height of the page
        current_height = driver.execute_script("return document.body.scrollHeight")

        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for the page to load
        time.sleep(2)

        # Get the new height of the page
        new_height = driver.execute_script("return document.body.scrollHeight")

        # If the new height is the same as the current height, we have reached the end of the page
        if new_height == current_height:
            break

def get_first_connections(url: str) -> list:
    # to connections page
    to_connections_page(url)

    # wait
    list_connection = 'li.mn-connection-card'
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,list_connection)))

    scroll()

    # now retrieve fully list of contacts
    connections_loc = 'div.scaffold-finite-scroll__content ul'
    connections = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,connections_loc)))

    soup = BeautifulSoup(connections.get_attribute("outerHTML"), 'html.parser')

    f_contacts = []

    # get names, occupations and links for each contact in html
    links = soup.find_all('a', class_='mn-connection-card__link')
    names = soup.find_all('span', class_='mn-connection-card__name')
    occupation = soup.find_all('span', class_='mn-connection-card__occupation')
    for name, occ, link in zip(names, occupation, links):
        # Decoding the encoded path
        decoded_link = urllib.parse.unquote(link.get('href'))
        
        # save contact
        f_contacts.append((name.get_text().strip(), 
                        occ.get_text().strip(), 
                        "https://www.linkedin.com" + decoded_link))

    return f_contacts


def get_second_connections(url: str) -> list:
    # to connections page
    to_connections_page(url)

    s_contacts = []
    html = ""

    while True:
        # now retrieve fully list of contacts
        connections_loc = 'div.search-results-container ul.reusable-search__entity-result-list'
        connections = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,connections_loc)))
        html += connections.get_attribute("outerHTML")
    
        scroll()
        
        # next page or exit if all connections were retrieved
        next_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[class*='artdeco-pagination__button--next']")))
        if next_button.is_enabled():
            next_button.click()
        else:
            break

    soup = BeautifulSoup(html, 'html.parser')

    # Extract names, occupations, connection types, link profiles, and places from the HTML
    name_conn_link = soup.find_all('span', class_='entity-result__title-text')
    occupations = soup.find_all('div', class_='entity-result__primary-subtitle')
    places = soup.find_all('div', class_='entity-result__secondary-subtitle')

    for first, occ, place in zip(name_conn_link, occupations, places):
        text = first.get_text().strip()
        
        contact = {
            'name': text.split("View")[0],
            'occupation': occ.get_text().strip(),
            'link_profile': urllib.parse.unquote(first.find('a')['href']),
            'place': place.get_text().strip()
        }
        s_contacts.append(contact)

    return s_contacts


if __name__ == "__main__":
    main()
