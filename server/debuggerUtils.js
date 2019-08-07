function pause_pipeline(mrId) {
    document.getElementById("debugger_running_" + mrId).style.display = "none";
    document.getElementById("debugger_paused_" + mrId).style.display = "inline-block";
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
    document.getElementById("debugger_running_" + mrId).style.display = "inline-block";
    document.getElementById("debugger_paused_" + mrId).style.display = "none";
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
    document.getElementById("debugger_running_" + mrId).style.display = "none";
    document.getElementById("debugger_paused_" + mrId).style.display = "none";
    document.getElementById("debugger_stopped_" + mrId).style.display = "inline-block";
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

function select_debugger_model(mrId) {
    models = document.getElementsByClassName("debugger_model");
    for (i = 0; i < models.length; i++) {
        models[i].style.display = "none";
    }
    tabs = document.getElementsByClassName("debugger_tab");
    for (i = 0; i < tabs.length; i++) {
        tabs[i].className = tabs[i].className.replace(" active", "");
    }

    document.getElementById("debugger_model_" + mrId).style.display = "block";
    document.getElementById("debugger_tab_" + mrId).className += " active";
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
        var mrId = running_models[0].modelId + '_' + running_models[0].runNo;
        select_debugger_model(mrId);
    } else {
        close_debugger();
    }
};

function update_running_pipeline(split_data) {
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
                    _module.split_outputs.push(split_data.viz_file);
                }
            }
        }
    }
    if (_continue) {
        document.getElementById("pbh_" + split_data.modelId + "_" + split_data.runNo + "_" + split_data.module_name + "_" + split_data.split).className += " done";
        document.getElementById("pbv_" + split_data.modelId + "_" + split_data.runNo + "_" + split_data.module_name + "_" + split_data.split).className += " done";
    } else {
        document.getElementById("pbh_" + split_data.modelId + "_" + split_data.runNo + "_" + split_data.module_name + "_" + split_data.split).className += " done incorrect";
        document.getElementById("pbv_" + split_data.modelId + "_" + split_data.runNo + "_" + split_data.module_name + "_" + split_data.split).className += " done incorrect";
    }
    document.getElementById("pbh_" + split_data.modelId + "_" + split_data.runNo + "_" + split_data.module_name + "_" + split_data.split).title = bp_text;
    document.getElementById("pbv_" + split_data.modelId + "_" + split_data.runNo + "_" + split_data.module_name + "_" + split_data.split).title = bp_text;
    select_debugger_model(mrId);
};

function finish_running_pipeline(data) {
    var mrId = data.modelId.toString() + '_' + data.runNo.toString();
    document.getElementById("debugger_running_" + mrId).style.display = "none";
    document.getElementById("debugger_ended_" + mrId).style.display = "inline-block";
    select_debugger_model(mrId);
};

function add_model_to_debugger(modelJsonString) {
    var model = JSON.parse(modelJsonString); // model = {'modelID','runNo','modules':[{'name','splits','split_ouputs'}]}
    var mrId = model.modelId.toString() + '_' + model.runNo.toString();
    var html = new EJS({url : '/debugger_tab.ejs'}).render({'mrId': mrId, 'modelId': model.modelId, 'runNo': model.runNo});
    $('.debugger_scrollmenu').append($(html));
    html = new EJS({url : '/debugger_model.ejs'}).render({'mrId': mrId, 'model': model});
    $('.debugger_models').append($(html));
    running_models.push(model);
    select_debugger_model(mrId);
};

function add_tracking_ids(data) {
    var tracking_ids = data.tracking_ids; // tracking_ids = {'module': [{'start_id','num_segments','data_file_path'}]}
    var mrId = data.mrId;
    for (const _module of Object.keys(tracking_ids)) {
        console.log("OK")
        var id_ranges = tracking_ids[_module];
        $("#ti_"+mrId+"_"+_module).html("");
        console.log(id_ranges);
        console.log($("#ti_"+mrId+"_"+_module));
        for (var i = 0; i < id_ranges.length; i++) {
            var metadata = id_ranges[i];
            var html = new EJS({url : '/tracked_id_range.ejs'}).render({'data': metadata});
            $("#ti_"+mrId+"_"+_module).append($(html));
        }
    }
}

function visualizeDebuggingOutput(modelId, runNo, module_name, splitNo) {

    var iframe = document.getElementById('iframeViz');
    for (var i = running_models.length - 1; i >= 0; i--) {
        var model = running_models[i];
        if (model.modelId == modelId && model.runNo == runNo) {
            var modules = model.modules;
            for (var i = modules.length - 1; i >= 0; i--) {
                var _module = modules[i];
                if (_module.name == module_name) {
                    if (_module.split_outputs.length > splitNo) {
                        const viz_file = _module.split_outputs[splitNo]
                        if (viz_file != undefined) {
                            $.get('/setViz',{"pathJSON": "./Data/" + viz_file})
                                .done(function (response) {
                                    iframe.setAttribute("src", "vizFrame");
                                    iframe.src = iframe.src;
                                });
                        }
                    }
                }
            }
        }
    }
};