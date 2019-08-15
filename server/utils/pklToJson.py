import sys
import pickle
import numpy as np
from mod_util import save_as_tensor

def pkl_to_json(pkl_file, json_file):
    with open(pkl_file, 'rb') as f:
        eeg_data_array = pickle.load(f)
    montage = eeg_data_array.astype(dtype=np.float32).transpose()
    save_as_tensor(montage, json_file)

pkl_to_json(sys.argv[1], sys.argv[2])