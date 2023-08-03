// Define the base URL for the API
const url = '/api';

// First AJAX request to get data from the API to verify that it's loading properly/accessible
$.ajax({
  url: url,
  method: 'GET',
  dataType: 'json',
  cache: false,
  success: function(data) {
    console.log(data);
  },
});

// Function to process the data received from the API
function processData(data) {
  // Initialize an array to store the formatted data
  const formattedData = [];
  // Iterate through each column in the data
  data.forEach(column => {
    // Extract the values for each column and store them in variables
    const product_name = column['product_name'];
    const original_price = column['original_price'];
    const clearance_price = column['clearance_price'];
    const percentage_off = column['percentage_off'];
    const product_category = column['product_category'];
    const rating = column['rating'];
    const link = column['link'];

    // Create a row of data with the extracted values
    const rowData = [
      product_name,
      original_price,
      clearance_price,
      percentage_off,
      product_category,
      rating,
      link,
    ];

    // Add the row of data to the formattedData array
    formattedData.push(rowData);
  });
  return formattedData;
}

// Document ready function
$(document).ready(function () {
  // Second AJAX request to get data from the API
  $.ajax({
    url: url,
    method: 'GET',
    dataType: 'json',
    success: function (response) {
      // Get the clearance data from the API response
      const clearance_data = response.clearance.csv_data;
      // Process the clearance data using the processData function
      const formattedData = processData(clearance_data);

      // Define columns for the DataTable representing clearance data
      const columns = [
        { title: 'Product Name', className: "text-left" },
        { title: 'Original Price', className: "text-right" },
        { title: 'Clearance Price', className: "text-right" },
        { title: 'Percentage Off', className: "text-right" },
        { title: 'Product Category', className: "text-left" },
        { title: 'Rating', className: "text-right" },
        {
          title: 'Link',
          className: "text-left",
          // Custom render function for the link column to get the hyperlinks working
          render: function (data, type) {
            return type === 'display' ? '<a href="' + data + '">' + data + '</a>' : data;
          }
        },
      ];

      // Initialize the DataTable for clearance data
      $('#myTable').DataTable({
        data: formattedData,
        order: [[3, 'desc']],
        columns: columns,
        dom: 'Blfrtip',
        buttons: ['copy', 'csv']
      });

      const sale_data = response.sales.csv_data;
      const formattedData2 = processData(sale_data);

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

      $('#myTable2').DataTable({
        data: formattedData2,
        order: [[3, 'desc']],
        columns: columns2,
        dom: 'Blfrtip',
        buttons: ['copy', 'csv',]
      });

      // Initialize the clearance prices above the threshold table
      const tableAboveThreshold = $('#myTableAboveThreshold').DataTable({
        // Empty data initially; it will be updated later based on the threshold
        data: [], 
        order: [[3, 'asc']],
        columns: columns,
        dom: 'Blfrtip',
        buttons: ['copy', 'csv'],
      });

      // Get the threshold html element and its value
      const thresholdSlider = document.getElementById('thresholdSlider');
      const thresholdValue = document.getElementById('thresholdValue');

      // Update the threshold value display when the slider value changes
      thresholdSlider.addEventListener('input', function () {
        thresholdValue.textContent = thresholdSlider.value;

        // Calculate the percentage threshold from the slider value
        const thresholdPercentage = parseFloat(thresholdSlider.value);

        // Filter the clearance_data based on the threshold
        const dataAboveThresholdClearance = clearance_data.filter(
          (item) => parseFloat(item.percentage_off) >= thresholdPercentage
        );

        // Filter the sale_data based on the threshold
        const sale_data = response.sales.csv_data;
        const dataAboveThresholdSale = sale_data.filter(
          (item) => parseFloat(item.percentage_off) >= thresholdPercentage
        );

        // Combine the filtered clearance data and sale data -- I want to display both datasets
        const dataAboveThreshold = dataAboveThresholdClearance.concat(dataAboveThresholdSale);

        // Update the table with clearance and sale prices above the threshold!
        tableAboveThreshold.clear().rows.add(processData(dataAboveThreshold)).draw();
      });
    },
  });
});