const url = '/api';

$.ajax({
  url: url,
  method: 'GET',
  dataType: 'json',
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
    },
    error: function (err) {
      console.error('Error fetching data:', err);
    },   
  });
  $("#emailAlertForm").on("submit", function (event) {
    event.preventDefault();
    const email = $("#email").val();
    const threshold = $("#threshold").val();
    
    $.ajax({
      url: "/subscribe",
      method: "POST",
      data: {
        email: email,
        threshold: threshold,
      },
      dataType: "json",
      success: function (response) {
        alert(response.message);
      },
      error: function (error) {
        alert("An error occurred while subscribing.");
      },
    });
  });
});