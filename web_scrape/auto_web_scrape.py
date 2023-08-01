#imports
import time
import math 
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from splinter import Browser
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import re
import os

#establishing the base url from the clearance section

base_url = "https://www.canadiantire.ca/en/promotions/clearance.html?page="

#setting up some options for the chrome browser. Using the exp_option to click the allow location, and incognito mode to
#seperate the browers from my other open browsers. Also, repeat testing without cookies saved was helpful. 

chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.geolocation": 1
})

#setup the Chromedriver. it was not working without the time delay, perhaps letting the page load fully.
service = Service("C:\Program Files\Common Files\ChromeDriver\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get(base_url)
time.sleep(5)
html_content = driver.page_source
html_soup = soup(html_content, 'html.parser')

# I wanted to dynamically determine the number of loops to use. I judged that total results, or total number of 
# products on sale, divided by the default number of products per page worked well. Using math.ceil to always round up. 

total_results_element = html_soup.find('span', class_='nl-filters__results')
total_results_text = total_results_element.text if total_results_element else '0'
total_results = int(re.search(r'\d+', total_results_text).group())
items_per_page = 24
total_pages = math.ceil(total_results / items_per_page)

# creating a empty list to store data
product_data = []

#beginning the loop, adding time for the page to load, using a try except to handle a random survey pop-up. 

for page_number in range(1, total_pages + 1):
    url = base_url + str(page_number)
    driver.get(url)
    time.sleep(5)

    try:
        not_right_now_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "kplDeclineButton"))
        )
        not_right_now_button.click()
    except:
        pass

#gathering the ingredients for my soup. 

    html_content = driver.page_source
    html_soup = soup(html_content, 'html.parser')

    product_info = html_soup.find_all(class_='nl-product__content')

#another loop to grab all the info on the page. The first code chunk locates, the second chunk parses out. 
    for product in product_info:
        product_name_element = product.find('div', class_='nl-product-card__title')
        original_price_element = product.find('s', attrs={'aria-hidden': 'true'})
        clearance_price_element = product.find('span', class_='nl-price--total--red')
        rating_element = product.find('div', class_='bv_text')
        image_element = product.find('div', class_='nl-product-card__image-wrap')
        anchor_tag = product.find('a', class_='nl-product-card__no-button', href=True)
        img_tag = product.find('img', attrs={'data-src': True})

        product_name = product_name_element.text.strip() if product_name_element else 'N/A'
        original_price = original_price_element.text.strip() if original_price_element else 'N/A'
        clearance_price = clearance_price_element.text.strip() if clearance_price_element else 'N/A'
        rating = rating_element.text.strip() if rating_element else None
        product_code_element = product.find('p', class_='nl-product__code', attrs={'aria-hidden': 'true'})
        product_code = product_code_element.get_text(strip=True).lstrip('#') if product_code_element else 'N/A'
        product_link = "https://www.canadiantire.ca" + anchor_tag['href'] if anchor_tag is not None else 'N/A'
        product_image_link = img_tag['data-src'] if img_tag and 'data-src' in img_tag.attrs else 'N/A'

#there were some products with prices in different places, so this fills in those spaces. 
        if original_price == 'N/A':
            alt_original_price_element = product.find('span', class_='nl-price--total')
            original_price = alt_original_price_element.text.strip() if alt_original_price_element else 'N/A'

#adding some data cleaning and parsing to the loop to make it easier later on. 
        clearance_price = float(clearance_price.replace('Each', '').replace('$', '').replace(',', '')) if clearance_price != 'N/A' else None
        original_price = float(original_price.replace('Each', '').replace('$', '').replace(',', '')) if original_price != 'N/A' else None

        product_data.append({
            'Product Name': product_name,
            'Original Price': original_price,
            'Clearance Price': clearance_price,
            'Rating': rating,
            'Product Code': product_code,
            'Link': product_link, 
            'Image Link': product_image_link
        })

