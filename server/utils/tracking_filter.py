import json
from abc import ABC, abstractmethod

class TrackingFilter(ABC):

    @abstractmethod
    def evaluate(self, record):
        pass

class IdTrackingFilter(TrackingFilter):

    def __init__(self, _id):
        self.id = _id

    def evaluate(self, record):
        return record.getId() == self.id

class IdRangeTrackingFilter(TrackingFilter):

    def __init__(self, id_start, id_end):
        self.id_start = id_start
        self.id_end = id_end

    def evaluate(self, record):
        return record.getId() >= self.id_start and record.getId() < self.id_end

def get_tracking_filters():
    filters = {}
    with open('./utils/tracking_filters.json') as file:
        dic = json.load(file)
        for key, _filter in dic.items():
            filters[key] = globals()[_filter['classname']]
    return filters


tracking_filters = get_tracking_filters()