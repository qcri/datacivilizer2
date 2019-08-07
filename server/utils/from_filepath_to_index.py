import pickle
import numpy as np


def from_filepath_to_index(zero_file_path):
    p, home, dell, a, b, subject_key, date_str, time_str, segment = zero_file_path.split('/')
    segment_index = segment.split('.')[0]
    m = subject_key + "_" + date_str + "_" + time_str
    c = "second_dataset_from_cpd_label"
    d = "label_" + m + ".pkl"
    a = "sssd"
    label_file_path = ("./Data/{}/{}".format(c, d))
    vote_arr = pickle.load(open(label_file_path, 'rb'), encoding='latin1')
    target = np.squeeze(vote_arr, axis=1).astype(np.int)
    tmp = [(m, int(segment_index), target[int(segment_index)])]
    return tmp