driver.quit()

#printing these as a way to check that the scraping was working
print(f"Total number of results: {total_results}")
print(f"Total number of pages: {total_pages}")

# I wasn't actually interested in the image links as image links, but rather to parse out product category information, 
# which didn't seem to be present anywhere else on the page. I created a function that uses urllib.parse from urlparse
# to grab the information that I wanted. I was having trouble getting re to work here, and this was simpler.

def extract_category(link_url):
    parsed_url = urlparse(link_url)
    path_components = parsed_url.path.split('/')
    category = '/'.join(path_components[3:4])
    return category

#creating the dataframe, creating a new column that calculates the clearance prices, applying my extract_category
clearance_df = pd.DataFrame(product_data)
clearance_df['Percentage Off'] = round(((clearance_df['Original Price'] - clearance_df['Clearance Price']) / clearance_df['Original Price']) * 100)
clearance_df['Product Category'] = clearance_df['Image Link'].apply(extract_category)

# HOT-SALE scraping. Code is nearly idential to the above.
# scraping the sale section for additional data

base_url = "https://www.canadiantire.ca/en/promotions/hot-sale.html?page="

chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.geolocation": 1
})

service = Service("C:\Program Files\Common Files\ChromeDriver\chromedriver.exe")
driver2 = webdriver.Chrome(service=service)

driver2.get(base_url)
time.sleep(5)
html_content = driver2.page_source
html_soup = soup(html_content, 'html.parser')

total_results_element = html_soup.find('span', class_='nl-filters__results')
total_results_text = total_results_element.text if total_results_element else '0'

total_results = int(re.search(r'\d+', total_results_text).group())

items_per_page = 24
total_pages = math.ceil(total_results / items_per_page)

sale_product_data = []

for page_number in range(1, total_pages + 1):
    url = base_url + str(page_number)
    driver2.get(url)
    time.sleep(5)

    try:
        not_right_now_button = WebDriverWait(driver2, 10).until(
            EC.element_to_be_clickable((By.ID, "kplDeclineButton"))
        )
        not_right_now_button.click()
    except:
        pass

    html_content = driver2.page_source
    html_soup = soup(html_content, 'html.parser')

    sale_product_info = html_soup.find_all(class_='nl-product__content')

    for product in sale_product_info:
        product_name_element = product.find('div', class_='nl-product-card__title')
        original_price_element = product.find('s', attrs={'aria-hidden': 'true'})
        clearance_price_element = product.find('span', class_='nl-price--total--red')
        rating_element = product.find('div', class_='bv_text')
        image_element = product.find('div', class_='nl-product-card__image-wrap')
        anchor_tag = product.find('a', class_='nl-product-card__no-button', href=True)
        img_tag = product.find('img', attrs={'data-src': True})

        product_name = product_name_element.text.strip() if product_name_element else 'N/A'
        original_price = original_price_element.text.strip() if original_price_element else 'N/A'
        clearance_price = clearance_price_element.text.strip() if clearance_price_element else 'N/A'
        rating = rating_element.text.strip() if rating_element else None
        product_code_element = product.find('p', class_='nl-product__code', attrs={'aria-hidden': 'true'})
        product_code = product_code_element.get_text(strip=True).lstrip('#') if product_code_element else 'N/A'
        product_link = "https://www.canadiantire.ca" + anchor_tag['href'] if anchor_tag is not None else 'N/A'
        product_image_link = img_tag['data-src'] if img_tag and 'data-src' in img_tag.attrs else 'N/A'

        if original_price == 'N/A':
            alt_original_price_element = product.find('span', class_='nl-price--total')
            original_price = alt_original_price_element.text.strip() if alt_original_price_element else 'N/A'

        clearance_price = float(clearance_price.replace('Each', '').replace('$', '').replace(',', '')) if clearance_price != 'N/A' else None
        original_price = float(original_price.replace('Each', '').replace('$', '').replace(',', '')) if original_price != 'N/A' else None

        sale_product_data.append({
            'Product Name': product_name,
            'Original Price': original_price,
            'Sale Price': clearance_price,
            'Rating': rating,
            'Product Code': product_code,
            'Link': product_link, 
            'Image Link': product_image_link
        })

