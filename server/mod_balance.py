import sys
import pickle
import numpy as np
from tqdm import tqdm
from shutil import copyfile
from utils.stacked_bar_chart import plot_stacked_bar_chart

def down_sample_init(in_file, out_file):
    SECOND_DATA_KEYS = set(np.load("./Data/file_name_exist_in_second.npy", allow_pickle=True))

    with open('./Data/' + in_file, "rb") as f:
        data_splits = pickle.load(f)
    print(data_splits['train'][0][0])
    print("train", len(data_splits['train']))
    print("test", len(data_splits['test']))
    print("validation", len(data_splits['validation']))
    new_dataset_index = dict()
    prob = 0
    
    other_train_kept = 0
    other_train_removed = 0
    other_test_kept = 0
    other_test_removed = 0
    other_validation_kept = 0
    other_validation_removed = 0
    rest_train = 0
    rest_test = 0
    rest_validation = 0
    
    not_other = 0
    for eeg_file_path in tqdm(SECOND_DATA_KEYS):

        eeg_file_path = eeg_file_path.replace("eeg-data-sample", "ssd")
        p, home, dell, a, b, subject_key, date_str, time_str, segment = eeg_file_path.split('/')
        segment_index = segment.split('.')[0]
        c = "second_dataset_from_cpd_label"
        m = subject_key + "_" + date_str + "_" + time_str
        d = "label_" + m + ".pkl"
        label_file_path = ("./Data/{}/{}".format(c, d))

        if detect_other(label_file_path, int(segment_index)):
            prob = prob + 1
            if prob % 2 == 0:
                vote_arr = pickle.load(open(label_file_path, 'rb'), encoding='latin1')
                tmp = [(m, int(segment_index), vote_arr[int(segment_index)])]
                t_1 = 0
                for i in range(len(data_splits['train'])):
                    if m == data_splits['train'][i][0]:
                        other_train_kept += 1
                        t_1 = 1
                        if 'train' in new_dataset_index:
                            new_dataset_index['train'].extend(tmp)
                        else:
                            new_dataset_index['train'] = tmp
                        break
                if t_1 == 1:
                    continue
                for i in range(len(data_splits['test'])):
                    if m == data_splits['test'][i][0]:
                        other_test_kept += 1
                        if 'test' in new_dataset_index:
                            new_dataset_index['test'].extend(tmp)
                        else:
                            new_dataset_index['test'] = tmp
                        break
                for i in range(len(data_splits['validation'])):
                    if m == data_splits['validation'][i][0]:
                        other_validation_kept += 1
                        if 'validation' in new_dataset_index:
                            new_dataset_index['validation'].extend(tmp)
                        else:
                            new_dataset_index['validation'] = tmp
                        break
            else:
                vote_arr = pickle.load(open(label_file_path, 'rb'), encoding='latin1')
                tmp = [(m, int(segment_index), vote_arr[int(segment_index)])]
                t_1 = 0
                for i in range(len(data_splits['train'])):
                    if m == data_splits['train'][i][0]:
                        other_train_removed += 1
                        t_1 = 1
                        break
                if t_1 == 1:
                    continue
                for i in range(len(data_splits['test'])):
                    if m == data_splits['test'][i][0]:
                        other_test_removed += 1
                        break
                for i in range(len(data_splits['validation'])):
                    if m == data_splits['validation'][i][0]:
                        other_validation_removed += 1
                        break
        else:
            not_other += 1
            if not_other % 1000 == 0:
                pass
            vote_arr = pickle.load(open(label_file_path, 'rb'), encoding='latin1')
            tmp = [(m, int(segment_index), vote_arr[int(segment_index)])]
            t = 0
            for i in range(len(data_splits['train'])):
                if m == data_splits['train'][i][0]:
                    rest_train += 1
                    t = 1
                    if 'train' in new_dataset_index:
                        new_dataset_index['train'].extend(tmp)
                    else:
                        new_dataset_index['train'] = tmp
                    break

            if t == 1:
                continue
            for i in range(len(data_splits['test'])):
                if m == data_splits['test'][i][0]:
                    rest_test += 1
                    if 'test' in new_dataset_index:
                        new_dataset_index['test'].extend(tmp)
                    else:
                        new_dataset_index['test'] = tmp
                    break
            for i in range(len(data_splits['validation'])):
                if m == data_splits['validation'][i][0]:
                    rest_validation += 1
                    if 'validation' in new_dataset_index:
                        new_dataset_index['validation'].extend(tmp)
                    else:
                        new_dataset_index['validation'] = tmp
                    break


    print("Left other segments: ", other_train_kept + other_test_kept + other_validation_kept)
    print("train", len(new_dataset_index['train']))
    print("test", len(new_dataset_index['test']))
    print("validation", len(new_dataset_index['validation']))

    pickle.dump(new_dataset_index, open('./Data/' + out_file, "wb"), pickle.HIGHEST_PROTOCOL)
    print("Dataset index saved!")

    return other_train_kept, other_train_removed, other_test_kept, other_test_removed, other_validation_kept, other_validation_removed, rest_train, rest_test, rest_validation


def detect_other(label_file_path, segment_index):
    vote_arr = pickle.load(open(label_file_path, 'rb'), encoding='latin1')
    other = np.array([1, 0, 0, 0, 0, 0])
    if vote_arr[segment_index][0][0] == 1:
        return True
    else:
        return False

def execute_service(in_path, out_path, viz_path):

    # For demo purposes, just copy precomputed output to the run directory
    precomp_out_path = 'main_D_outputs/out_-3.pkl'
    precomp_viz_path = 'main_D_outputs/viz_-3.jpg'
    copyfile('./Data/' + precomp_out_path, './Data/' + out_path)
    copyfile('./Data/' + precomp_viz_path, './Data/' + viz_path)
    return 

    otrk, otrr, otek, oter, ovk, ovr, rtr, rte, rv = down_sample_init(in_path, out_path)
    plot_stacked_bar_chart(viz_path, [otrk, otek, ovk], [otrr, oter, ovr], [rtr, rte, rv])

execute_service(sys.argv[1], sys.argv[2], sys.argv[3])