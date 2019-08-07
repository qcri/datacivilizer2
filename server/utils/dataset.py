import os
import pickle

import numpy as np
import torch
from torch.utils.data import Dataset
from Tools import Cleaning
import sys
import h5py

np.set_printoptions(threshold=sys.maxsize)

# FIRST_DATA_PATH = "/mnt/disks/3_2T_SSD/EEG_10s_splits/first_dataset_sungtae_eeg_10s_split"
# SECOND_DATA_PATH = "/home/ast0414/Data/second_dataset_from_cpd_eeg_10s_split"
#
# FIRST_DATA_KEYS = set(np.load("/home/ast0414/Data/first_dataset_key_array.npy").tolist())
# SECOND_DATA_KEYS = set(np.load("/home/ast0414/Data/second_dataset_key_array.npy").tolist())


# def get_file_path(key_string, segment_idx):
# 	pid, date_str, time_str = key_string.split('_')
# 	if key_string in FIRST_DATA_KEYS:
# 		return os.path.join(FIRST_DATA_PATH, pid, date_str, time_str, "{}.pkl".format(segment_idx))
# 	elif key_string in SECOND_DATA_KEYS:
# 		return os.path.join(SECOND_DATA_PATH, pid, date_str, time_str, "{}.pkl".format(segment_idx))
# 	else:
# 		raise KeyError


def laplace_smoothing(observations, alpha=1.0):
    # assuming that 'observations' is a numpy 1d array
    return (observations + alpha) / (np.sum(observations) + alpha*observations.shape[0])


# class MontagePickleDataset(Dataset):
#
# 	def __init__(self, list_index, num_surroundings=2, alpha=1.0, transform=None):
# 		# EEG Montage Data Path
# 		self.data_path = "/home/ast0414/Data/eeg_symlink_all"
# 		# self.data_path = "/home/ast0414/Data/first_dataset_sungtae_eeg"
#
# 		# cEEG Sampling Rate (Hz)
# 		self.sampling_rate = 200
#
# 		# duration of each segment of data (sec)
# 		self.segment_duration = 2
#
# 		# number of montage channels
# 		self.num_channels = 18
#
# 		# number of classes
# 		self.num_classes = 6
#
# 		# Duration of context segments in the original data (in sec)
# 		# indexing and labels in the original dataset start after this amount of time
# 		self.context_duration = 6
#
# 		# Number of surrounding segments we want to use
# 		self.num_surroundings = num_surroundings
#
# 		# pseudo count for Laplace smoothing
# 		self.alpha = alpha
#
# 		# class weights
# 		# class_weights: [0.26186868, 2.13210605, 1.13455135, 2.89780825, 3.7256212, 4.60052174]
#
# 		self.list_index = list_index
# 		self.transform = transform
#
# 	def __getitem__(self, index):
# 		"""
# 		Args:
# 			index (int): Index
#
# 		Returns:
# 			tuple: (sample, target) where target is class_index of the target class.
# 		"""
# 		subject_key, seq_idx, segment_idx, target = self.list_index[index]
#
# 		eeg_file_path = os.path.join(self.data_path, "eeg_{}.pkl".format(subject_key))
# 		eeg_data_array = pickle.load(open(eeg_file_path, 'rb'), encoding='latin1')
#
# 		num_seq, len_seq, num_channel = eeg_data_array.shape
#
# 		if len_seq == (2*self.num_surroundings + 1) * self.segment_duration * self.sampling_rate:
# 			# data from CPD
# 			montage = eeg_data_array[seq_idx, :, :].astype(dtype=np.float32).transpose()
# 		else:
# 			# data from continuous eeg
# 			center_segment_start = (self.context_duration + segment_idx * self.segment_duration) * self.sampling_rate
# 			center_segment_end = center_segment_start + self.segment_duration * self.sampling_rate  # -1: I don't subtract 1 for convenient indexing later
#
# 			eeg_start_idx = center_segment_start - self.num_surroundings * self.segment_duration * self.sampling_rate
# 			eeg_end_idx = center_segment_end + self.num_surroundings * self.segment_duration * self.sampling_rate
#
# 			montage = eeg_data_array[seq_idx, eeg_start_idx:eeg_end_idx, :].astype(dtype=np.float32).transpose()
#
# 		if self.transform is not None:
# 			montage = self.transform(montage)
#
# 		# This shares memory between ndarray and tensor
# 		montage_tensor = torch.from_numpy(montage)
# 		target_tensor = torch.from_numpy(laplace_smoothing(target, alpha=self.alpha).astype(dtype=np.float32))
#
# 		return montage_tensor, target_tensor, (subject_key, seq_idx, segment_idx)
#
# 	def __len__(self):
# 		return len(self.list_index)
#
# 	def __repr__(self):
# 		fmt_str = 'Dataset ' + self.__class__.__name__ + '\n'
# 		fmt_str += '    Number of datapoints: {}\n'.format(self.__len__())
# 		fmt_str += '    Data Location: {}\n'.format(self.data_path)
# 		tmp = '    Transforms (if any): '
# 		fmt_str += '{0}{1}\n'.format(tmp, self.transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
# 		return fmt_str

