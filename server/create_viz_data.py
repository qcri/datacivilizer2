import pickle
import numpy as np
from utils.mod_util import save_as_tensor

def main():
    with open('./Data/second_dataset_from_cpd_eeg_10s_split/sid456/20170213/082536/1098.pkl', 'rb') as f:
        eeg_data_array = pickle.load(f)
    montage = eeg_data_array.astype(dtype=np.float32).transpose()
    print(montage.shape)
    save_as_tensor(montage, "./Data/0.json")

if __name__ == "__main__":
    main()