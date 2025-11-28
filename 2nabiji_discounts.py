from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

executable_path = "./driver/chromedriver"
base_url = "https://2nabiji.ge"

def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # optional
    cService = ChromeService(executable_path=executable_path)
    return webdriver.Chrome(service=cService, options=options)

driver = setup_driver()

try:
    url = 'https://2nabiji.ge/ge/search?searchId=64c19575b3118b3676d26898'
    driver.get(url)
    driver.maximize_window()

    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Search_search__result__5biZE")))

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
    product_cards = driver.find_elements(By.CSS_SELECTOR, "div.ProductCard_container__7IE0M")

    data = []

    for card in product_cards:
        try:
            # Title and Link
            title_elem = card.find_element(By.CSS_SELECTOR, "a.ProductCard_title__Rpp75 > span")
            title = title_elem.get_attribute("title")
        except:
            title = None

        try:
            discount = card.find_element(By.CLASS_NAME, "Label_label__EnQXP").text
        except:
            discount = None

        try:
            new_price = card.find_element(By.CLASS_NAME, "ProductCard_productInfo__price__NyCJR").find_element(
                By.TAG_NAME, "span").text
        except:
            new_price = None

        try:
            old_price = card.find_element(By.CLASS_NAME, "ProductCard_productInfo__price_discount__CXdp2").find_element(
                By.TAG_NAME, "span").text
        except:
            old_price = None

        # IMAGE LINK
        try:
            img_elem = card.find_element(By.CSS_SELECTOR, "figure.ProductCard_image__zCC4j > img")
            img_link = img_elem.get_attribute("src")
            product_link = img_link.replace("/cdn.", "")
            product_link = product_link.replace("2nabiji.ge", "2nabiji.ge/ge")
            product_link = product_link.replace("products", "product")
            product_link = product_link.replace("-300x300.webp", "#")

        except:
            img_link = None
            product_link = None

        data.append({
            "Title": title,
            "Discount": discount,
            "New Price": new_price,
            "Old Price": old_price,
            "Image Link": img_link,
            "Product Link": product_link
        })

    # -------- CREATE DATAFRAME --------
    df = pd.DataFrame(data)
    print(df)
    df.to_csv('2nabiji_discounts.csv')

finally:
    driver.quit()
