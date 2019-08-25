/**
 * A nodejs web server that acts as the backend of the DC2 dashboard used for the demo
 *
 * @author  Maxime Schoemans
 * @institution MIT
 */

process.env.PWD = process.cwd()
var express = require('express');
var app = express();
app.use(express.static(process.env.PWD + '/public'));
var path = require('path');
var fs = require('fs');
const csv = require('csv-parser');
const { execSync } = require('child_process');

var image_path = "";
var dataVizPath = "";
var trackModName = "";
var current_page_type;
var current_modelId = '';
var current_runNo = '';
var connection;

var Connection = (function () {
    function Connection(res) {
        console.log(" sseMiddleware construct connection for response ");
        this.res = res;
    }
    Connection.prototype.setup = function () {
        console.log("set up SSE stream for response");
        this.res.writeHead(200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        });
    };
    Connection.prototype.send = function (data) {
        console.log("send message to SSE stream "+JSON.stringify(data));
        this.res.write("data: " + JSON.stringify(data) + "\n\n");
    };
    Connection.prototype.sendUpdate = function (data) {
        console.log("send update event to SSE stream "+JSON.stringify(data));
        this.res.write("event: update\ndata: " + JSON.stringify(data) + "\n\n");
    };
    Connection.prototype.sendPageSwitch = function (data) {
        console.log("send page switch event to SSE stream "+JSON.stringify(data));
        this.res.write("event: ps\ndata: " + JSON.stringify(data) + "\n\n");
    };
    Connection.prototype.sendPageReset = function (data) {
        console.log("send page reset event to SSE stream "+JSON.stringify(data));
        this.res.write("event: pr\ndata: " + JSON.stringify(data) + "\n\n");
    };
    return Connection;
}());

app.get('/registerDashboard', function(req,res) {
    console.log("Dashboard is connecting");
    var sseConnection = new Connection(res);
    res.sseConnection = sseConnection;
    sseConnection.setup();
    connection = sseConnection;
    connection.send({'data': 'Connection established'});
});

app.use(express.json());

app.get('/ml_dashboard.html', function (request, response) {
    response.sendfile(path.resolve('./ml_dashboard.html'));
});

app.get('/cleaning_dashboard.html', function (request, response) {
    response.sendfile(path.resolve('./cleaning_dashboard.html'));
});

app.get('/', function (request, response) {
    response.sendfile(path.resolve('./base_dashboard.html'));
});

app.get('/kyrix.js', function (request, response) {
    response.sendfile(path.resolve('./kyrix.js'));
});

app.get('/lpf.js', function (request, response) {
    response.sendfile(path.resolve('../server/eeg_renderer/lpf.js'));
});

app.get('/data3.js', function (request, response) {
    response.sendfile(path.resolve('../server/eeg_renderer/data3.js'));
});

app.get('/Chart.js', function (request, response) {
    response.sendfile(path.resolve('../extensions/Chart.js'));
});

app.get('/dragscroll.js', function (request, response) {
    response.sendfile(path.resolve('../extensions/dragscroll.js'));
});

app.post('/startNewRun', function (request, response) {

    current_modelId = request.body.modelId;
    current_runNo = request.body.runNo;

    console.log(current_modelId);
    console.log(current_runNo);

    // Verify model Id's before running
    var new_type = '';
    if (current_modelId == 3 || current_modelId == 5 || current_modelId == 4 || current_modelId == 0) {
        new_type = 'ml';
    } else if (current_modelId == 1 || current_modelId == 2) {
        new_type = 'cleaning';
    }

    console.log(new_type);
    if (current_page_type == new_type) {
        connection.sendPageReset(current_modelId);
    } else if (new_type == 'ml') {
        connection.sendPageSwitch({'html': 'ml_dashboard.html'});
        connection.sendPageReset(current_modelId);
    } else if (new_type == 'cleaning') {
        connection.sendPageSwitch({'html': 'cleaning_dashboard.html'});
        connection.sendPageReset(current_modelId);
    } else {
        connection.sendPageSwitch({'html': '/'});
    }
    current_page_type = new_type;
    response.end();
});

app.post('/updatePage', function (request, response) {
    console.log(request.body);
    const data = request.body.data;
    const modelId = data.modelId;
    const runNo = data.runNo;
    const split = data.split;
    if (split == 100 && modelId == current_modelId && runNo == current_runNo) {
        connection.sendUpdate(data);
    };
    response.end();
});

app.get('/getBarChartData', function (request, response) {
    var data = JSON.parse(fs.readFileSync('../server/Data/' + request.query.filepath));
    console.log(data);
    response.send({'data': data.accuracy});
});

app.get('/getLineChartData', function (request, response) {
    labels = [];
    chart1 = {'points': []};
    chart2 = {'points': []};
    chart3 = {'points': []};
    chart4 = {'points': []};
    fs.createReadStream('../server/Data/' + request.query.filepath)
        .pipe(csv({'headers': false}))
        .on('data', (data) => {
            labels.push(data[0]);
            chart1.points.push(data[1]);
            chart2.points.push(data[2]);
            chart3.points.push(data[3]);
            chart4.points.push(data[4]);
        })
        .on('end', () => {
            response.send({'labels': labels, 'data': [chart1, chart2, chart3, chart4]});
        });
});

app.get('/getImage', function (request, response) {
    const in_path = '../server/Data/' + request.query.filepath;
    const out_path = './public/' + request.query.filepath;
    if (!fs.existsSync(path.dirname(out_path))){
        fs.mkdirSync(path.dirname(out_path));
    }
    execSync('python copyFile.py ' + in_path + ' ' + out_path, {stdio: 'inherit'});
    response.end();
});

app.get('/vizFrame', function (request, response) {
    response.sendfile(path.resolve('../server/eeg_renderer/eeg_renderer.html'));
});

app.get('/setViz', function (request, response) {
    filepath = request.query.pathJSON;
    trackModName = request.query.moduleName;
    dataVizPath = filepath;
    response.send("ok");
});

app.get('/pklFileOrNot', function (request, response) {
    response.send(false);
});

app.get('/vizIdTracker', function (request, response) {
    var trackingFilePath = '../server/Data/' + dataVizPath.substring(0, dataVizPath.lastIndexOf('/')) + '/tracking_file.json';
    var trackingFileIds = new Array();
    if (fs.existsSync(trackingFilePath)) {
        var trackingFileArray = fs.readFileSync(trackingFilePath);
        var trackingFileParse = JSON.parse(trackingFileArray);
        var moduleName = trackingFileParse[trackModName];
        var moduleElements;
        for (moduleElements of moduleName) {
            trackingFileIds.push(moduleElements['start_id']);
            trackingFileIds.push(moduleElements['num_segments']);
        }
    }
    response.send(trackingFileIds);
});

app.get('/vizData', function (request, response) {
    var rawdata = fs.readFileSync('../server/Data/' + dataVizPath);
    var data_series = JSON.parse(rawdata);
    console.log("data")
    response.send(data_series)
});

var server = app.listen(9131, function () {
    var host = server.address().address
    var port = server.address().port

    console.log("Example app listening at http://%s:%s", host, port)
})
