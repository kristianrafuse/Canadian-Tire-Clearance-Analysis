**Canadian Tire Clearance ETL and WebApp**
-------
This example shows an interactive WebApp to visualize the price data that I've scraped from CanadianTire. I use Tableau to visualize pricing trends, and DataTables for an interactive way to explore the data. I created an HTML slider bar to allow users to find deals based on a clearance percentage threshold. 

**Deployment**
-------
https://teal-sasha-50.tiiny.site/ 

(Thanks for Greg Hatt for help with deploying the application!)

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

Basic html structure for a slider bar 
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
