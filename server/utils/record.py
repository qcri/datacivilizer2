from abc import ABC, abstractmethod

class AbstractRecord(ABC):

    @abstractmethod
    def __init__(self, _id, data):
        self.id = _id
        self.data = data

    def getId(self):
        return self.id

    def getData(self):
        return self.data

    def getMetaData(self):
        return {}

class Segment(AbstractRecord):

    def __init__(self, _id, data):
        super(Segment, self).__init__(_id, data)

class SegmentRange(AbstractRecord):

    def __init__(self, segment):
        super(SegmentRange, self).__init__(segment.getId(), segment.getData())
        self.num_segments = 1

    def add_segment(self, segment):
        if segment.getId() == self.id + self.num_segments:
            self.data = [x + y for x, y in zip(self.data, segment.getData())]
            self.num_segments += 1
        elif segment.getId() == self.id - 1:
            self.data = [x + y for x, y in zip(segment.getData(), self.data)]
            self.id = segment.getId()
            self.num_segments += 1
        else:
            raise ValueError("The given segment is not adjacent to the current range")

    def getMetaData(self):
        return {
            'start_id': self.id,
            'num_segments': self.num_segments
        }