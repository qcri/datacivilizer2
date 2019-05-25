var request = new XMLHttpRequest();
request.open("GET", "/data_from_file", false);
request.send(null);
data_text = String(request.responseText);
var data_series = JSON.parse(data_text);
// var data_series = [];

// console.log(data);

var viewBox = "3702125 0 ";
