import sys
import glob
import pickle
import operator
import numpy as np
from tqdm import tqdm
from shutil import copyfile
from utils.from_filepath_to_index import from_filepath_to_index
from utils.weight_cal import compute_class_weight
from utils.stacked_bar_chart import plot_stacked_bar_chart_2

def drop_init(in_file, out_file):
    all_dataset = glob.glob("./Data/second_dataset_from_cpd_eeg_10s_split/*/*/*/*.pkl")
    count_zero = 0
    all_zero_file_path = []
    not_zero_file_path = []
    az_file_path = set(np.load("./Data/all_zero_file_path.npy", allow_pickle=True))
    nz_file_path = set(np.load("./Data/not_zero_file_path.npy", allow_pickle=True))
    return drop_in_dataset_index(in_file, out_file, nz_file_path, az_file_path)

def drop_in_dataset_index(in_file, out_file, nz_file_path, az_file_path):

    with open('./Data/' + in_file, "rb") as f:
        data_splits_sample = pickle.load(f)

    non_zero_train = 0
    non_zero_test = 0
    non_zero_validation = 0
    all_zero_train = 0
    all_zero_test = 0
    all_zero_validation = 0

    new_dataset_index = dict()
    for not_zero_file_path in tqdm(nz_file_path):
        p, home, dell, a, b, subject_key, date_str, time_str, segment = not_zero_file_path.split('/')
        segment_index = segment.split('.')[0]
        m = subject_key + "_" + date_str + "_" + time_str

        tmp = from_filepath_to_index(not_zero_file_path)
        jump = 0
        for i in range(len(data_splits_sample['train'])):
            if m == data_splits_sample['train'][i][0] and int(segment_index) == int(data_splits_sample['train'][i][1]):
                non_zero_train += 1
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
                non_zero_validation += 1
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
                non_zero_test += 1
                if 'test' in new_dataset_index:
                    new_dataset_index['test'].extend(tmp)
                else:
                    new_dataset_index['test'] = tmp

    for not_zero_file_path in tqdm(az_file_path):
        p, home, dell, a, b, subject_key, date_str, time_str, segment = not_zero_file_path.split('/')
        segment_index = segment.split('.')[0]
        m = subject_key + "_" + date_str + "_" + time_str

        tmp = from_filepath_to_index(not_zero_file_path)
        jump = 0
        for i in range(len(data_splits_sample['train'])):
            if m == data_splits_sample['train'][i][0] and int(segment_index) == int(data_splits_sample['train'][i][1]):
                all_zero_train += 1
                jump = 1
                break
        if jump == 1:
            continue
        jump_1 = 0
        for i in range(len(data_splits_sample['validation'])):
            if m == data_splits_sample['validation'][i][0] and int(segment_index) == int(data_splits_sample['validation'][i][1]):
                all_zero_validation += 1
                jump_1 = 1
                break
        if jump_1 == 1:
            continue
        for i in range(len(data_splits_sample['test'])):
            if m == data_splits_sample['test'][i][0] and int(segment_index) == int(data_splits_sample['test'][i][1]):
                all_zero_test += 1

    print("train", len(new_dataset_index['train']))
    print("test", len(new_dataset_index['test']))
    print("validation", len(new_dataset_index['validation']))

    pickle.dump(new_dataset_index, open('./Data/' + out_file, "wb"),
                pickle.HIGHEST_PROTOCOL)
    print("Dataset index saved!")

    return non_zero_train, non_zero_test, non_zero_validation, all_zero_train, all_zero_test, all_zero_validation


def equal_tuple(a, b):
    if a[0] == b[0] and a[1] == b[1] and a[2] == b[2]:
        return True
    else:
        return False

def execute_service(in_path, out_path, viz_path):

    # For demo purposes, just copy precomputed output to the run directory
    precomp_out_path = 'ml_outputs/out_-9.pkl'
    precomp_viz_path = 'ml_outputs/viz_-9.jpg'
    copyfile('./Data/' + precomp_out_path, './Data/' + out_path)
    copyfile('./Data/' + precomp_viz_path, './Data/' + viz_path)
    return 

    nztr, nzte, nzv, aztr, azte, azv = drop_init(in_path, out_path)
    plot_stacked_bar_chart_2(viz_path, [nztr, nzte, nzv], [aztr, azte, azv])

execute_service(sys.argv[1], sys.argv[2], sys.argv[3])