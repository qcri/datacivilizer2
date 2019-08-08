function get_tracking_filters() {
    var filter_nodes = document.getElementById("tracking_filters").children;
    var filters = []
    for (var i = filter_nodes.length - 1; i >= 0; i--) {
        filters.push(parse_tracking_filter(filter_nodes[i]));
    }
    return filters;
}

function parse_tracking_filter(filter_node) {
    var li = filter_node;
    var data = li.getAttribute('data-value');
    var data_arr = data.split(",");
    return {
        'type': data_arr.shift(),
        'params': data_arr.map(x => parseInt(x))
    };
}

function add_filter(filter_type) {
    if (filter_type == 'id') {
        var _id = document.getElementById("tracking_form_input_01").value;
        if (_id == "") {
            alert("Please fill all required fields")
            return
        } else {
            var html = new EJS({url : '/tracking_filter.ejs'}).render({'_type': filter_type, '_id': _id});
            $('.tracking_filters').append($(html));
        }
    } else if (filter_type == 'id_range') {
        var id_from = document.getElementById("tracking_form_input_02").value;
        var id_until = document.getElementById("tracking_form_input_03").value;
        if (id_from == "" || id_until == "") {
            alert("Please fill all required fields")
            return
        } else {
            var html = new EJS({url : '/tracking_filter.ejs'}).render({'_type': filter_type, 'id_from': id_from, 'id_until': id_until});
            $('.tracking_filters').append($(html));
        }
    }

};

function remove_filter(elem) {
    var li = elem.parentElement.parentElement.parentElement;
    var ul = li.parentElement;
    ul.removeChild(li);
};