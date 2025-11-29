from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from urllib.parse import unquote
import time

executable_path = "./driver/chromedriver"

def setup_driver():
    options = webdriver.ChromeOptions()
    return webdriver.Chrome(service=Service(executable_path), options=options)

def scrape_libre(driver):
    url = 'https://libre.ge/productebi'
    driver.get(url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p-md-4")))

    # -------- SCROLL TO LOAD ALL PRODUCTS --------
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # -------- FIND ALL PRODUCT CARDS --------
    product_cards = driver.find_elements(By.CSS_SELECTOR, "div.p-md-4 .col-xl-2")
    data = []

    for card in product_cards:
        try:
            title_element = card.find_element(
                By.CSS_SELECTOR,
                ".product_card__title .line_2"
            )

            title = title_element.text.strip()
        except:
            title = None

        try:
            # --- New price: Lari ---
            new_price_lari = card.find_element(
                By.CSS_SELECTOR, "div.product_card__new_price_lari"
            ).text.strip()

            # --- New price: Tetri ---
            new_price_tetri = card.find_element(
                By.CSS_SELECTOR, "div.product_card__new_price_tetri"
            ).text.strip()

            # Combine into a proper decimal price
            new_price = f"{new_price_lari}.{new_price_tetri}"
        except:
            new_price = None

        try:
            # --- Old price: Lari ---
            old_price = card.find_element(
                By.CSS_SELECTOR, "div.product_card__old_price"
            ).text.strip()
        except:
            old_price = None

        # --- Product link ---
        try:
            link_element = card.find_element(By.CSS_SELECTOR, "a.link-secondary")
            product_link = link_element.get_attribute("href")
            decoded_link = unquote(product_link)
        except:
            decoded_link = None

        data.append({
            "Title": title,
            "New Price": new_price,
            "Old Price": old_price,
            "Product Link": decoded_link
        })

    return pd.DataFrame(data)



# Boom Discounts
def scrape_libre_boom(driver):
    url = 'https://libre.ge/productebi/boom-price'
    driver.get(url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p-md-4")))

    # -------- SCROLL TO LOAD ALL PRODUCTS --------
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # -------- FIND ALL PRODUCT CARDS --------
    product_cards = driver.find_elements(By.CSS_SELECTOR, "div.p-md-4 .col-xl-2")
    data = []

    for card in product_cards:
        try:
            title_element = card.find_element(
                By.CSS_SELECTOR,
                ".product_card__title .line_2"
            )

            title = title_element.text.strip()
        except:
            title = None

        try:
            # --- New price: Lari ---
            new_price_lari = card.find_element(
                By.CSS_SELECTOR, "div.product_card__new_price_lari"
            ).text.strip()

            # --- New price: Tetri ---
            new_price_tetri = card.find_element(
                By.CSS_SELECTOR, "div.product_card__new_price_tetri"
            ).text.strip()

            # Combine into a proper decimal price
            new_price = f"{new_price_lari}.{new_price_tetri}"
        except:
            new_price = None

        try:
            # --- Old price: Lari ---
            old_price = card.find_element(
                By.CSS_SELECTOR, "div.product_card__old_price"
            ).text.strip()
        except:
            old_price = None

        # --- Product link ---
        try:
            link_element = card.find_element(By.CSS_SELECTOR, "a.link-secondary")
            product_link = link_element.get_attribute("href")
            decoded_link = unquote(product_link)
        except:
            decoded_link = None

        data.append({
            "Title": title,
            "New Price": new_price,
            "Old Price": old_price,
            "Product Link": decoded_link
        })

    return pd.DataFrame(data)


driver = setup_driver()
df_discounts = scrape_libre(driver)
df_boom_discounts = scrape_libre_boom(driver)

df_all = pd.concat([df_discounts, df_boom_discounts], ignore_index=True)

print(df_all)

