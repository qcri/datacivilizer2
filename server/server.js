/**
 * A nodejs web server that acts as the backend of DC2
 * various routes are defined including running and saving client-authored pipelines
 * Individual DC2 modules are executed through Python wrappers
 *
 * @author  Elkindi Rezig
 * @institution MIT
 */

var express = require('express');
var app = express();
var request = require('request');
var path = require('path');
var fs = require('fs');
const { execSync, spawn } = require('child_process');
const csv = require('csv-parser');
const path_sort = require('path-sort');

var dataVizPath = "";
var trackingModuleName = "";
var colorVizTracker = "";
var setVizPicture = "";
var pklFileBoolean = "";
var running_models = [];
var paused_models = [];
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
    Connection.prototype.sendSplitUpdate = function (data) {
        console.log("send split update event to SSE stream "+JSON.stringify(data));
        this.res.write("event: split_update\ndata: " + JSON.stringify(data) + "\n\n");
    };
    Connection.prototype.sendTrackingUpdate = function (data) {
        console.log("send tracking update event to SSE stream "+JSON.stringify(data));
        this.res.write("event: tracking_update\ndata: " + JSON.stringify(data) + "\n\n");
    };
    Connection.prototype.finish_run = function (data) {
        console.log("send finished run event to SSE stream "+JSON.stringify(data));
        this.res.write("event: finish_run\ndata: " + JSON.stringify(data) + "\n\n");
    };
    return Connection;
}());

app.get('/registerEditor', function(req,res){
    console.log("Editor is connecting");
    var sseConnection = new Connection(res);
    res.sseConnection = sseConnection;
    sseConnection.setup();
    connection = sseConnection;
    connection.send({'data': 'Connection established'});
});

const {TopologicalSort} = require('topological-sort');
app.use(express.json());

app.get('/', function (request, response) {
    response.sendfile(path.resolve('./editor.html'));
});

app.get('/idTrackingModule', function (request, response) {
  trackingModuleName = request.query.moduleName;
  response.send("ok");
});

app.get('/vizFrame', function (request, response) {
    response.sendfile(path.resolve('./eeg_renderer/eeg_renderer.html'));
});

app.get('/setViz', function (request, response) {
    filepath = request.query.pathJSON;
    colorVizTracker = request.query.visualizeColorIds;
    dataVizPath = filepath;
    if (filepath.endsWith('.pkl')) {
        pklFileBoolean = true;
        dataVizPath = "./Data/plk_viz.json";
        execSync('python utils/pklToJson.py ' + filepath + ' ' + dataVizPath, {stdio: 'inherit'});
    } else {
        pklFileBoolean = false;
    }
    response.send("ok");
});

app.get('/vizData', function (request, response) {
    var rawdata = fs.readFileSync(dataVizPath);
    var data_series = JSON.parse(rawdata);
    console.log("data")
    response.send(data_series)
});

app.get('/pklFileOrNot', function (request, response) {
    response.send(pklFileBoolean);
});
    
app.get('/vizIdTracker', function (request, response) {
    if (colorVizTracker == 0) {
        var trackingFilePath = dataVizPath.substring(0, dataVizPath.lastIndexOf('/')) + '/tracking_file.json';
        if (trackingFilePath) {
            var trackingFileArray = fs.readFileSync(trackingFilePath);
            var trackingFileParse = JSON.parse(trackingFileArray);
            var moduleName = trackingFileParse[trackingModuleName];
            var moduleElements;
            var trackingFileIds = new Array();
            for (moduleElements of moduleName) {
                trackingFileIds.push(moduleElements['start_id']);
                trackingFileIds.push(moduleElements['num_segments']);
            }
            response.send(trackingFileIds);
        } else {
          response.send('ok');
        }
    } else if (colorVizTracker == 1) {
        response.send('ok');
    }
});

app.get('/csvVizList', function (request, response) {
    results = []
    fs.createReadStream(request.query.pathCsv)
      .pipe(csv({'headers': false}))
      .on('data', (data) => results.push(data['0']))
      .on('end', () => {
        response.send({'list': path_sort(results)})
      });
});

