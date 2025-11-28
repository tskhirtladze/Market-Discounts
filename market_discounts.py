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

def scrape_2nabiji(driver):
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

    return pd.DataFrame(data)

def scrape_nikora(driver):
    base_url = "https://nikorasupermarket.ge/ge/%E1%83%9B%E1%83%98%E1%83%9B%E1%83%93%E1%83%98%E1%83%9C%E1%83%90%E1%83%A0%E1%83%94-%E1%83%90%E1%83%A5%E1%83%AA%E1%83%98%E1%83%94%E1%83%91%E1%83%98/2-%E1%83%99%E1%83%95%E1%83%98%E1%83%A0%E1%83%98%E1%83%90%E1%83%9C%E1%83%98"

    all_data = []
    page = 1

    while True:
        url = f"{base_url}?page={page}"
        driver.get(url)
        wait = WebDriverWait(driver, 15)

        # Dismiss cookies on first page only
        if page == 1:
            try:
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "cookie_reject_btn"))).click()
            except:
                pass

        # Wait for container
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.lg_9")))

        # Container and product cards
        product_cards_div = driver.find_element(By.CSS_SELECTOR, "div.lg_9")
        product_cards = product_cards_div.find_elements(By.CSS_SELECTOR, "div.lg_4")

        print(f"Page {page} – Found {len(product_cards)} products")

        for card in product_cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, "h4.cp6").text
            except:
                title = None

            try:
                discount_days = card.find_element(
                    By.CSS_SELECTOR, "div.cp16.col_padding"
                ).text.strip().replace("\n", " ")
            except:
                discount_days = None

            try:
                major = card.find_element(By.CSS_SELECTOR, "div.new span.cp103.cp104").text.strip()
                minor = card.find_element(By.CSS_SELECTOR, "div.new sup.tetri small").text.strip()
                currency = card.find_element(By.CSS_SELECTOR, "div.new span.cp108").text.strip()
                new_price = f"{major}.{minor} {currency}"
            except:
                new_price = None

            try:
                old_major = card.find_element(By.CSS_SELECTOR, "div.old span.cp103.cp105").text.strip()
                old_minor = card.find_element(By.CSS_SELECTOR, "div.old sup.tetri small").text.strip()
                old_currency = card.find_element(By.CSS_SELECTOR, "div.old div.cp102.cp105 span").text.strip()
                old_price = f"{old_major}.{old_minor} {old_currency}"
            except:
                old_price = None

            try:
                product_link = card.find_element(By.CSS_SELECTOR, "a.team.cp7").get_attribute("href")
                decoded_link = unquote(product_link)
            except:
                decoded_link = None

            all_data.append({
                "Title": title,
                "Days Left": discount_days,
                "New Price": new_price,
                "Old Price": old_price,
                "Product Link": decoded_link
            })

        # Check if there is a next page
        try:
            next_page = driver.find_element(By.CSS_SELECTOR, "a.ba_arrow_right#pg0")
            page += 1
            time.sleep(1)
        except:
            print("No more pages.")
            break

    df = pd.DataFrame(all_data)

    return df

if __name__ == "__main__":
    driver = setup_driver()
    try:
        df_2nabiji = scrape_2nabiji(driver)
        time.sleep(2)
        driver = setup_driver()

        df_nikora = scrape_nikora(driver)

        # Save both dataframes in one Excel file with different sheets
        with pd.ExcelWriter("market_discounts.xlsx", engine="openpyxl") as writer:
            df_2nabiji.to_excel(writer, sheet_name="2nabiji", index=False)
            df_nikora.to_excel(writer, sheet_name="nikora", index=False)

        print("Scraping finished. Data saved to market_discounts.xlsx")

    finally:
        driver.quit()

