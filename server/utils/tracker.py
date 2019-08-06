import json
from operator import itemgetter
from abc import ABC, abstractmethod
from splitter import Splitter
from tracking_filter import tracking_filters
from record import Segment, SegmentRange
from mod_util import save_as_tensor

class Tracker(object):

    """docstring for Tracker"""

    def __init__(self, modelId, runNo, filter_dics, filename, _type, splitter_type):
        super(Tracker, self).__init__()
        self.modelId = modelId
        self.runNo = runNo
        self.run_dir = str(modelId) + '_' + str(runNo)
        self.filename = filename
        self.filters = self.prepare_filters(filter_dics)
        self.type = _type # lazy or eager
        self.splitter = Splitter(splitter_type)
        self.track_data = {}

    def prepare_filters(self, filter_dics):
        filters = []
        for filter_dic in filter_dics:
            if filter_dic['type'] in tracking_filters:
                filters.append(tracking_filters[filter_dic['type']](*filter_dic['params']))
        return filters

    def handle_record(self, record, created_by):
        if created_by not in self.track_data:
            self.track_data[created_by] = []
        self.track_data[created_by].append((record.getId(), record))

    def test_condition(self, record):
        for _filter in self.filters:
            if _filter.evaluate(record):
                return True
        return False

    def track_file(self, file, created_by):
        if file[-4:] == '.mat':
            segments = self.splitter.split_file(file)
            for segment in segments:
                if self.test_condition(segment):
                    self.handle_record(segment, created_by)
            if self.type == 'eager':
                return self.save_tracked_records()
        return False

    def save_tracked_records(self):
        track_data_dic = self.group_track_data()
        out_data = self.save_data_in_files(track_data_dic)
        with open('./Data/' + self.run_dir + '/' + self.filename, 'w') as outfile:
            json.dump(out_data, outfile, ensure_ascii=False, indent=4)
        return True

    def group_track_data(self):
        track_data_dic = {}
        for module, record_list in self.track_data.items():
            record_list.sort(key=itemgetter(0))
            new_record_list = []
            prev_record = None
            for [record_id, record] in record_list:
                if prev_record == None:
                    prev_record = SegmentRange(record)
                else:
                    try:
                        prev_record.add_segment(record)
                    except ValueError:
                        new_record_list.append([prev_record.getId(), prev_record])
                        prev_record = SegmentRange(record)
            if prev_record != None:
                new_record_list.append([prev_record.getId(), prev_record])
            track_data_dic[module] = new_record_list
        return track_data_dic

    def save_data_in_files(self, track_data_dic):        
        out_data = {}
        for module, record_list in track_data_dic.items():
            new_record_list = []
            for [record_id, record] in record_list:
                metadata = record.getMetaData()
                out_filepath = './Data/' + self.run_dir + '/' + module + '_record_' + str(record_id) + '.json'
                metadata['data_file_path'] = out_filepath
                save_as_tensor(record.getData(), out_filepath)
                new_record_list.append(metadata)
            out_data[module] = new_record_list
        return out_data