app.get('/csvGraphData', function (request, response) {
    labels = []
    chart1 = {'chartContainer': 'myChart1', 'title': 'Training loss', 'points': []}
    chart2 = {'chartContainer': 'myChart2', 'title': 'Training accuracy', 'points': []}
    chart3 = {'chartContainer': 'myChart3', 'title': 'Validation loss', 'points': []}
    chart4 = {'chartContainer': 'myChart4', 'title': 'Validation accuracy', 'points': []}
    fs.createReadStream(request.query.pathCsv)
        .pipe(csv({'headers': false}))
        .on('data', (data) => {
            labels.push(data[0])
            chart1.points.push(data[1])
            chart2.points.push(data[2])
            chart3.points.push(data[3])
            chart4.points.push(data[4])
        })
        .on('end', () => {
            response.send({'labels': labels, 'data': [chart1, chart2, chart3, chart4]})
        });
});

app.get('/vizPicture', function (request, response) {
    response.sendfile(path.resolve(setVizPicture));
});

app.get('/setImageViz', function (request, response) {
    setVizPicture = request.query.pathJSON;
    response.send("ok");
});

app.get('/lpf.js', function (request, response) {
    response.sendfile(path.resolve('./eeg_renderer/lpf.js'));
});

// app.get('/data1.js', function (request, response) {
//     response.sendfile(path.resolve('./eeg_renderer/data1.js'));
// });

app.get('/data3.js', function (request, response) {
    response.sendfile(path.resolve('./eeg_renderer/data3.js'));
});

app.get('/data_from_file', function (request, response) {
    response.sendfile(path.resolve('./Data/data_json_new.json'));
});

app.get('/go.js', function (request, response) {
    response.sendfile(path.resolve('../release/go.js'));
});

app.get('/Figures.js', function (request, response) {
    response.sendfile(path.resolve('../extensions/Figures.js'));
});

app.get('/dragscroll.js', function (request, response) {
    response.sendfile(path.resolve('../extensions/dragscroll.js'));
});

app.get('/DataInspector.js', function (request, response) {
    response.sendfile(path.resolve('../extensions/DataInspector.js'));
});

app.get('/Chart.js', function (request, response) {
    response.sendfile(path.resolve('../extensions/Chart.js'));
});

app.get('/DataInspector.css', function (request, response) {
    response.sendfile(path.resolve('../extensions/DataInspector.css'));
});

app.get('/versioningUtils.js', function (request, response) {
    response.sendfile(path.resolve('./versioningUtils.js'));
});

app.get('/visualizerUtils.js', function (request, response) {
    response.sendfile(path.resolve('./visualizerUtils.js'));
});

app.get('/debuggerUtils.js', function (request, response) {
    response.sendfile(path.resolve('./debuggerUtils.js'));
});

app.get('/trackingUtils.js', function (request, response) {
    response.sendfile(path.resolve('./trackingUtils.js'));
});

app.get('/ejs_production.js', function (request, response) {
    response.sendfile(path.resolve('./ejs_production.js'));
});

app.get('/model.ejs', function (request, response) {
    response.sendfile(path.resolve('./ejs/model.ejs'));
});

app.get('/parameters.ejs', function (request, response) {
    response.sendfile(path.resolve('./ejs/parameters.ejs'));
});

app.get('/metrics.ejs', function (request, response) {
    response.sendfile(path.resolve('./ejs/metrics.ejs'));
});

app.get('/debugger_tab.ejs', function (request, response) {
    response.sendfile(path.resolve('./ejs/debugger_tab.ejs'));
});

app.get('/debugger_model.ejs', function (request, response) {
    response.sendfile(path.resolve('./ejs/debugger_model.ejs'));
});

app.get('/tracked_id_range.ejs', function (request, response) {
    response.sendfile(path.resolve('./ejs/tracked_id_range.ejs'));
});

app.get('/tracking_filter.ejs', function (request, response) {
    response.sendfile(path.resolve('./ejs/tracking_filter.ejs'));
});

app.get('/edv_list_elem.ejs', function (request, response) {
    response.sendfile(path.resolve('./ejs/edv_list_elem.ejs'));
});

app.get('/visualizer.css', function (request, response) {
    response.sendfile(path.resolve('./css/visualizer.css'));
});

