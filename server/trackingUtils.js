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

function showAppropriateForm(v) {
    form_elems = document.getElementsByClassName("tracking_form_elem")
    for (i = 0; i < form_elems.length; i++) {
        form_elems[i].style.display = "none";
    }
    if (v == "id") {
        form_elems = document.getElementsByClassName("tracking_form_elem")
        for (i = 0; i < form_elems.length; i++) {
            if (form_elems[i].name == "tr_id") {
                form_elems[i].style.display = "inline-block";
            }
        }
    } else if (v == 'id_range') {
        form_elems = document.getElementsByClassName("tracking_form_elem")
        for (i = 0; i < form_elems.length; i++) {
            if (form_elems[i].name == "tr_id_start" || form_elems[i].name == "tr_id_end") {
                form_elems[i].style.display = "inline-block";
            }
        }
    }
}

function newElement() {
    var inputValue = document.getElementById("tracking_filter_options").value + "(";
    var data = document.getElementById("tracking_filter_options").value;
    var li = document.createElement("li");
    var inputs = document.getElementsByClassName("tracking_form_elem");
    var first = true;
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].style.display != 'none') {
            if (inputs[i].value == "") {
                alert("Please fill all required fields")
                inputValue = "";
                break
            } else {
                data += "," + inputs[i].value;
                if (first) {
                    inputValue += inputs[i].value;
                    first = false;
                } else {
                    inputValue += ", " + inputs[i].value;
                }
            }
        }
    }
    if (inputValue != "") {
        inputValue += ")";
        var t = document.createTextNode(inputValue);
        li.setAttribute('data-value', data);
        li.appendChild(t);
        document.getElementById("tracking_filters").appendChild(li);

        var span = document.createElement("SPAN");
        var txt = document.createTextNode("\u00D7");
        span.onclick = function() {
            var li_elem = this.parentElement;
            var ul_elem = li.parentElement;
            ul_elem.removeChild(li)
        };
        span.className = "close";
        span.appendChild(txt);
        li.appendChild(span);
    }
} 