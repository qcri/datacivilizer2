import hdf5storage
from record import Segment

class Splitter(object):

    """docstring for Splitter"""
    points = 400

    def __init__(self, _type):
        super(Splitter, self).__init__()
        self.type = _type
        self.typeDic = {'segments': self.split_segments}
        self.split_file = self.typeDic.get(_type, NotImplemented)

    def split_segments(self, filename):
        f = hdf5storage.loadmat('./Data/' + filename)
        data = f['data']
        (_,l) = data.shape
        count = 0
        segments = []
        for i in range(0,l,type(self).points):
            segments.append(Segment(count, data[:,i:i + type(self).points].tolist()))
            count += 1
        return segments
