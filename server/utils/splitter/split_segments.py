import hdf5storage
from record import Segment

def split_segments(filename):
    points = 400
    f = hdf5storage.loadmat('./Data/' + filename)
    data = f['data']
    (_,l) = data.shape
    count = 0
    segments = []
    for i in range(0,l,points):
        segments.append(Segment(count, data[:,i:i + points].tolist()))
        count += 1
    return segments

dic = {'segments': split_segments}