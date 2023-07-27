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




//     // Extract the data for the bar chart
//     const regionalData = response.regional.csv_data;

//     // Extract the categories from the regional data
//     const regionalCategories = Object.keys(regionalData[0]);

//     // Remove the "Region" category from the list
//     regionalCategories.splice(regionalCategories.indexOf('Region'), 1);

//     // Create the data array for the bar chart
//     const barData = [{
//       x: regionalCategories,
//       y: regionalCategories.map(category => parseInt(regionalData[0][category])),
//       type: 'bar'
//     }];

//     // Create the layout for the bar chart
//     const barLayout = {
//       title: 'Regional Data, Canada, 2020',
//       xaxis: { title: 'Category',
//               automargin: true,
//     },
//       yaxis: { title: 'Species Count' },
//       width: 1100,
//       height: 1000
//     };

//     // Create the bar chart
//     Plotly.newPlot('bar1', barData, barLayout);

//     // Populate the dropdown with province options
//     const provinceDropdown = document.getElementById('selDataset');
//     const provinces = regionalData.map(entry => entry.Region);
//     provinces.forEach(province => {
//       const option = document.createElement('option');
//       option.text = province;
//       provinceDropdown.add(option);
//     });

//     // Add event listener to the dropdown
//     provinceDropdown.addEventListener('change', function() {
//       const selectedProvince = this.value;
//       updateBarChart(selectedProvince);
//     });

//     // Function to update the bar chart based on the selected province
//     function updateBarChart(selectedProvince) {
//       // Find the data for the selected province
//       const selectedData = regionalData.find(entry => entry.Region === selectedProvince);

//       // Extract the categories from the selected data
//       const regionalCategories = Object.keys(selectedData);

//       // Remove the "Region" category from the list
//       regionalCategories.splice(regionalCategories.indexOf('Region'), 1);

//       // Create the data array for the bar chart
//       const barData = [{
//         x: regionalCategories,
//         y: regionalCategories.map(category => parseInt(selectedData[category])),
//         type: 'bar'
//       }];

//       // Create the layout for the bar chart
//       const barLayout = {
//         title: `Regional Data for ${selectedProvince}`,
//         xaxis: { title: 'Category',
//                  automargin: true,
//       },
//         yaxis: { title: 'Species Count' },
//         width: 1100,
//         height: 1000
//       };

//       // Update the bar chart
//       Plotly.newPlot('bar1', barData, barLayout);
//     }

//   // (Line graphs, pie chart, etc.)
// const data = response.birds.csv_data;

// // Extract the years from the data
// const years = data.map(entry => parseInt(entry.Year));

// // Extract the percentage change values for each bird category
// const categories = [
//   'Aerial_insectivores',
//   'All_other_birds',
//   'Birds_of_prey',
//   'Forest_birds',
//   'Grassland_birds',
//   'Seabirds',
//   'Shorebirds',
//   'Waterfowl',
//   'Wetland_birds'
// ];

// const categoryData = {};

// categories.forEach(category => {
//   categoryData[category] = data.map(entry => parseFloat(entry[`${category}_percentage_change`]));
// });

// // Create the trace objects for the line graph
// const traces = categories.map(category => ({
//   x: years,
//   y: categoryData[category],
//   name: category,
//   type: 'scatter',
//   line: {
//     width: 5
//   }
// }));

// // Create the layout for the line graph
// const layout = {
//   title: 'Bird Population Changes Since 1970',
//   xaxis: { title: 'Year' },
//   yaxis: { title: 'Percentage Change' },
//   width: 1100,
//   height: 900
// };

// // Create the line graph
// Plotly.newPlot('line2', traces, layout);

//     // Load the data for the second line graph from species_percent.csv_data
//     const secondLineData = response.species_percent.csv_data;

//     // Extract the years from the data
//     const secondLineYears = secondLineData.map(entry => parseInt(entry.Year));

//     // Extract the percentage change values for each source of data
//     const sources = Object.keys(secondLineData[0]).filter(key => key !== 'Year');

//     const sourceData = {};

//     sources.forEach(source => {
//       sourceData[source] = secondLineData.map(entry => parseFloat(entry[source]));
//     });

//     // Create the traces for the second line graph
//     const sourceTraces = sources.map(source => ({
//       x: secondLineYears,
//       y: sourceData[source],
//       name: source,
//       type: 'scatter',
//       line: {   
//         width: 5,
//       }
//     }));

//     // Create the layout for the second line graph
//     const secondLineLayout = {
//       title: 'Species Percentage Change Since 1970',
//       xaxis: { title: 'Year' },
//       yaxis: { title: 'Percentage Change' },
//       width: 1100,
//       height: 900
//     };

//     // Create the second line graph
//     Plotly.newPlot('line1', sourceTraces, secondLineLayout);

//     // Extract the "Number of species" and "Status" data from the "national" CSV file
//     const nationalData = response.national.csv_data;

//     // Extract the values from the national data
//     const values = nationalData.map(entry => parseFloat(entry['Number_of_species']));
//     const labels = nationalData.map(entry => entry['Status']);

//     // Create the data array for the pie chart
//     const pieData = [{
//       labels: labels,
//       values: values,
//       type: 'pie'
//     }];

//     // Create the layout for the pie chart
//     const pieLayout = {
//       title: 'Biodiversity Overview, Canada 2020',
//       width: 1100,
//       height: 1000
//     };

//     // Create the pie chart
//     Plotly.newPlot('pie1', pieData, pieLayout);
//   });