app.get('/debugger.css', function (request, response) {
    response.sendfile(path.resolve('./css/debugger.css'));
});

app.get('/Data/out_-1.jpg', function (request, response) {
    response.sendfile(path.resolve('./Data/out_-1.jpg'));
});

/**
 * Runs a DC2 pipeline
 * args
 @pipeline (Map): maps node id to its JSON description. Assumes the nodes are sorted in toplogical order
 @in_map (Map): maps input dependencies for each node id
 * process
 * 1/ loop through nodes in the graph
 * 2/ call the corresponding python script depending on the value of cmd attribute
 * 3/ params are passed automatically:
 *    3.1/ data source operator specifies file path for the first module(s)
 *    3.2/ get output file path from module
 *    3.3/ pass output file (and possible other files) as input file(s) to the next module
 */
function run_pipeline(modelId, runNo, pipeline_map, in_map, debugger_type, tracking_filters) {

    //create output map
    var out_map = new Map();

    const dirName = modelId + '_' + runNo;
    const run_info_filename = 'run_info.json';
    const tracking_info_filename = 'tracking_info.json';

    args = ["utils/debugger.py", dirName, run_info_filename, tracking_info_filename];

    var num_modules = 0;
    var run_info = {
        'modelId': modelId,
        'runNo': runNo,
        'debugger_type': debugger_type,
        'metric_file': "metric_temp.json",
        'max_processes': 2,
        'pipeline': []
    }

    var tracking_info = {
        'filters': tracking_filters,
        'type': 'eager',
        'splitter_type': 'segments',
        'filename': 'tracking_file.json'
    }

    if (tracking_filters.length == 0) {
        tracking_info['active'] = false;
    } else {
        tracking_info['active'] = true;
    }

    for (var node_id of pipeline_map.keys()) {
        var node = pipeline_map.get(node_id).node;
        var cmd_name = node.cmd;

        if (cmd_name == "mod_source") {
            out_map[node_id] = [node.path];
            continue;
        }

        num_modules += 1;
        var json_file = cmd_name + ".json";
        var module_info = JSON.parse(fs.readFileSync(json_file, 'utf8'));
        var cmd_path = module_info.cmd_path;
        var num_inputs = module_info.num_inputs;
        var in_types = module_info.in_types;
        var num_outputs = module_info.num_outputs;
        var out_types = module_info.out_types;
        var viz_type = module_info.viz_type;
        var num_params = module_info.num_parameters;
        var params = module_info.parameters;

        var inputs = [];
        var outputs = [];
        var parameters = [];
        var splits = [];

        if (node_id in in_map) {
            for (var n of in_map[node_id]) {
                for (var o of out_map[n]) {
                    inputs.push(o);
                }
            }
        }

        out_map[node_id] = []
        for (var i = 0; i < num_outputs; i++) {
            if (out_types[i] == 'dir') {
                out_name = "out_" + node_id;
            } else {
                out_name = "out_" + node_id + out_types[i];
            }
            out_map[node_id].push(out_name);
            outputs.push(out_name);
        }

        var viz = undefined;
        if (module_info.viz) {
            viz = module_info.viz;
            for (var viz_elem of viz) {
                viz_elem.filename = "viz_" + node_id + viz_elem.extension;
            }
        }

        for (var i=0; i<num_params; i++) {
            var param_type = params[i].type;
            var param = node[params[i].name];
            var found_type = typeof(param);
            if (found_type == param_type) {
                parameters.push(node[params[i].name]);
            } else {
                console.log("Wrong type for parameter " + params[i].name + ", expected " + param_type + ", found " + found_type);
                console.log("Using default value");
                parameters.push(params[i].default_value);
            }
        }

        if ('splits' in node) {
            if (node.splits != "") {
                splits = node.splits.split(',').map(Number);
            }
        }
        splits.push(100);

        console.log("Viz:");
        console.log(viz);

        run_info['pipeline'].push({
            'cmd_name': cmd_name,
            'cmd_path': cmd_path,
            'num_inputs': num_inputs,
            'in_types': in_types,
            'inputs': inputs,
            'num_outputs': num_outputs,
            'out_types': out_types,
            'outputs': outputs,
            'viz': viz,
            'num_params': num_params,
            'params': parameters,
            'splits': splits
        })
    }

    run_info['num_modules'] = num_modules;

    console.log("Run info")
    console.log(run_info)
    console.log("Tracking info")
    console.log(tracking_info)

    if (!fs.existsSync('./Data/' + dirName)){
        fs.mkdirSync('./Data/' + dirName);
        console.log("Directory " + './Data/' + dirName + " created")
    } else {
        console.log("Directory " + './Data/' + dirName + " already exists")
    }
    run_obj = JSON.stringify(run_info, null, 4);
    tracking_obj = JSON.stringify(tracking_info, null, 4);
    fs.writeFileSync('./Data/' + dirName + '/' + run_info_filename, run_obj, 'utf8');
    fs.writeFileSync('./Data/' + dirName + '/' + tracking_info_filename, tracking_obj, 'utf8');
    var child = spawn('python ' + args.join(' '), {'shell': true, 'stdio': 'inherit'});
    running_models.push(modelId.toString() + '_' + runNo.toString());
};