driver2.quit()

print(f"Total number of results: {total_results}")
print(f"Total number of pages: {total_pages}")

sale_df = pd.DataFrame(sale_product_data)
sale_df['Percentage Off'] = round(((sale_df['Original Price'] - sale_df['Sale Price']) / sale_df['Original Price']) * 100)
sale_df['Product Category'] = sale_df['Image Link'].apply(extract_category)

#RED-ALERT-DEALS scraping. Code is nearly idential to the above.
# scraping the sale section for additional data

base_url = "https://www.canadiantire.ca/en/promotions/red-alert-deals.html?page="

chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.geolocation": 1
})

service = Service("C:\Program Files\Common Files\ChromeDriver\chromedriver.exe")
driver3 = webdriver.Chrome(service=service)

driver3.get(base_url)
time.sleep(5)
html_content = driver3.page_source
html_soup = soup(html_content, 'html.parser')

total_results_element = html_soup.find('span', class_='nl-filters__results')
total_results_text = total_results_element.text if total_results_element else '0'

total_results = int(re.search(r'\d+', total_results_text).group())

items_per_page = 24
total_pages = math.ceil(total_results / items_per_page)

sale_product_data_2 = []

for page_number in range(1, total_pages + 1):
    url = base_url + str(page_number)
    driver3.get(url)
    time.sleep(5)

    try:
        not_right_now_button = WebDriverWait(driver3, 10).until(
            EC.element_to_be_clickable((By.ID, "kplDeclineButton"))
        )
        not_right_now_button.click()
    except:
        pass

    html_content = driver3.page_source
    html_soup = soup(html_content, 'html.parser')

    sale_product_info2 = html_soup.find_all(class_='nl-product__content')

    for product in sale_product_info2:
        product_name_element = product.find('div', class_='nl-product-card__title')
        original_price_element = product.find('s', attrs={'aria-hidden': 'true'})
        clearance_price_element = product.find('span', class_='nl-price--total--red')
        rating_element = product.find('div', class_='bv_text')
        image_element = product.find('div', class_='nl-product-card__image-wrap')
        anchor_tag = product.find('a', class_='nl-product-card__no-button', href=True)
        img_tag = product.find('img', attrs={'data-src': True})

        product_name = product_name_element.text.strip() if product_name_element else 'N/A'
        original_price = original_price_element.text.strip() if original_price_element else 'N/A'
        clearance_price = clearance_price_element.text.strip() if clearance_price_element else 'N/A'
        rating = rating_element.text.strip() if rating_element else None
        product_code_element = product.find('p', class_='nl-product__code', attrs={'aria-hidden': 'true'})
        product_code = product_code_element.get_text(strip=True).lstrip('#') if product_code_element else 'N/A'
        product_link = "https://www.canadiantire.ca" + anchor_tag['href'] if anchor_tag is not None else 'N/A'
        product_image_link = img_tag['data-src'] if img_tag and 'data-src' in img_tag.attrs else 'N/A'

        if original_price == 'N/A':
            alt_original_price_element = product.find('span', class_='nl-price--total')
            original_price = alt_original_price_element.text.strip() if alt_original_price_element else 'N/A'

        clearance_price = float(clearance_price.replace('Each', '').replace('$', '').replace(',', '')) if clearance_price != 'N/A' else None
        original_price = float(original_price.replace('Each', '').replace('$', '').replace(',', '')) if original_price != 'N/A' else None

        sale_product_data_2.append({
            'Product Name': product_name,
            'Original Price': original_price,
            'Sale Price': clearance_price,
            'Rating': rating,
            'Product Code': product_code,
            'Link': product_link, 
            'Image Link': product_image_link
        })

