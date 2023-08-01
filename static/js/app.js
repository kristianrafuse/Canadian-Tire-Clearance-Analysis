const url = '/api';

$.ajax({
  url: url,
  method: 'GET',
  dataType: 'json',
  cache: false,
  success: function(data) {
    console.log(data);
  },
});

function processData(data) {
  const formattedData = [];
  data.forEach(column => {
    const product_name = column['product_name'];
    const original_price = column['original_price'];
    const clearance_price = column['clearance_price'];
    const percentage_off = column['percentage_off'];
    const product_category = column['product_category'];
    const rating = column['rating'];
    const link = column['link'];

    const rowData = [
      product_name,
      original_price,
      clearance_price,
      percentage_off,
      product_category,
      rating,
      link,
    ];

    formattedData.push(rowData);
  });
  return formattedData;
}

$(document).ready(function () {
  $.ajax({
    url: url,
    method: 'GET',
    dataType: 'json',
    success: function (response) {
      const clearance_data = response.clearance.csv_data;
      const formattedData = processData(clearance_data);

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
          render: function (data, type) {
            return type === 'display' ? '<a href="' + data + '">' + data + '</a>' : data;
          }
        },
      ];

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
        data: [], // Empty data initially; it will be updated later based on the threshold
        order: [[3, 'asc']],
        columns: columns,
        dom: 'Blfrtip',
        buttons: ['copy', 'csv'],
      });

      // Get the threshold element and its value
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

        // Combine the filtered clearance data and sale data
        const dataAboveThreshold = dataAboveThresholdClearance.concat(dataAboveThresholdSale);

        // Update the table with clearance prices above the threshold
        tableAboveThreshold.clear().rows.add(processData(dataAboveThreshold)).draw();
      });
    },
  });
});