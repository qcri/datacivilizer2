import sys
import pickle
import numpy as np
import glob
import operator
from tqdm import tqdm
from utils.from_filepath_to_index import from_filepath_to_index
from utils.weight_cal import compute_class_weight


def drop_init(in_file, out_file):
    all_dataset = glob.glob("./Data/second_dataset_from_cpd_eeg_10s_split/*/*/*/*.pkl")
    count_zero = 0
    all_zero_file_path = []
    not_zero_file_path = []
    # for file_path in tqdm(all_dataset):
    #     eeg = pickle.load(open(file_path, 'rb'), encoding='latin1').astype(np.float)
    #     regular_sum = np.sum(eeg, axis=0)
    #
    #     if np.sum(regular_sum) == 0:
    #         count_zero += 1
    #         all_zero_file_path.append(file_path)
    #     else:
    #         not_zero_file_path.append(file_path)
    #     # print(count_zero)
    # print("Not zero: ", len(not_zero_file_path))
    # print("All zero: ", len(all_zero_file_path))
    # with open('/home/dell/eeg-data-sample/all_zero_file_path.npy', 'wb') as f:
    #     pickle.dump(all_zero_file_path, f, pickle.HIGHEST_PROTOCOL)
    # with open('/home/dell/eeg-data-sample/not_zero_file_path.npy', 'wb') as f:
    #     pickle.dump(not_zero_file_path, f, pickle.HIGHEST_PROTOCOL)
    SECOND_DATA_KEYS = set(np.load("./Data/not_zero_file_path.npy", allow_pickle=True))
    drop_in_dataset_index(in_file, out_file, SECOND_DATA_KEYS)


# 直接对dataset_index进行删除操作，这样不行
# 建立新表，只有非全零的，而且在sample中出现的才能进入
def drop_in_dataset_index(in_file, out_file, file_path):

    with open('./Data/' + in_file, "rb") as f:
        data_splits_sample = pickle.load(f)

    new_dataset_index = dict()
    for not_zero_file_path in tqdm(file_path):
        p, home, dell, a, b, subject_key, date_str, time_str, segment = not_zero_file_path.split('/')
        segment_index = segment.split('.')[0]
        m = subject_key + "_" + date_str + "_" + time_str

        # 把path处理成tmp index用于添加
        tmp = from_filepath_to_index(not_zero_file_path)
        # print(not_zero_file_path)
        # print(data_splits_sample['train'][0])
        # print(tmp)
        jump = 0
        for i in range(len(data_splits_sample['train'])):
            if m == data_splits_sample['train'][i][0] and int(segment_index) == int(data_splits_sample['train'][i][1]):
                jump = 1
                if 'train' in new_dataset_index:
                    new_dataset_index['train'].extend(tmp)
                else:
                    new_dataset_index['train'] = tmp
                # print("In train")
                break
        if jump == 1:
            continue
        jump_1 = 0
        for i in range(len(data_splits_sample['validation'])):
            if m == data_splits_sample['validation'][i][0] and int(segment_index) == int(data_splits_sample['validation'][i][1]):
                jump_1 = 1
                if 'validation' in new_dataset_index:
                    new_dataset_index['validation'].extend(tmp)
                else:
                    new_dataset_index['validation'] = tmp
                # print("In validation")
                break
        if jump_1 == 1:
            continue
        for i in range(len(data_splits_sample['test'])):
            if m == data_splits_sample['test'][i][0] and int(segment_index) == int(data_splits_sample['test'][i][1]):
                if 'test' in new_dataset_index:
                    new_dataset_index['test'].extend(tmp)
                else:
                    new_dataset_index['test'] = tmp

    print("train", len(new_dataset_index['train']))
    print("test", len(new_dataset_index['test']))
    print("validation", len(new_dataset_index['validation']))

    pickle.dump(new_dataset_index, open('./Data/' + out_file, "wb"),
                pickle.HIGHEST_PROTOCOL)
    print("Dataset index saved!")

    # class_weights, pseudo_counts = compute_class_weight(new_dataset_index['train'], alpha=0.2)
    # print("Class weights")
    # print(class_weights)
    # pickle.dump(class_weights, open("/home/dell/eeg-data-sample/class_weights_sample_without_zero.pkl", "wb"), pickle.HIGHEST_PROTOCOL)


def equal_tuple(a, b):
    if a[0] == b[0] and a[1] == b[1] and a[2] == b[2]:
        return True
    else:
        return False

def execute_service(in_path, out_path):
    return
    drop_init(in_path, out_path)

execute_service(sys.argv[1], sys.argv[2])