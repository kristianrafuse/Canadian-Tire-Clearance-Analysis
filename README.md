**Canadian Tire Clearance ETL and WebApp**
-------


**ETL**
-------
* re
* os
* time
* math
* python
* pandas
* urlparse
* sqlalchemy
* BeautifulSoup
* splinter/Browser
* selenium webdriver

**app.py**
-------
* os
* Flask
* sqlalchemy

**app.js**
-------
* ajax
* html
* datatables
* tableau



**ETL Highlights**
-------

```
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.geolocation": 1
})
```

```
# I wanted to dynamically determine the number of loops to use. I judged that total results, or total number of products on sale, divided by the default number of products per page worked well. Using math.ceil to always round up. 

total_results_element = html_soup.find('span', class_='nl-filters__results')
total_results_text = total_results_element.text if total_results_element else '0'

# using re to extract the first sequence of digits found in the total_results_text and store it in the variable total_results as an integer.

total_results = int(re.search(r'\d+', total_results_text).group())
# default number of products per page

items_per_page = 24
total_pages = math.ceil(total_results / items_per_page)
```


```
original_price_element = product.find('s', attrs={'aria-hidden': 'true'})
original_price = original_price_element.text.strip() if original_price_element else 'N/A'

there were some products with prices in different places, so this fills in those spaces. 

if original_price == 'N/A':
alt_original_price_element = product.find('span', class_='nl-price--total')
original_price = alt_original_price_element.text.strip() if alt_original_price_element else 'N/A'

img_tag = product.find('img', attrs={'data-src': True})
product_image_link = img_tag['data-src'] if img_tag and 'data-src' in img_tag.attrs else 'N/A'

```

```
# I wasn't actually interested in the image links as image links, but rather to parse out product category information, which didn't seem to be present anywhere else on the page. I created a function that uses urllib.parse from urlparse to grab the information that I wanted. I was having trouble getting re to work here, and this was simpler.

def extract_category(link_url):
    parsed_url = urlparse(link_url)
    path_components = parsed_url.path.split('/')
    category = '/'.join(path_components[3:4])
    return category
```

```
# handle survey pop-up
    try:
        not_right_now_button = WebDriverWait(driver3, 10).until(
            EC.element_to_be_clickable((By.ID, "kplDeclineButton"))
        )
        not_right_now_button.click()
    except:
        pass
```

**app.py Highlights**
-------
```
# Loop through the table names

table_names = ["clearance", "sales"]

for table_name in table_names:

    try:
        # Execute a select query on each table
        query = f"SELECT * FROM {table_name}"
        result = engine.execute(query)
      
        # Fetch all rows and columns
        rows = result.fetchall()
        columns = result.keys()
        
        # use zip function to take columns and rows and pair their elements together then create a dictonary 

        table_data = [dict(zip(columns, row)) for row in rows]
        data[table_name] = {"csv_data": table_data}

        # error handling -- this saved me when I decided it would be a good idea to upgrade SQLalchemy...

    except Exception as e:
        print(e)
        return jsonify({"error": f"An error occurred while fetching data from the table {table_name}: {str(e)}"})

return jsonify(data)

```