class MontagePickleDataset(Dataset):

    def __init__(self, list_index, label_h5_path, transform):

        ### self.FIRST_DATA_KEYS = set(np.load("/home/ast0414/Data/first_dataset_key_array.npy", allow_pickle=True).tolist())
        self.SECOND_DATA_KEYS = set(np.load("/home/dell/eeg-data-sample/second_dataset_key_array.npy", allow_pickle=True).tolist())

        ### self.FIRST_DATA_PATH = "/mnt/disks/3_2T_SSD/EEG_10s_splits/first_dataset_sungtae_eeg_10s_split"
        self.SECOND_DATA_PATH = "/home/dell/sssd/dirty1"

        self.LABEL_H5_PATH = label_h5_path
        self.labels_hf = None
        # print(list_index)
        self.list_index = list_index
        self.transform = transform

    def __getitem__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (sample, target) where target is class_index of the target class.
        """
        subject_key, segment_idx, target = self.list_index[index]
        pid, date_str, time_str = subject_key.split('_')
        # emu285文件被损坏，所以剔除试一下
        if pid == "emu285":
            subject_key, segment_idx, target = self.list_index[index-1]

        # print("~~~~~~here~~~~~~")
        ### if subject_key in self.FIRST_DATA_KEYS:
        ###    eeg_file_path = os.path.join(self.FIRST_DATA_PATH, pid, date_str, time_str, "{}.pkl".format(segment_idx))
        ### el
        subject_key = bytes(subject_key.encode('utf-8'))
        if subject_key in self.SECOND_DATA_KEYS:
            eeg_file_path = os.path.join(self.SECOND_DATA_PATH, pid, date_str, time_str, "{}.pkl".format(segment_idx))
            # print(eeg_file_path)
        else:
            raise KeyError


        with open(eeg_file_path, 'rb') as f:
            eeg_data_array = pickle.load(f)

        # 如果前面进行了清洗，这句话就不需要了
        # 清理要在训练之前，算一个单独的步骤，否则训练的时间太长
        montage = eeg_data_array.astype(dtype=np.float32).transpose()

        if self.transform is not None:
            montage = self.transform(montage)

        # # Data Cleaning
        # montage = Cleaning.clean_pipline(montage, 200)

        # Data Dirty
        # montage = Cleaning.dirty(montage, 2500, 1500)



        # （model.h5报错
        if self.labels_hf is None:
             self.labels_hf = h5py.File(self.LABEL_H5_PATH, 'r', libver='latest', swmr=True)

        target_array = np.array(self.labels_hf[subject_key][str(segment_idx)]).astype(dtype=np.float32)




        # traget_array = np.array()

        # This shares memory between ndarray and tensor
        # consume 15.1G (4 workers, data only) 32G (12 workers, eval forward) 32.5G (12 workers, at 65% train)
        montage_tensor = torch.from_numpy(montage)
        # target_tensor = torch.from_numpy(laplace_smoothing(target_array, alpha=self.alpha).astype(dtype=np.float32))
        target_tensor = torch.from_numpy(target_array)

        # Random data consume 15GB (4 workers, data only) 15.3GB (4 workers, eval forward) 15.3GB (4 workers, train)
        # montage_tensor = torch.rand(18, 2000)
        # target_tensor = torch.rand(6)

        return montage_tensor, target_tensor, (subject_key, segment_idx)

    def __len__(self):
        return len(self.list_index)

    def __repr__(self):
        fmt_str = 'Dataset ' + self.__class__.__name__ + '\n'
        fmt_str += '    Number of datapoints: {}\n'.format(self.__len__())
        tmp = '    Transforms (if any): '
        fmt_str += '{0}{1}\n'.format(tmp, self.transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
        return fmt_str
