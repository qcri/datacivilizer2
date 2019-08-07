import sys
import pickle
import numpy as np
from tqdm import tqdm

def down_sample_init(in_file, out_file):
    SECOND_DATA_KEYS = set(np.load("./Data/file_name_exist_in_second.npy", allow_pickle=True))

    # ('sid881_20150208_093524', 1255, array([1, 0, 0, 0, 0, 0]))
    with open('./Data/' + in_file, "rb") as f:
        data_splits = pickle.load(f)
    print(data_splits['train'][0][0])
    print("train", len(data_splits['train']))
    print("test", len(data_splits['test']))
    print("validation", len(data_splits['validation']))
    new_dataset_index = dict()
    prob = 0
    count = 0
    not_other = 0
    for eeg_file_path in tqdm(SECOND_DATA_KEYS):
        # "/home/dell/eeg-data-sample/second_dataset_from_cpd_eeg_10s_split/sid881/20150203/094931/1884.pkl"
        eeg_file_path = eeg_file_path.replace("eeg-data-sample", "ssd")
        # with open(eeg_file_path, 'rb+') as f:
        # print(eeg_file_path)
        p, home, dell, a, b, subject_key, date_str, time_str, segment = eeg_file_path.split('/')
        segment_index = segment.split('.')[0]
        c = "second_dataset_from_cpd_label"
        m = subject_key + "_" + date_str + "_" + time_str
        d = "label_" + m + ".pkl"
        label_file_path = ("./Data/{}/{}".format(c, d))

        # name = input("Please intput your name:")
        # 如果是other，一定概率下进入新表
        if detect_other(label_file_path, int(segment_index)):
            prob = prob + 1  # 用于计算概率
            # print(prob)
            if prob % 2 == 0:  # 要进入新表
                # print("j==inru")
                vote_arr = pickle.load(open(label_file_path, 'rb'), encoding='latin1')
                tmp = [(m, int(segment_index), vote_arr[int(segment_index)])]
                 # print(tmp)
                t_1 = 0
                for i in range(len(data_splits['train'])):
                    if m == data_splits['train'][i][0]:
                        count += 1
                        t_1 = 1
                        # print("In train", data_splits['train'][i])
                        if 'train' in new_dataset_index:
                            new_dataset_index['train'].extend(tmp)
                        else:
                            new_dataset_index['train'] = tmp
                        # print(new_dataset_index)
                        # name = input("Please intput your name:")
                        # print("train", len(new_dataset_index['train']))
                        break
                if t_1 == 1:
                    continue
                for i in range(len(data_splits['test'])):
                    if m == data_splits['test'][i][0]:
                        count += 1
                        # print("In test", data_splits['test'][i][0])
                        if 'test' in new_dataset_index:
                            new_dataset_index['test'].extend(tmp)
                        else:
                            new_dataset_index['test'] = tmp
                        break
                for i in range(len(data_splits['validation'])):
                    if m == data_splits['validation'][i][0]:
                        count += 1
                        # print("In valid", data_splits['valid'][i][0])
                        if 'validation' in new_dataset_index:
                            new_dataset_index['validation'].extend(tmp)
                        else:
                            new_dataset_index['validation'] = tmp
                        break
        else:
            not_other += 1
            if not_other % 1000 == 0:
                pass
                # print(not_other)
            vote_arr = pickle.load(open(label_file_path, 'rb'), encoding='latin1')
            tmp = [(m, int(segment_index), vote_arr[int(segment_index)])]
            # print(vote_arr[int(segment_index)])
            t = 0
            for i in range(len(data_splits['train'])):
                if m == data_splits['train'][i][0]:
                    t = 1
                    if 'train' in new_dataset_index:
                        new_dataset_index['train'].extend(tmp)
                    else:
                        new_dataset_index['train'] = tmp
                    # print("train", len(new_dataset_index['train']))
                    break

            if t == 1:
                continue
            for i in range(len(data_splits['test'])):
                if m == data_splits['test'][i][0]:
                    if 'test' in new_dataset_index:
                        new_dataset_index['test'].extend(tmp)
                    else:
                        new_dataset_index['test'] = tmp
                    break
            for i in range(len(data_splits['validation'])):
                if m == data_splits['validation'][i][0]:
                    if 'validation' in new_dataset_index:
                        new_dataset_index['validation'].extend(tmp)
                    else:
                        new_dataset_index['validation'] = tmp
                    break


    print("Left other segments: ", count)
    # print(new_dataset_index)
    print("train", len(new_dataset_index['train']))
    print("test", len(new_dataset_index['test']))
    print("validation", len(new_dataset_index['validation']))

    pickle.dump(new_dataset_index, open('./Data/' + out_file, "wb"), pickle.HIGHEST_PROTOCOL)
    print("Dataset index saved!")


def detect_other(label_file_path, segment_index):
    vote_arr = pickle.load(open(label_file_path, 'rb'), encoding='latin1')
    other = np.array([1, 0, 0, 0, 0, 0])
    if vote_arr[segment_index][0][0] == 1:
        return True
    else:
        return False

def execute_service(in_path, out_path):

    down_sample_init(in_path, out_path)

execute_service(sys.argv[1], sys.argv[2])