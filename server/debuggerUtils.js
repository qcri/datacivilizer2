function toggle_border(id) {
    var x = document.getElementById(id);
    if (x.className.indexOf("w3-border-bottom") == -1) {
        x.className = x.className.replace("w3-border-top", "w3-border-bottom");
    } else {
        x.className = x.className.replace("w3-border-bottom", "w3-border-top");
    }
};

function select_debugging_tab(id) {
    var x = document.getElementById(id);
    if (x.className.indexOf("w3-opacity") != -1) {
        x.className = x.className.replace(" w3-opacity", "");
    }
};

function deselect_debugging_tab(id) {
    var x = document.getElementById(id);
    if (x.className.indexOf("w3-opacity") == -1) {
        x.className += " w3-opacity";
    }
};

function pause_pipeline(mrId) {
    toggle_viz('debugger_running_'  + mrId);
    toggle_viz('debugger_paused_'  + mrId);
    $.ajax({
        url: '/pause_pipeline',
        type: 'post',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({'mrId': mrId}),
        success: function (data) {
            console.log("success!");
        }
    });
};

function resume_pipeline(mrId) {
    toggle_viz('debugger_running_'  + mrId);
    toggle_viz('debugger_paused_'  + mrId);
    $.ajax({
        url: '/resume_pipeline',
        type: 'post',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({'mrId': mrId}),
        success: function (data) {
            console.log("success!");
        }
    });
};

function stop_pipeline(mrId) {
    close_viz('debugger_running_'  + mrId);
    close_viz('debugger_paused_'  + mrId);
    toggle_viz('debugger_stopped_'  + mrId);
    $.ajax({
        url: '/kill_pipeline',
        type: 'post',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({'mrId': mrId}),
        success: function (data) {
            console.log("success!");
        }
    });
};


function finish_running_pipeline(data) {
    var mrId = data.modelId.toString() + '_' + data.runNo.toString();
    close_viz('debugger_running_'  + mrId);
    close_viz('debugger_paused_'  + mrId);
    close_viz('debugger_stopped_'  + mrId);
    open_viz("debugger_ended_" + mrId);
    select_debugger_model(mrId);
};

function select_debugger_model(mrId) {
    debugger_models = document.getElementById('debugger_models').children;
    for (i = 0; i < debugger_models.length; i++) {
        close_viz(debugger_models[i].id);
    }
    tabs = document.getElementById('debugger_scrollmenu').children;
    for (i = 0; i < tabs.length; i++) {
        deselect_debugging_tab(tabs[i].id);
    }

    toggle_viz("debugger_model_" + mrId);
    select_debugging_tab("debugger_tab_" + mrId);
};

function remove_debugger_model(mrId, modelId, runNo) {
    console.log("Removing model from rebugger");
    var tab = document.getElementById("debugger_tab_" + mrId);
    tab.parentNode.removeChild(tab);
    var model = document.getElementById("debugger_model_" + mrId);
    model.parentNode.removeChild(model);
    for (var i = running_models.length - 1; i >= 0; i--) {
        var model = running_models[i];
        if (model.modelId == modelId && model.runNo == runNo) {
            running_models.splice(i,1);
        }
    }
    $.ajax({
        url: '/remove_tmp_run_dir',
        type: 'post',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({'mrId': mrId}),
        success: function (data) {
            console.log("success!");
        }
    });
    if (running_models.length > 0) {
        var mrId = running_models[running_models.length-1].modelId + '_' + running_models[running_models.length-1].runNo;
        select_debugger_model(mrId);
    } else {
        close_debugger();
    }
};

function update_running_pipeline(split_data) {
    console.log("Updating model data");
    console.log(split_data);
    const mrId = split_data.modelId.toString() + '_' + split_data.runNo.toString();
    var breakpoints = split_data.breakpoints;
    const breakpoint_entries = Object.entries(breakpoints);
    var _continue = true;
    var bp_text = ""
    for (const [bp, val] of breakpoint_entries) {
        bp_text += bp + ": " + val + "\n";
        if (val == false) {
            _continue = false;
            pause_pipeline(mrId);
        }
    }
    for (var i = running_models.length - 1; i >= 0; i--) {
        var model = running_models[i];
        if (model.modelId == split_data.modelId && model.runNo == split_data.runNo) {
            var modules = model.modules;
            for (var i = modules.length - 1; i >= 0; i--) {
                var _module = modules[i];
                if (_module.name == split_data.module_name) {
                    _module.split_outputs.push(split_data.viz);
                }
            }
        }
    }
    split_div = document.getElementById(split_data.modelId + "_" + split_data.runNo + "_" + split_data.module_name + "_" + split_data.split);
    if (_continue) {
        split_div.className += " w3-green w3-hover-gray";
    } else {
        split_div.className += " w3-red w3-hover-gray";
    }
    split_div.title = bp_text;
    select_debugger_model(mrId);
};

function add_model_to_debugger(modelJsonString) {
    if (running_models.length == 0) {
        open_debugger();
    }
    var model = JSON.parse(modelJsonString); // model = {'modelID','runNo','modules':[{'name','splits','split_ouputs'}]}
    var mrId = model.modelId.toString() + '_' + model.runNo.toString();
    var html = new EJS({url : '/debugger_tab.ejs'}).render({'mrId': mrId, 'modelId': model.modelId, 'runNo': model.runNo});
    $('#debugger_scrollmenu').prepend($(html));
    html = new EJS({url : '/debugger_model.ejs'}).render({'mrId': mrId, 'model': model});
    $('#debugger_models').prepend($(html));
    running_models.push(model);
    select_debugger_model(mrId);
};

function add_tracking_ids(data) {
    var tracking_ids = data.tracking_ids; // tracking_ids = {'module': [{'start_id','num_segments','data_file_path'}]}
    var mrId = data.mrId;
    for (const _module of Object.keys(tracking_ids)) {
        var id_ranges = tracking_ids[_module];
        if (id_ranges.length > 0) {
            open_viz("tic_"+mrId+"_"+_module)
            $("#ti_"+mrId+"_"+_module).html("");
            for (var i = 0; i < id_ranges.length; i++) {
                var metadata = id_ranges[i];
                var html = new EJS({url : '/tracked_id_range.ejs'}).render({'data': metadata});
                $("#ti_"+mrId+"_"+_module).append($(html));
            }
        }
    }
};

function visualizeDebuggingOutput(modelId, runNo, module_name, splitNo) {

    for (var i = running_models.length - 1; i >= 0; i--) {
        var model = running_models[i];
        if (model.modelId == modelId && model.runNo == runNo) {
            var modules = model.modules;
            for (var i = modules.length - 1; i >= 0; i--) {
                var _module = modules[i];
                if (_module.name == module_name) {
                    if (_module.split_outputs.length > splitNo) {
                        const vizObjList = _module.split_outputs[splitNo]
                        visualizeObjList(vizObjList);
                    }
                }
            }
        }
    }
};