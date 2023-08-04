**Canadian Tire Clearance ETL and WebApp**
-------

**ETL**
-------
* re
* os
* time
* math
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

I wanted to dynamically determine the number of loops to use. I judged that total results, or total number of products on sale, divided by the default number of products per page worked well. Using math.ceil to always round up. 
```
    total_results_element = html_soup.find('span', class_='nl-filters__results')
    total_results_text = total_results_element.text if total_results_element else '0'

Use re to extract the first sequence of digits found in the total_results_text and store it in the variable total_results as an integer.

    total_results = int(re.search(r'\d+', total_results_text).group())

Default number of products per page

    items_per_page = 24
    total_pages = math.ceil(total_results / items_per_page)
```

Basic structure of locating the object then scraping out the details 
```  
    original_price_element = product.find('s', attrs={'aria-hidden': 'true'})
    original_price = original_price_element.text.strip() if original_price_element else 'N/A'

There were some products with prices in different places, so this fills in those spaces. 

    if original_price == 'N/A':
    alt_original_price_element = product.find('span', class_='nl-price--total')
    original_price = alt_original_price_element.text.strip() if alt_original_price_element else 'N/A'

I notice that the urls of the images links contained product category information.
    img_tag = product.find('img', attrs={'data-src': True})
    product_image_link = img_tag['data-src'] if img_tag and 'data-src' in img_tag.attrs else 'N/A'

```

I wasn't actually interested in the image links as image links, but rather to parse out product category information, which didn't seem to be present anywhere else on the page. I created a function that uses urllib.parse from urlparse to grab the information that I wanted. I was having trouble getting re to work here, and this was simpler.
```
    def extract_category(link_url):
        parsed_url = urlparse(link_url)
        path_components = parsed_url.path.split('/')
        category = '/'.join(path_components[3:4])
        return category
```

handle survey pop-up
```
    try:
        not_right_now_button = WebDriverWait(driver3, 10).until(
            EC.element_to_be_clickable((By.ID, "kplDeclineButton"))
        )
        not_right_now_button.click()
    except:
        pass
```

Error handling example that should have been taken care of earlier, I think.
```
    sales_data_to_insert = []
    for row in csv_reader:
        original_price = float(row[1]) if row[1] != '' else None
        clearance_price = float(row[2]) if row[2] != '' else None
        percentage_off = float(row[3]) if row[3] != '' else None
        rating = float(row[6]) if row[6] != '' else None

        sales_data_to_insert.append({
            "product_name": row[0],
            "original_price": original_price,
            "clearance_price": clearance_price,
            "percentage_off": percentage_off,
            "product_category": row[4],
            "product_code": row[5],
            "rating": rating,
            "link": row[7]
        })

Insert the data into the "sales" table
    sales_insert_query = sales_table.insert()
    engine.execute(sales_insert_query, sales_data_to_insert)
    engine.dispose()
```

**app.py Highlights**
-------

Initial data serving by accessing my sqlserver, and loop through the table names
```
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

**app.js Highlights**
-------

Basic setup:
```
    $.ajax({
    url: url,
    method: 'GET',
    dataType: 'json',
    cache: false,
    success: function(data) {
        console.log(data);
    },
    });
```

HTML for initializing Datatables:
```
    <div class="row">
      <div class="col-md-12 text-center">
        <h2>Clearance Products</h2>
        <table id="myTable" class="display" style="width: 100%; padding: 50px;"></table>
      </div>
    </div>

```

Initialize the DataTable for clearance data
```
    $('#myTable').DataTable({
    data: formattedData,
    order: [[3, 'desc']],
    columns: columns,
    dom: 'Blfrtip',
    buttons: ['copy', 'csv']
      });
```

In Datatables, there lots of options for defining and modifying columns I was happy to figure out how to get the hyperlinks working.
```
      const columns2 = [
        { title: 'Product Name', className: "text-left" },
        { title: 'Original Price', className: "text-right" },
        { title: 'Sale Price', className: "text-right" },
        { title: 'Percentage Off', className: "text-right" },
        { title: 'Product Category', className: "text-left" },
        { title: 'Rating', className: "text-right" },
        {
          title: 'Link',
          className: "text-left",
          render: function (data, type) {
            return type === 'display' ? '<a href="' + data + '">' + data + '</a>' : data;
          }
        },
      ];
```

Basic html structire for a slider bar 
```

        <label for="thresholdSlider">Find products by Percentage Off.</label>
        <input type="range" id="thresholdSlider" min="0" max="100" step="1" value="0">
        <span id="thresholdValue">0</span>

```

Get the threshold html element and its value and use it to populate a table
```
      const thresholdSlider = document.getElementById('thresholdSlider');
      const thresholdValue = document.getElementById('thresholdValue');

Update the threshold value display when the slider value changes
      thresholdSlider.addEventListener('input', function () {
        thresholdValue.textContent = thresholdSlider.value;

Calculate the percentage threshold from the slider value
        const thresholdPercentage = parseFloat(thresholdSlider.value);

Filter the clearance_data based on the threshold
        const dataAboveThresholdClearance = clearance_data.filter(
          (item) => parseFloat(item.percentage_off) >= thresholdPercentage
        );

Filter the sale_data based on the threshold
        const sale_data = response.sales.csv_data;
        const dataAboveThresholdSale = sale_data.filter(
          (item) => parseFloat(item.percentage_off) >= thresholdPercentage
        );

Combine the filtered clearance data and sale data -- I want to display both datasets in this table.
        const dataAboveThreshold = dataAboveThresholdClearance.concat(dataAboveThresholdSale);

Update the table with clearance and sale prices above the threshold! use 'clear()' to clear the previous selection, and 'draw()' to add the new data.

        tableAboveThreshold.clear().rows.add(processData(dataAboveThreshold)).draw();

```