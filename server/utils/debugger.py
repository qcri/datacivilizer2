import sys
import os
import fnmatch
import time
import json
import hdf5storage
import requests
import subprocess
from operator import itemgetter
from shutil import copyfile
from tracker import Tracker

class Debugger(object):

    """docstring for Debugger"""

    def __init__(self, dirName, run_info_filename, tracking_info_filename):
        self.dirName = dirName
        self.run_info_filename = run_info_filename
        self.tracking_info_filename = tracking_info_filename
        self.metrics = {}
        self.stopped = False
        self.paused = False
        self.quickPause = 0
        self.get_run_info()
        self.get_tracker_info()
        self.prepare_modules()

    def get_run_info(self):
        with open('./Data/' + self.dirName + '/' + self.run_info_filename) as run_info_file:
            run_info = json.load(run_info_file)
            self.modelId = run_info['modelId']
            self.runNo = run_info['runNo']
            self.type = run_info['debugger_type']
            self.metric_file = run_info['metric_file']
            self.max_processes = run_info['max_processes']
            self.num_modules = run_info['num_modules']
            self.pipeline = run_info['pipeline']

    def get_tracker_info(self):
        with open('./Data/' + self.dirName + '/' + self.tracking_info_filename) as tracking_info_file:
            tracking_info = json.load(tracking_info_file)
            self.tracking_file = tracking_info['filename']
            self.tracker = Tracker(self.modelId, self.runNo, tracking_info['filters'], self.tracking_file, tracking_info['type'], tracking_info['splitter_type'])

    def prepare_modules(self):
        for i in range(self.num_modules):
            module_dic = self.pipeline[i]
            module_args = ['python', module_dic['cmd_path']]
            module_args.extend(module_dic['inputs'])
            module_args.extend(module_dic['outputs'])
            module_args.extend(map(str,module_dic['params']))
            self.pipeline[i]['args'] = module_args

    def update_status(self):
        get_params = {'modelId': self.modelId, 'runNo': self.runNo}
        response = requests.get(url="http://localhost:8080/get_status", params=get_params)
        if response.text == 'running':
            if self.quickPause == 0:
                self.paused = False
                print(response.text)
            else:
                print("quickPaused")
                self.quickPause -= 1
        elif response.text == 'paused':
            print(response.text)
            self.paused = True
            self.quickPause = 0
        elif response.text == 'stopped':
            print(response.text)
            self.stopped = True

    def run(self):
        run_list = self.create_run_list()
        process_queue = []
        done_list = []
        while (len(run_list) > 0 or len(process_queue) > 0) and not self.stopped:
            # try to add a new process
            if len(run_list) > 0 and len(process_queue) < self.max_processes and not self.paused:
                for i in range(len(run_list)):
                    ready = True
                    (_, _, _, in_files, _, _, _) = run_list[i]
                    for file in in_files:
                        if not self.rdy_tmp_file(file, done_list.copy()):
                            ready = False
                            break
                    if ready:
                        break
                if ready:
                    (_, module_name, split, _, out_files, tmp_file_name, args) = run_list.pop(i)
                    print("Starting new process")
                    print(args)
                    p = subprocess.Popen(args)
                    process_queue.append((module_name, split, out_files, tmp_file_name, p))
            # wait for the next running process to finish with 5 second timeout, handle finished process if present
            if len(process_queue) > 0: # and not self.paused ?
                (_, _, _, _, p) = process_queue[0]
                try:
                    p.wait(5)
                    (module_name, split, out_files, tmp_file_name, _) = process_queue.pop(0)
                    self.handle_split(module_name, split, out_files, tmp_file_name)
                    done_list.append(out_files)
                except subprocess.TimeoutExpired as e:
                    pass
            else:
                time.sleep(5)
            self.update_status()

        if self.stopped:
            for (_, _, _, _, p) in process_queue:
                p.kill()
        else:
            self.finish_run()

    # create a list containg the module names, split values, names of output files and arguments of the processes to run, in the correct order.
    def create_run_list(self):
        run_list = []
        tmp_counter = 0
        for k in range(len(self.pipeline)):
            module_dic = self.pipeline[k]
            num_in_files = module_dic['num_inputs']
            num_out_files = module_dic['num_outputs']
            splits = module_dic['splits']
            n = len(splits)
            for i in range(n):
                args = module_dic['args'].copy()
                suffix = '_' + str(splits[i]).zfill(3)
                new_in_files = []
                new_out_files = []
                for j in range(num_in_files):
                    name, _, extension = module_dic['inputs'][j].partition('.')
                    in_filename = self.dirName + '/' + name + suffix + '.' + extension
                    new_in_files.append(in_filename)
                    args[2+j] = in_filename
                for j in range(num_out_files):
                    name, _, extension = module_dic['outputs'][j].partition('.')
                    out_filename = self.dirName + '/' + name + suffix + '.' + extension
                    new_out_files.append(out_filename)
                    args[2+num_in_files+j] = out_filename
                tmp_file_name = './Data/' + self.dirName + '/' + 'tmp_' + str(tmp_counter) + '.json'
                tmp_counter += 1
                args.append(tmp_file_name)
                run_list.append((k, module_dic['cmd_name'], splits[i], new_in_files, new_out_files, tmp_file_name, args))
        if self.type == 'dirty':
            run_list.sort(key=itemgetter(2,0))
        return run_list

    def rdy_tmp_file(self, filepath, done_list):
        print("Testing file availability ", filepath)
        (mrId, name, split, extension) = self.get_file_info(filepath)
        if name[:3] != "out":
            if not os.path.exists('./Data/' + mrId + '/' + name + '_100.' + extension):
                copyfile('./Data/' + name + '.' + extension, './Data/' + mrId + '/' + name + '_100.' + extension)
            done_list.append([mrId + '/' + name + '_100.' + extension])
        for out_files in done_list:
            for filepath in out_files:
                (_, done_name, done_split, _) = self.get_file_info(filepath)
                if done_name == name:
                    if self.type == 'clean':
                        if int(done_split) == 100:
                            self.split_file(mrId, name, int(done_split), int(split))
                            return True
                    elif self.type == 'dirty':
                        if int(done_split) >= int(split):
                            self.split_file(mrId, name, int(done_split), int(split))
                            return True
        return False

    def get_file_info(self, filepath):
        mrId, _, file = filepath.partition('/')
        filename, _, extension = file.partition('.')
        name, _, split = filename.rpartition('_')
        return (mrId, name, split, extension)

    def split_file(self, mrId, name, in_split, out_split):
        if out_split == in_split:
            print("File exists")
            return
        # while True:
        #     try:
        f = hdf5storage.loadmat('./Data/' + mrId + '/' + name + '_' + str(in_split).zfill(3) + '.mat')
            #     break
            # except:
            #     print("Loading failed, trying again")
            #     time.sleep(2)
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
        # while True:
        #     try:
        hdf5storage.savemat('./Data/' + mrId + '/' + name + '_' + str(out_split).zfill(3) + '.mat', tmp_f)
            #     break
            # except:
            #     print("Saving failed, trying again")
            #     raise 
            #     # print("---------------------------")
            #     # print("---------------------------")
            #     # print("---------------------------")
            #     # print("---------------------------")
            #     # print("---------------------------")
            #     # print("---------------------------")
            #     time.sleep(2)
        print("File created")

    def handle_split(self, module_name, split, out_files, tmp_file_name):
        if split == 100:
            for file in out_files:
                tracked = self.tracker.track_file(file, module_name)
                if tracked:
                    post_data = {
                        'modelId': self.modelId,
                        'runNo': self.runNo,
                        'tracking_file_name': './Data/' + self.dirName + '/' + self.tracking_file
                        }
                    requests.post(url="http://localhost:8080/update_tracking_file", json=post_data)
        if os.path.exists(tmp_file_name):
            with open(tmp_file_name) as tmp_file:
                data = json.load(tmp_file)
                breakpoints = data['breakpoints']
                for val in breakpoints.values():
                    if val == False:
                        self.paused = True
                        self.quickPause = 2
                if split == 100:
                    metrics = data['metrics']
                    if (metrics != {}):
                        self.metrics[module_name] = {}
                        for metric in metrics.keys():
                            self.metrics[module_name][metric] = metrics[metric]
            os.remove(tmp_file_name)
        else:
            breakpoints = {}
        self.send_split(module_name, split, out_files, breakpoints)

    def send_split(self, module_name, split, out_files, breakpoints):
        post_data = {
            'modelId': self.modelId,
            'runNo': self.runNo,
            'module_name': module_name,
            'split': split,
            'out_files': out_files,
            'breakpoints': breakpoints
        }
        requests.post(url="http://localhost:8080/split", json=post_data)

    def finish_run(self):
        self.tracker.save_tracked_records()
        with open('./Data/' + self.dirName + '/' + self.metric_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, ensure_ascii=False, indent=4)
        post_data = {
            'modelId': self.modelId,
            'runNo': self.runNo,
            'metric_file_name': './Data/' + self.dirName + '/' + self.metric_file,
            'tracking_file_name': './Data/' + self.dirName + '/' + self.tracking_file
            }
        requests.post(url="http://localhost:8080/finish_run", json=post_data)

def main(args):
    dirName = args.pop(0)
    run_info_filename = args.pop(0)
    tracking_info_filename = args.pop(0)
    debugger = Debugger(dirName, run_info_filename, tracking_info_filename)
    debugger.run()

if __name__ == '__main__':
    main(sys.argv[1:])