driver3.quit()

print(f"Total number of results: {total_results}")
print(f"Total number of pages: {total_pages}")

sale_df2 = pd.DataFrame(sale_product_data_2)
sale_df2['Percentage Off'] = round(((sale_df2['Original Price'] - sale_df2['Sale Price']) / sale_df2['Original Price']) * 100)
sale_df2['Product Category'] = sale_df2['Image Link'].apply(extract_category)

#no longer needed, I just used them to parse out the product type
clearance_df.drop('Image Link', axis=1, inplace=True)
sale_df.drop('Image Link', axis=1, inplace=True)
sale_df2.drop('Image Link', axis=1, inplace=True)

#reordering columns so they make more sense to me. 
clearance_column_order = ['Product Name',
                    'Original Price',
                    'Clearance Price',
                    'Percentage Off',
                    'Product Category',
                    'Product Code',
                    'Rating',
                    'Link']

sale_column_order = ['Product Name',
                    'Original Price',
                    'Sale Price',
                    'Percentage Off',
                    'Product Category',
                    'Product Code',
                    'Rating',
                    'Link']

clearance_df = clearance_df.loc[:, clearance_column_order]
sale_df = sale_df.loc[:, sale_column_order]
sale_df2 = sale_df2.loc[:, sale_column_order]

#change astype in case I want to use this later
clearance_df['Rating'] = clearance_df['Rating'].astype(float)
sale_df['Rating'] = sale_df['Rating'].astype(float)
sale_df2['Rating'] = sale_df2['Rating'].astype(float)

#Removing characters that were causing sql import issues. 

clearance_df["Product Name"] = clearance_df["Product Name"].str.replace("'", '')
clearance_df["Product Name"] = clearance_df["Product Name"].str.replace("Â®", '')
sale_df["Product Name"] = sale_df["Product Name"].str.replace("'", '')
sale_df["Product Name"] = sale_df["Product Name"].str.replace("Â®", '')
sale_df2["Product Name"] = sale_df2["Product Name"].str.replace("'", '')
sale_df2["Product Name"] = sale_df2["Product Name"].str.replace("Â®", '')

clearance_df.to_csv("./clearance.csv", index=False)
sale_df.to_csv("./sale.csv", index=False)
sale_df2.to_csv("./sale2.csv", index=False)

#just in case I only want to work with all the sale products, not seperated by specific promotion
allsales_df = pd.concat([sale_df, sale_df2], ignore_index=True)
allsales_df.to_csv("./allsales.csv", index=False)

allproducts_df = pd.concat([clearance_df, sale_df, sale_df2], ignore_index=True)
allproducts_df.to_csv("./allproducts_df.csv", index=False)

# for historical record keeping
from datetime import datetime
current_date = datetime.now().strftime("%Y-%m-%d")

clearance_df.to_csv(f"./clearance_{current_date}.csv", index=False)
sale_df.to_csv(f"./sale_{current_date}.csv", index=False)
sale_df2.to_csv(f"./sale2_{current_date}.csv", index=False)
allsales_df.to_csv(f"./allsales_{current_date}.csv", index=False)
allproducts_df.to_csv(f"./allproducts_{current_date}.csv", index=False)

# Connection details for uploading to server
username = os.environ.get('DB_USERNAME')
password = os.environ.get('DB_PASSWORD')
host = os.environ.get('DB_HOST')
database = os.environ.get('DB_NAME')

# Create the database connection URL
url = f'postgresql://{username}:{password}@{host}/{database}'

engine = create_engine(url)  
clearance_table = 'clearance2'
allsales_table = 'sales2'

# Write the DataFrames to the database tables
clearance_df.to_sql(clearance_table, engine, if_exists='replace', index=False)
allsales_df.to_sql(allsales_table, engine, if_exists='replace', index=False)