/* HTLM generic viz functions */
function open_viz(id) {
    var x = document.getElementById(id);
    if (x.className.indexOf("w3-show") == -1) {
        x.className = x.className.replace(" w3-hide", " w3-show");
    }
};

function close_viz(id) {
    var x = document.getElementById(id);
    if (x.className.indexOf("w3-hide") == -1) {
        x.className = x.className.replace(" w3-show", " w3-hide");
    }
};

function toggle_viz(id) {
    var x = document.getElementById(id);
    if (x.className.indexOf("w3-show") == -1) {
        x.className = x.className.replace(" w3-hide", " w3-show");
    } else {
        x.className = x.className.replace(" w3-show", " w3-hide");
    }
};

function toggle_arrow(id) {
    var x = document.getElementById(id);
    if (x.className.indexOf("fa-angle-up") == -1) {
        x.className = x.className.replace(" fa-angle-down", " fa-angle-up");
    } else {
        x.className = x.className.replace(" fa-angle-up", " fa-angle-down");
    }
};

function open_debugger() {
    var _debugger = document.getElementById('debugger');
    if (_debugger.className.indexOf("w3-show") == -1) {
        _debugger.className = _debugger.className.replace(" w3-hide", " w3-show");
    }
    var _diagram = document.getElementById("diagram");
    _diagram.style.width = "40%";
    myDiagram.requestUpdate();
};

function close_debugger() {
    var _debugger = document.getElementById('debugger');
    if (_debugger.className.indexOf("w3-hide") == -1) {
        _debugger.className = _debugger.className.replace(" w3-show", " w3-hide");
    }
    var _diagram = document.getElementById("diagram");
    _diagram.style.width = "80%";
    myDiagram.requestUpdate();
};

/* Modules output viz functions */

function visualizeTrackedFile(vizObjList, moduleName) {
    $.get('/idTrackingModule',
        {"moduleName" : moduleName})
        .done(function (response) {
            viz_type = vizObjList[0].type;
            viz_file = './Data/' + vizObjList[0].filename;
            if (viz_type == "eeg_json") {
                visualizeJson(viz_file, 0);
            } else {
                console.log("Wrong Function");
            }
        });
};

function visualizeObjList(vizObjList) {
    close_viz('edv_list_div')
    close_viz('graph_viz_div')
    for (var viz_elem of vizObjList) {
        viz_type = viz_elem.type;
        viz_file = './Data/' + viz_elem.filename
        if (viz_type == "image") {
            visualizeImage(viz_file);
        } else if (viz_type == "eeg_json") {
            visualizeJson(viz_file);
        } else if (viz_type == "pkl_dir") {
            visualizeCsv(viz_file);
        } else if (viz_type == "graph_data") {
            visualizeNnCsv(viz_file);
        }
    }
};

function visualizeFile(filepath) {
    close_viz('edv_list_div');
    close_viz('graph_viz_div');
    var extension = filepath.split('.').pop();
    if (extension == 'json') {
        visualizeJson(filepath);
    } else if (extension == 'jpg' || extension == 'png') {
        visualizeImage(filepath);
    } else if (extension == 'csv') {
        visualizeCsv(filepath);
    } else {
        console.log("Cannot visualize " + filepath);
    }
};

function visualizeCsv(filepath) {
    open_viz('edv_list_div');
    $('#edv_list').html("");
    console.log("visualizing csv: " + filepath);
    console.log(filepath.replace('.csv', '') + '/');
    $.get('/csvVizList',
        {"pathCsv": filepath})
        .done(function (response) {
            const l = response.list;
            for (const elem of l){
                var html = new EJS({url : '/edv_list_elem.ejs'}).render({'filepath': elem, 'prefix': filepath.replace('.csv', '') + '/'});
                $('#edv_list').append($(html));
            }
        });
};

function visualizeImage(filepath) {
    console.log("visualizing image: " + filepath);
    var iframe = document.getElementById('iframeViz');
    $.get('/setImageViz',
        {"pathJSON": filepath})
        .done(function (response) {
            iframe.setAttribute("src", "vizPicture");
            iframe.src = iframe.src;
            setTimeout(iFrameImageParams, 500);
        });
};

function visualizeJson(filepath, colorIdBoolean = 1) {
    console.log("visualizing json: " + filepath);
    var iframe = document.getElementById('iframeViz');
    $.get('/setViz',
    {"pathJSON": filepath, "visualizeColorIds": colorIdBoolean})
        .done(function (response) {
            iframe.setAttribute("src", "vizFrame");
            iframe.src = iframe.src;
            setTimeout(iFrameJsonParams, 500);
        });
};

function visualizeNnCsv(filepath) {
    open_viz('graph_viz_div');
    console.log("visualizing nncsv: " + filepath);
    $.get('/csvGraphData',
        {"pathCsv": filepath})
        .done(function (response) {
            const labels = response.labels;
            const data = response.data;
            console.log(data);
            for (const elem of data) {
                createGraph(labels, elem);
            }
        });
};

function createGraph(graph_labels, graph_data) {

    var myLineChart = new Chart(graph_data.chartContainer, {
        type: 'line',
        data: {
            labels: graph_labels,
            datasets: [{
                data: graph_data.points,
                label: "",
                borderColor: "#3e95cd",
                fill: false
            }]
        },
        options: {
            title: {
                display: true,
                text: graph_data.title
            },
            legend: {
                display: false
            },
            maintainAspectRatio: false
        }
    });
};