function get_sortOp(pipeline) {

    const nodes = new Map();
    for (var id in pipeline.nodeDataArray) {
        nodes.set(pipeline.nodeDataArray[id].key, pipeline.nodeDataArray[id]);
    }
    const sortOp = new TopologicalSort(nodes);
    for (var edge in pipeline.linkDataArray) {
        sortOp.addEdge(pipeline.linkDataArray[edge].from, pipeline.linkDataArray[edge].to);
    }
    console.log("sort op: ", sortOp);
    return sortOp;
}

//map each module to its set of input sources (ds operator or out file)
function get_input_map(nodes) {

    var in_map = new Map();
    for (var node_id of nodes.keys()) {
        for (var value_id of nodes.get(node_id).children.keys()) {
            if (value_id in in_map) {
                in_map[value_id].push(node_id);
            } else {
                in_map[value_id] = [];
                in_map[value_id].push(node_id);
            }
        }
    }
    //sort node ids (left edges have lower order in argument list than right edges)
    for (var key in in_map)
        in_map[key].sort(function (a, b) {
            return b - a
        });
    console.log("in map: ", in_map);
    return in_map;
}

// Save metrics from a new run in the file containing the model
function save_run(modelId, runNo, metrics) {

    const filename = "./saved_models/model_" + modelId + ".json";
    var pipeline = JSON.parse(fs.readFileSync(filename, 'utf8'));
    if (!('runs' in pipeline)) {
        pipeline['runs'] = []
    }
    pipeline['runs'].push({'runNo' : runNo, 'metrics' : metrics});
    obj = JSON.stringify(pipeline, null, 4);
    fs.writeFileSync(filename, obj, 'utf8');
};

function get_model_params(modelJsonString) {
    var model = JSON.parse(modelJsonString);
    var module_array = model.nodeDataArray;
    var _module;
    var parameters = {}
    for (var i in module_array) {
        _module = module_array[i];
        delete _module.key;
        delete _module.cmd;
        delete _module.figure;
        delete _module.fill;
        delete _module.loc;
        delete _module.text;
        delete _module.splits;
        for (var j in _module) {
            parameters[j] = _module[j];
        }
    }
    return parameters;
};

app.post('/run', function (request, response) {

    console.log("running pipeline requested");
    console.log(request.body);

    //parse JSON file
    var pipeline = request.body.pipeline;
    const modelId = pipeline.modelId;
    const runNo = pipeline.runNo;
    const debugger_type = request.body.debugger_type;
    const tracking_filters = request.body.tracking_filters;

    startNewRun(modelId, runNo);

    // get parameters for run
    var sortOp = get_sortOp(pipeline);
    const sorted = sortOp.sort();
    var input_map = get_input_map(sortOp.nodes);

    // run the pipeline
    run_pipeline(modelId, runNo, sorted, input_map, debugger_type, tracking_filters);
    var model_debug_info = {
        'modelId': modelId,
        'runNo': runNo,
        'modules': [],
    }
    if (tracking_filters.length == 0) {
        model_debug_info['tracking'] = false;
    } else {
        model_debug_info['tracking'] = true;
    }
    var node;
    for (var node_id of sorted.keys()) {
        node = sorted.get(node_id).node;
        if (node.cmd != "mod_source") {
            var splits = [];
            if (node.splits == "" || debugger_type == 'no_split') {
                splits = [100];
            } else {
                splits = splits.concat(node.splits.split(',').map(Number));
                splits.push(100);
            }
            model_debug_info.modules.push({
                'name': node.cmd,
                'splits': splits,
                'split_outputs': []
            });
        }
    }
    console.log(model_debug_info);
    response.send(JSON.stringify(model_debug_info));
});

