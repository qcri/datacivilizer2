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
var path = require('path');
var fs = require('fs');
const { spawn } = require('child_process');

var dataVizPath = "";
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
        console.log("send event to SSE stream "+JSON.stringify(data));
        this.res.write("data: " + JSON.stringify(data) + "\n\n");
    };
    Connection.prototype.sendSplitUpdate = function (data) {
        console.log("send event to SSE stream "+JSON.stringify(data));
        this.res.write("event: split_update\ndata: " + JSON.stringify(data) + "\n\n");
    };
    Connection.prototype.finish_run = function (data) {
        console.log("send event to SSE stream "+JSON.stringify(data));
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

app.get('/vizFrame', function (request, response) {
    response.sendfile(path.resolve('./eeg_renderer/eeg_renderer.html'));
});

app.get('/setViz', function (request, response) {
    dataVizPath = request.query.pathJSON;
    response.send("ok");
});

app.get('/vizData', function (request, response) {
    var rawdata = fs.readFileSync(dataVizPath);
    var data_series = JSON.parse(rawdata);
    console.log("data")
    response.send(data_series)
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

app.get('/DataInspector.js', function (request, response) {
    response.sendfile(path.resolve('../extensions/DataInspector.js'));
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

app.get('/visualizer.css', function (request, response) {
    response.sendfile(path.resolve('./css/visualizer.css'));
});

app.get('/debugger.css', function (request, response) {
    response.sendfile(path.resolve('./css/debugger.css'));
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
function run_pipeline(modelId, runNo, pipeline_map, in_map, debugger_type) {

    //create output map
    var out_map = new Map();

    args = ["debugger.py"];
    var num_modules = pipeline_map.size;
    args.push(modelId);
    args.push(runNo);
    args.push(num_modules);
    args.push(debugger_type);

    for (var node_id of pipeline_map.keys()) {
        var node = pipeline_map.get(node_id).node;
        var cmd_name = node.cmd;
        var json_file = cmd_name + ".json";
        var module_info = JSON.parse(fs.readFileSync(json_file, 'utf8'));
        var cmd_path = module_info.cmd_path;
        var num_inputs = module_info.num_inputs;
        var num_outputs = module_info.num_outputs;
        var num_params = module_info.num_parameters;
        var params = module_info.parameters;

        if (cmd_name == "mod_changePoints")
            out_map[node_id] = "out_" + node_id + ".jpg";
        else
            out_map[node_id] = "out_" + node_id + ".mat";

        // get input files list
        var module_args = [];
        module_args.push(cmd_path);

        // push input files
        module_args.push(num_inputs);
        if (cmd_name == "mod_source")
            module_args.push(node.path)
        else {
            for (var n of in_map[node_id]) {
                module_args.push(out_map[n]);
            }
        }

        // push output file name
        module_args.push(num_outputs);
        module_args.push(out_map[node_id]);

        // push parameters
        module_args.push(num_params);
        for (var i=0; i<num_params; i++) {
            var param_type = params[i].type;
            var param = node[params[i].name];
            var found_type = typeof(param);
            if (found_type == param_type) {
                module_args.push(node[params[i].name]);
            } else {
                console.log("Wrong type for parameter " + params[i].name + ", expected " + param_type + ", found " + found_type);
                console.log("Using default value");
                module_args.push(params[i].default_value);
            }
        }

        // push splits
        if (node.splits == "") {
            module_args.push(0);
        } else {
            var splits = node.splits.split(',').map(Number);
            module_args.push(splits.length);
            module_args = module_args.concat(splits);
        }

        console.log(module_args);
        args = args.concat(module_args);
    }

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
    var pipeline = request.body;
    const modelId = pipeline.modelId;
    const runNo = pipeline.runNo;
    const debugger_type = pipeline.debugger_type;
    delete pipeline.debugger_type;

    // get parameters for run
    var sortOp = get_sortOp(pipeline);
    const sorted = sortOp.sort();
    var input_map = get_input_map(sortOp.nodes);

    // run the pipeline
    run_pipeline(modelId, runNo, sorted, input_map, debugger_type);
    var model_debug_info = {
        'modelId': modelId,
        'runNo': runNo,
        'modules': []
    }
    var node;
    for (var node_id of sorted.keys()) {
        node = sorted.get(node_id).node;
        var splits = [];
        if (node.splits == "") {
            splits = [100];
        } else {
            splits = splits.concat(node.splits.split(',').map(Number));
            splits.push(100);
        }
        console.log(splits);
        model_debug_info.modules.push({
            'name': node.cmd,
            'splits': splits,
            'split_outputs': []
        });
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

    connection.sendSplitUpdate(request.body);
    response.end();
});

app.post('/finish_run', function (request, response) {

    var obj = request.body;
    var metric_file_name = obj.metric_file_name;
    var modelId = obj.modelId;
    var runNo = obj.runNo;

    var metrics = JSON.parse(fs.readFileSync(metric_file_name, 'utf8'));
    console.log(metrics);
    fs.unlinkSync(metric_file_name);

    save_run(modelId, runNo, metrics)
    connection.finish_run(obj)
    response.end()
});

function remove_dir(dir_name) {
    console.log("Removing directory " + dir_name)
    try {
        fs.readdirSync(dir_name).forEach(function(filename, index){
            var file_path = path.join(dir_name, filename)
            fs.unlinkSync(file_path);
        });
        fs.rmdirSync(dir_name);
        console.log("Directory successfully removed")
    } catch (err) {
        console.log("An error occurred, trying again in 30 seconds")
        setTimeout(remove_dir, 30000, dir_name)
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

    var modules_info = {};

    dir_name = './';
    var regex = /^mod_.*\.json$/;
    fs.readdirSync(dir_name).filter(fn => regex.test(fn)).forEach(handle_module_file);
    
    function handle_module_file(file_name) {
        const pathname = dir_name + file_name;
        var obj = JSON.parse(fs.readFileSync(pathname, 'utf8'));
        modules_info[file_name.substring(0,file_name.length-5)] = JSON.stringify(obj);
    };
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

var server = app.listen(8080, function () {
    var host = server.address().address
    var port = server.address().port

    console.log("Example app listening at http://%s:%s", host, port)
})