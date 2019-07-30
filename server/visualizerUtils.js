function load_models() {
    console.log("Loading models");
    $.ajax({
        url: '/models',
        type: 'get',
        success: function (data) {
            models_data = data.models;
            modules_info = data.modules_info;
            models = {};
            for (var i = 0; i< models_data.length; i++) {
                model = JSON.parse(models_data[i]);
                models[model.modelId] = model;
            }
            set_parameter_filter();
            set_metric_filter();

            display_models();
        }
    });
};

function set_parameter_filter() {
    $('.parameters').html("");
    var parameters = [];
    var _module;
    var num_parameters;
    for (var module_name in modules_info) {
        module_info = JSON.parse(modules_info[module_name]);
        num_parameters = module_info.num_parameters;
        for (var i = 0; i < num_parameters; i++) {
            parameters.push(module_info.parameters[i].name);
        }
    }
    var html = new EJS({url : '/parameters.ejs'}).render({'parameters': parameters});
    $('.parameters').append($(html));
};

function set_metric_filter() {
    $('.metrics').html("");
    var metrics = [];
    var model;
    var runs;
    for (var modelId in models) {
        model = models[modelId];
        runs = model.runs;
        for (var runId in runs) {
            run = runs[runId];
            run_modules = run.metrics;
            for (var _module in run_modules) {
                module_metrics = run.metrics[_module];
                for (var metric in module_metrics) {
                    if (!metrics.includes(metric)) {
                        metrics.push(metric);
                    }
                }
            }
        }
    }
    var html = new EJS({url : '/metrics.ejs'}).render({'metrics': metrics});
    $('.metrics').append($(html));
}

function filter_model(model) {
    var model_params = model.parameters;
    if (model_params == undefined && filter_parameters.length > 0) {
        return true;
    }
    for (var paramNo in filter_parameters) {
        var param = filter_parameters[paramNo];
        if (!(param in model_params)) {
            return true;
        }
    }
    for (var metricNo in filter_metrics) {
        var metric = filter_metrics[metricNo];
        var has_metric = false;
        for (var runId in model.runs) {
            for (var _module in model.runs[runId].metrics) {
                if (metric in model.runs[runId].metrics[_module]) {
                    has_metric = true;
                }
            }
        }
        if (!has_metric) {
            return true;
        }
    }
    return false;
};

function display_models() {
    $('.models').html("");
    var model;
    for (var modelId in models) {
        model = models[modelId];
        if (filter_model(model)) {
            continue;
        }
        var runs = model.runs;
        var obj = get_modules_and_metrics(runs);
        var metrics = obj.metrics;
        model['runs_amount'] = obj.runs_amount;
        var html = new EJS({url : '/model.ejs'}).render({'model': model, 'filter_parameters': filter_parameters, 'filter_metrics': filter_metrics, 'runs': runs, 'modules': obj.modules, 'metrics' : metrics, 'metric_values': obj.metric_values});
        $('.models').append($(html));
    }
};

function get_modules_and_metrics(runs) {
    var modules = [];
    var metrics = {};
    var metric_values = {};
    var runs_amount = 0;
    for (var runId in runs) {
        runs_amount += 1;
        run = runs[runId];
        run_modules = run.metrics;
        for (var _module in run_modules) {
            if (!modules.includes(_module)) {
                modules.push(_module);
                metrics[_module] = [];
            }
            module_metrics = run.metrics[_module];
            for (var metric in module_metrics) {
                if (!metrics[_module].includes(metric)) {
                    metrics[_module].push(metric);
                }
                metric_values[metric] = module_metrics[metric];
            }
        }
    }
    return {'modules': modules, 'metrics': metrics, 'runs_amount': runs_amount, 'metric_values': metric_values};
};

function on_click_model(modelId) {
    model = models[modelId];
    load_diagram(model);
};

function see_more(event, modelId) {
    var addId = "add_" + modelId;
    var display = document.getElementById(addId).style.display;
    if (display == "flex") {
        document.getElementById(addId).style.display = "none";
    } else {
        document.getElementById(addId).style.display = "flex";
    }
    event.stopPropagation();
};

function switchSelect(x) {
    if (x.dataset.selected == 'true') {
        x.dataset.selected = 'false';
        x.style.backgroundColor = "rgb(241, 241, 241)";
    } else {
        x.dataset.selected = 'true';
        x.style.backgroundColor = "rgb(221, 221, 221)";
    }
    updateFilters(x);
};

function updateFilters(x) {
    if (x.dataset.selected == 'true') {
        if (x.dataset.type == 'parameter') {
            filter_parameters.push(x.dataset.value);
        } else {
            filter_metrics.push(x.dataset.value);
        }
    } else {
        if (x.dataset.type == 'parameter') {
            for( var i = filter_parameters.length - 1; i >= 0; i--){ 
                if (filter_parameters[i] === x.dataset.value) {
                    filter_parameters.splice(i, 1);
                }
            }
        } else {
            for( var i = filter_metrics.length - 1; i >= 0; i--) {
                if (filter_metrics[i] === x.dataset.value) {
                    filter_metrics.splice(i, 1);
                }
            }
        }
    }
    display_models();
};