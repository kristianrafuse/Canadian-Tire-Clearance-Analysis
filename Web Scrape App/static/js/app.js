const url = '/api';

$.ajax({
  url: url,
  method: 'GET',
  dataType: 'json',
  success: function(data) {
    console.log(data);
  },
});