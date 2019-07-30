import sys
import os
import fnmatch
import time
import json
import h5py
import hdf5storage
import requests
import subprocess
from operator import itemgetter
from shutil import copyfile

class Debugger(object):

    """docstring for Debugger"""

    def __init__(self, modelId, runNo, _type="dirty", metric_file="metric_temp.json", max_processes=2):
        super(Debugger, self).__init__()
        self.modelId = modelId
        self.runNo = runNo
        self.max_processes = max_processes
        self.dirName = str(modelId) + '_' + str(runNo)
        self.metric_file = './Data/' + self.dirName + '/' + metric_file
        self.metrics = {}
        self.type = _type # clean or dirty (breadth-first or depth-first)
        self.modules = []
        self.stopped = False
        self.paused = False
        self.create_run_directory()

    def update_status(self):
        get_params = {'modelId': self.modelId, 'runNo': self.runNo}
        response = requests.get(url="http://localhost:8080/get_status", params=get_params)
        print(response.text)
        if response.text == 'running':
            self.paused = False
        elif response.text == 'paused':
            self.paused = True
        elif response.text == 'stopped':
            self.stopped = True

    def send_split(self, module_name, split, out_files):
        post_data = {
            'modelId': self.modelId,
            'runNo': self.runNo,
            'module_name': module_name,
            'split': split,
            'out_files': out_files
        }
        # for j in range(len(out_files)):
        #     json_filename = out_files[j][i][:-4] + ".json"
        #     post_data['out_files'].append(json_filename)
        requests.post(url="http://localhost:8080/split", json=post_data)

    def create_run_directory(self):
        if not os.path.exists('./Data/' + self.dirName):
            os.mkdir('./Data/' + self.dirName)
            print("Directory " , './Data/' +self.dirName ,  " created")
        else:    
            print("Directory " , './Data/' + self.dirName ,  " already exists")

    def split_file(self, mrId, in_name, in_split, out_name, out_split):
        if out_split > in_split:
            raise ValueError("Out split must be smaller or equal to in split")
        extension = '.mat'
        if out_split == in_split:
            copyfile('./Data/' + in_name + '_' + str(in_split) + extension, './Data/' + mrId + '/' + out_name + '_' + str(out_split) + extension)
            return
        while True:
            try:
                f = hdf5storage.loadmat('./Data/' + mrId + '/' + in_name + '_' + str(in_split).zfill(3) + extension)
                break
            except:
                print("Loading failed, trying again")
                time.sleep(2)
        tmp_f = {}
        for key in f.keys():
            if key == 'data':
                data = f['data']
                (_,l) = data.shape
                new_l = int(l*out_split / in_split)
                new_data = data[:,:new_l]
                tmp_f[key] = new_data
            else:
                tmp_f[key] = f[key]
        while True:
            try:
                hdf5storage.savemat('./Data/' + mrId + '/' + out_name + '_' + str(out_split).zfill(3) + extension, tmp_f, truncate_existing=True)
                break
            except:
                print("Saving failed, trying again")
                raise
                time.sleep(2)

    def rdy_tmp_file(self, filepath):
        print("Testing file availability ", filepath)
        if os.path.exists('./Data/' + filepath):
            print("File exists")
            return True
        else:
            mrId, _, file = filepath.partition('/')
            filename, _, extension = file.partition('.')
            name, _, split = filename.rpartition('_')
            if "SampleData" in name:
                if not os.path.exists('./Data/' + mrId + '/' + name + '_100.' + extension):
                    copyfile('./Data/' + name + '.' + extension, './Data/' + mrId + '/' + name + '_100.' + extension)
                if int(split) == 100:
                    print("File created")
                    return True
            if int(split) == 100:
                print("File unavailable")
                return False
            else:
                if self.type == 'clean':
                    if int(split) != 100 and os.path.exists('./Data/' + mrId + '/' + name + '_100.' + extension):
                        self.split_file(mrId, name, 100, name, int(split))
                        print("File created")
                        return True
                elif self.type == 'dirty':
                    if int(split) != 100:
                        files = fnmatch.filter(os.listdir('./Data/' + mrId), name + '_*.' + extension)
                        files.sort()
                        for file in files:
                            other_filename, _, extension = file.partition('.')
                            name, _, other_split = other_filename.rpartition('_')
                            if int(other_split) >= int(split):
                                self.split_file(mrId, name, int(other_split), name, int(split))
                                print("File created")
                                return True
                print("File unavailable")
                return False

    def append_module(self, module_name, debug_info, module_args, in_files, out_files):
        module_args.insert(0,'python')
        module_args.append(self.metric_file)
        debug_info.append(100)
        self.modules.append((module_name, module_args, debug_info, in_files, out_files))

    # create a list containg the module names, split values, names of output files and arguments of the processes to run, in the correct order.
    def create_run_list(self):
        run_list = []
        for k in range(len(self.modules)):
            (module_name, module_args, splits, in_files, out_files) = self.modules[k]
            num_in_files = len(in_files)
            num_out_files = len(out_files)
            n = len(splits)
            for i in range(n):
                args = module_args[:]
                suffix = '_' + str(splits[i]).zfill(3)
                new_in_files = []
                new_out_files = []
                for j in range(num_in_files):
                    name, _, extension = in_files[j].partition('.')
                    in_filename = self.dirName + '/' + name + suffix + '.' + extension
                    new_in_files.append(in_filename)
                    args[2+j] = in_filename
                for j in range(num_out_files):
                    name, _, extension = out_files[j].partition('.')
                    out_filename = self.dirName + '/' + name + suffix
                    new_out_files.append(out_filename + '.json')
                    args[2+num_in_files+j] = out_filename + '.' + extension
                run_list.append((k, module_name, splits[i], new_in_files, new_out_files, args))
        if self.type == 'dirty':
            run_list.sort(key=itemgetter(2,0))

        for i in range(len(run_list)):
            print(run_list[i])
        return run_list

    def run(self):
        run_list = self.create_run_list()
        process_queue = []
        while (len(run_list) > 0 or len(process_queue) > 0) and not self.stopped:
            # try to add a new process
            if len(run_list) > 0 and len(process_queue) < self.max_processes and not self.paused:
                for i in range(len(run_list)):
                    ready = True
                    (_, _, _, in_files, _, _) = run_list[i]
                    for file in in_files:
                        if not self.rdy_tmp_file(file):
                            ready = False
                            break
                    if ready:
                        break
                if ready:
                    (_, module_name, split, _, out_files, args) = run_list.pop(i)
                    print("Starting new process")
                    print(args)
                    p = subprocess.Popen(args)
                    process_queue.append((module_name, split, out_files, p))
            # wait for the next running process to finish with 5 second timeout, handle finished process if present
            if len(process_queue) > 0: # and not self.paused ?
                (_, _, _, p) = process_queue[0]
                try:
                    p.wait(5)
                    (module_name, split, out_files, _) = process_queue.pop(0)
                    self.send_split(module_name,split,out_files)
                    if split == 100:
                        self.add_metrics(module_name)
                except subprocess.TimeoutExpired as e:
                    pass
            else:
                time.sleep(5)
            self.update_status()

        if self.stopped:
            for (_, _, _, p) in process_queue:
                p.kill()
        else:
            self.finish_run()

    def add_metrics(self, module_name):
        if os.path.exists(self.metric_file):
            self.metrics[module_name] = {}
            with open(self.metric_file) as metric_file:
                data = json.load(metric_file)
                for metric in data.keys():
                    self.metrics[module_name][metric] = data[metric]
            os.remove(self.metric_file)

    def finish_run(self):
        with open(self.metric_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, ensure_ascii=False, indent=4)
        post_data = {
            'modelId': self.modelId,
            'runNo': self.runNo,
            'metric_file_name': self.metric_file
            }
        requests.post(url="http://localhost:8080/finish_run", json=post_data)