app.post('/pause_pipeline', function (request, response) {

    console.log("Pausing pipeline");
    var mrId = request.body.mrId;
    paused_models.push(mrId);
    for (var i = running_models.length - 1; i >= 0; i--) {
        if (running_models[i] == mrId) {
            running_models.splice(i,1);
        }
    }
    response.end();
});

app.post('/resume_pipeline', function (request, response) {

    console.log("Resuming pipeline");
    var mrId = request.body.mrId;
    running_models.push(mrId);
    for (var i = paused_models.length - 1; i >= 0; i--) {
        if (paused_models[i] == mrId) {
            paused_models.splice(i,1);
        }
    }
    response.end();
});

app.post('/kill_pipeline', function (request, response) {

    console.log("Killing pipeline");
    var mrId = request.body.mrId;
    for (var i = running_models.length - 1; i >= 0; i--) {
        if (running_models[i] == mrId) {
            running_models.splice(i,1);
        }
    }
    for (var i = paused_models.length - 1; i >= 0; i--) {
        if (paused_models[i] == mrId) {
            paused_models.splice(i,1);
        }
    }
    response.end();
});

app.get('/get_status', function (request, response) {

    var model_run_info = request.query;
    var modelId = model_run_info.modelId;
    var runNo = model_run_info.runNo;
    var id = modelId + '_' + runNo;
    if (running_models.includes(id)) {
        response.send('running');
    } else if (paused_models.includes(id)) {
        response.send('paused');
    } else {
        response.send('stopped')
    }
});

app.post('/split', function (request, response) {

    sendDashboardUpdate(request.body);
    connection.sendSplitUpdate(request.body);
    response.end();
});

app.post('/update_tracking_file', function (request, response) {

    var obj = request.body;
    var tracking_file_name = obj.tracking_file_name;
    var tracking_ids = JSON.parse(fs.readFileSync(tracking_file_name, 'utf8'));
    var modelId = obj.modelId;
    var runNo = obj.runNo;
    var mrId = modelId + '_' + runNo;
    data = {'mrId': mrId, 'tracking_ids': tracking_ids}
    connection.sendTrackingUpdate(data);
    response.end();
});

app.post('/finish_run', function (request, response) {

    var obj = request.body;
    var metric_file_name = obj.metric_file_name;
    var modelId = obj.modelId;
    var runNo = obj.runNo;

    /* TODO update tracking file if present */
    /*var tracking_file_name = obj.tracking_file_name;*/

    var metrics = JSON.parse(fs.readFileSync(metric_file_name, 'utf8'));
    console.log(metrics);
    fs.unlinkSync(metric_file_name);

    save_run(modelId, runNo, metrics)
    connection.finish_run(obj)
    response.end()
});

function remove_dir(dir_name, is_first=true) {
    if (is_first) {
        console.log("Removing directory " + dir_name)
    }
    try {
        fs.readdirSync(dir_name).forEach(function(filename, index){
            var curPath = path.join(dir_name, filename)
            if (fs.lstatSync(curPath).isDirectory()) { // recurse
                remove_dir(curPath, false);
            } else { // delete file
                fs.unlinkSync(curPath);
            }
        });
        fs.rmdirSync(dir_name);
        if (is_first) {
            console.log("Directory successfully removed")
        }
    } catch (err) {
        if (is_first) {
            console.log("An error occurred, trying again in 30 seconds")
            setTimeout(remove_dir, 30000, dir_name)
        } else {
            throw(err)
        }
    }
};

app.post('/remove_tmp_run_dir', function (request, response) {

    var mrId = request.body.mrId;
    var dir_name = './Data/' + mrId
    remove_dir(dir_name)
    response.end()
});