def get_debug_info(args):
    num_splits = int(args.pop(0)) # number of breakpoints (not including the complete run)
    splits = []
    for i in range(num_splits):
        splits.append(int(args.pop(0)))
    return splits

def get_module_info(args):
    module_args = []
    in_files = []
    out_files = []
    module_cmd = args.pop(0)
    module_name = module_cmd[:-3] # remove .py
    module_args.append(module_cmd)
    num_inputs = int(args.pop(0)) # amount of input files
    for i in range(num_inputs):
        filename = args.pop(0)
        module_args.append(filename)
        in_files.append(filename)
    num_outputs = int(args.pop(0)) # amount of output files
    for i in range(num_outputs):
        filename = args.pop(0)
        module_args.append(filename)
        out_files.append(filename)
    num_params = int(args.pop(0)) # amount of parameters
    for i in range(num_params):
        param = args.pop(0)
        module_args.append(param)
    debug_info = get_debug_info(args) # debugging information (ex: breakpoints, filters, ...)
    return module_name, module_args, in_files, out_files, debug_info

def main(args):
    modelId = int(args.pop(0))
    runNo = int(args.pop(0))
    num_modules = int(args.pop(0))
    debugger_type = args.pop(0)
    print(str(num_modules) + " modules to run")
    debugger = Debugger(modelId, runNo, _type=debugger_type)
    for i in range(num_modules):
        module_name, module_args, in_files, out_files, debug_info = get_module_info(args)
        debugger.append_module(module_name, debug_info, module_args, in_files, out_files)
    debugger.run()

if __name__ == '__main__':
    main(sys.argv[1:])