app.post('/saveModel', function(request, response) {

    console.log("saving model data");
    var model = request.body;
    delete model.debugger_type;
    const filename = "saved_models/" + "model_" + model.modelId + ".json"

    if (model.runNo == 1) {
        var parameters = get_model_params(JSON.stringify(model));
        model['parameters'] = parameters;
        var obj = JSON.stringify(model, null, 4);
        fs.writeFileSync(filename, obj, 'utf8');
    } else {
        var prev_model = JSON.parse(fs.readFileSync(filename, 'utf8'));
        prev_model.modelData = model.modelData;
        prev_model.nodeDataArray = model.nodeDataArray;
        prev_model.linkDataArray = model.linkDataArray;
        prev_model.runNo = model.runNo;
        delete prev_model.debugger_type;
        var obj = JSON.stringify(prev_model, null, 4);
        fs.writeFileSync(filename, obj, 'utf8');
    }
    response.end()
});

app.post('/saveModelVersions', function (request, response) {

    console.log("saving versioning data");
    var obj = JSON.stringify(request.body, null, 4);
    fs.writeFileSync("versioningData.json", obj, 'utf8');
    response.end();
});

app.get('/getModelVersions', function (request, response) {

    console.log("loading versioning data");
    response.sendfile(path.resolve("versioningData.json"));
});

function get_modules_info() {

    function handle_module_file(file_name) {
        const pathname = dir_name + file_name;
        var obj = JSON.parse(fs.readFileSync(pathname, 'utf8'));
        modules_info[file_name.substring(0,file_name.length-5)] = JSON.stringify(obj);
    };

    var modules_info = {};
    dir_name = './';
    var regex = /^mod_.*\.json$/;
    fs.readdirSync(dir_name).filter(fn => regex.test(fn)).forEach(handle_module_file);
    return modules_info
};

app.get('/modules_info', function(request, response) {
    var modules_info = get_modules_info();
    response.send(modules_info);
});

app.get('/models', function(request, response) {
    console.log("Loading models")

    var models = [];

    var dir_name = './saved_models/';
    fs.readdirSync(dir_name).forEach(handle_model_file);

    function handle_model_file(file_name) {
        const pathname = dir_name + file_name;
        var obj = JSON.parse(fs.readFileSync(pathname, 'utf8'));
        models.push(JSON.stringify(obj));
    };

    var modules_info = get_modules_info();

    response.send({'models': models, 'modules_info': modules_info});
});

app.get('/request_pipeline', function (request, response) {

    var obj = JSON.stringify(request.query);
    var jss = JSON.parse(obj);
    var keys = Object.keys(jss);
    response.sendfile(path.resolve(keys[0]) + '.json');
});

app.get('/fig.png', function (request, response) {

    response.sendfile(path.resolve('fig.png'));
});

app.get('/download_output', function (request, response) {

    var obj = JSON.stringify(request.query);
    var jss = JSON.parse(obj);
    var keys = Object.keys(jss);
    var file_name = path.resolve("Data/out_" + Object.keys(jss)[0]) + ".mat";
    var stats = fs.statSync(file_name)
    response.writeHead(200, {
        'Content-Type': 'application/x-binary',
        'Content-Length': stats["size"],
        'Content-Disposition': 'attachment; filename= out_' + Object.keys(jss)[0] + '.mat'
    });
    var readStream = fs.createReadStream(file_name);
    // We replaced all the event handlers with a simple call to readStream.pipe()
    readStream.pipe(response);
});

function startNewRun(modelId, runNo) {

    request.post(
        'http://localhost:9131/startNewRun',
        { json: { modelId: modelId, runNo: runNo } },
        function (error, response, body) {
            if (!error && response.statusCode == 200) {
                console.log(body);
            }
        }
    );
};

function sendDashboardUpdate(data) {

    request.post(
        'http://localhost:9131/updatePage',
        { json: { data: data } },
        function (error, response, body) {
            if (!error && response.statusCode == 200) {
                console.log(body);
            }
        }
    );
};

var server = app.listen(8080, function () {
    var host = server.address().address
    var port = server.address().port

    console.log("Example app listening at http://%s:%s", host, port)
})
