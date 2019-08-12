import sys
import os
import numpy as np
import pickle
from tqdm import tqdm

montages = [
    [["FP1", "F7"], ["F7", "T3"], ["T3", "T5"], ["T5", "O1"]],  # LL
    [["FP2", "F8"], ["F8", "T4"], ["T4", "T6"], ["T6", "O2"]],  # RL
    [["FP1", "F3"], ["F3", "C3"], ["C3", "P3"], ["P3", "O1"]],  # LP
    [["FP2", "F4"], ["F4", "C4"], ["C4", "P4"], ["P4", "O2"]],  # RP
]

class RandomMontageFlip(object):
    """Flip the given EEG signal montage channels randomly with a given probability.

    Args:
        p (float): probability of the signal being flipped. Default value is 0.5
    """

    def __init__(self, p=0.5, seed=1):
        self.p = p
        self.rng = np.random.RandomState(seed=seed)

    def __call__(self, signal):
        """
        Args:
            signal (ndarray of (num_channels, length)): signal to be flipped.

        Returns:
            ndarray: Randomly flipped signal.

        One way to augment the dataset is to flip left and right side electrodes.
        This function flips electrodes from the first and last row below, leaving
        the middle row (centered on the brain) unchanged:
            0        1       2       3        4       5       6       7
        [['Fp1'], ['F3'], ['C3'], ['P3'],  ['F7'], ['T3'], ['T5'], ['O1'],
           8        9      10         (unchanged)
        ['Fz'],  ['Cz'], ['Pz'],
           11       12      13      14     15      16       17      18
        ['Fp2'], ['F4'], ['C4'], ['P4'], ['F8'], ['T4'], ['T6'], ['O2']]
        """

        if self.rng.rand() < self.p:
            signal_copy = np.zeros(signal.shape).astype(signal.dtype)
            for i in range(4):
                # Swap LL and RL
                signal_copy[i, :] = signal[4 + i, :].copy()
                signal_copy[4 + i, :] = signal[i, :].copy()
                # Swap LP and RP
                signal_copy[8 + i, :] = signal[12 + i, :].copy()
                signal_copy[12 + i, :] = signal[8 + i, :].copy()
            # TODO: Currently, we use 18ch montage: same order of 16ch + [Fz-Cz, Cz-Pz]
            signal_copy[16:, :] = signal[16:, :].copy()

            return signal_copy

        return signal

    def __repr__(self):
        return self.__class__.__name__ + '(p={})'.format(self.p)

class Compose(object):
    """Composes several transforms together.

    Args:
        transforms (list of ``Transform`` objects): list of transforms to compose.

    Example:
        # >>> transforms.Compose([
        # >>>     transforms.CenterCrop(10),
        # >>>     transforms.ToTensor(),
        # >>> ])
    """

    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, signal):
        for t in self.transforms:
            signal = t(signal)
        return signal

class Normalize(object):
    """Normalize a tensor image with mean and standard deviation.
    Given mean: ``(M1,...,Mn)`` and std: ``(S1,..,Sn)`` for ``n`` channels, this transform
    will normalize each channel of the input ``torch.*Tensor`` i.e.
    ``input[channel] = (input[channel] - mean[channel]) / std[channel]``

    Args:
        mean (sequence): Sequence of means for each channel.
        std (sequence): Sequence of standard deviations for each channel.
    """

    def __init__(self, mean, std):
        self.mean = np.array([mean]).T
        self.std = np.array([std]).T

    def __call__(self, signal):
        """
        Args:
            signal (ndarray): signal(C, L) to be normalized.

        Returns:
            ndarray: Normalized signal array.
        """

        # Broadcated operation
        signal -= self.mean
        signal /= self.std

        return signal

    def __repr__(self):
        return self.__class__.__name__ + '(mean={0}, std={1})'.format(self.mean, self.std)

class Processor():

    def __init__(self, in_path, out_path, list_index, transform):

        ### self.FIRST_DATA_KEYS = set(np.load("/home/ast0414/Data/first_dataset_key_array.npy", allow_pickle=True).tolist())
        self.SECOND_DATA_KEYS = set(np.load("./Data/second_dataset_key_array.npy", allow_pickle=True).tolist())

        ### self.FIRST_DATA_PATH = "/mnt/disks/3_2T_SSD/EEG_10s_splits/first_dataset_sungtae_eeg_10s_split"
        self.SECOND_DATA_PATH = "/home/dell/sssd/dirty1"

        self.LABEL_H5_PATH = "./Data/labels.h5"
        self.labels_hf = None
        # print(list_index)
        self.list_index = list_index
        self.transform = transform

        self.in_path = in_path
        self.out_path = out_path

    def process_all_items(self):
        for i in tqdm(range(len(self.list_index))):
            self.process_item(i)

    def process_item(self, index):
        subject_key, segment_idx, target = self.list_index[index]
        pid, date_str, time_str = subject_key.split('_')

        if pid == "emu285":
            subject_key, segment_idx, target = self.list_index[index-1]

        subject_key = bytes(subject_key.encode('utf-8'))
        if subject_key in self.SECOND_DATA_KEYS:
            eeg_dir_in_path = os.path.join('./Data/' + self.in_path, pid, date_str, time_str)
            eeg_file_in_path = os.path.join(eeg_dir_in_path, "{}.pkl".format(segment_idx))
            eeg_dir_out_path = os.path.join('./Data/' + self.out_path, pid, date_str, time_str)
            eeg_file_out_path = os.path.join(eeg_dir_out_path, "{}.pkl".format(segment_idx))
        else:
            raise KeyError

        with open(eeg_file_in_path, 'rb') as f:
            eeg_data_array = pickle.load(f)

        montage = eeg_data_array.astype(dtype=np.float32).transpose()

        if self.transform is not None:
            montage = self.transform(montage)

        if not os.path.exists(eeg_dir_out_path):
            os.makedirs(eeg_dir_out_path)

        data_array = montage.transpose()

        # TODO: verify object format
        with open(eeg_file_out_path, 'wb') as f:
            pickle.dump(montage, f)

        # if self.labels_hf is None:
        #      self.labels_hf = h5py.File(self.LABEL_H5_PATH, 'r', libver='latest', swmr=True)

        # target_array = np.array(self.labels_hf[subject_key][str(segment_idx)]).astype(dtype=np.float32)

        # montage_tensor = torch.from_numpy(montage)
        # target_tensor = torch.from_numpy(target_array)

        # return montage_tensor, target_tensor, (subject_key, segment_idx)

def execute_service(in_path, index_name, out_path):
    print(in_path, index_name)
    return

    mean=[0.05822158, 0.79031128, 0.68925828, 0.60800403, 0.92262352, 0.6753147,
        0.73978873, 0.7950735, 0.07544717, 0.5617258, 0.92687569, 0.60170792,
        0.90717008, 0.79729081, 0.67532425, 0.84732697, 0.77063115, 0.62400107]
    std=[76.89937982, 63.08870946, 67.46303121, 72.84682511, 71.82783947, 64.95668017,
        66.33093137, 71.29754579, 76.1623206, 61.62166303, 63.41062531, 69.50769695,
        71.26202116, 62.16298833, 63.83597864, 71.35798488, 65.21853278, 65.61397046]
    flipMontage = RandomMontageFlip()
    normalize = Normalize(mean, std)
    transform = Compose([flipMontage, normalize])

    with open(os.path.join('./Data', index_name), "rb") as f:
        data_splits = pickle.load(f)

    processor = Processor(in_path, out_path, data_splits['train'], transform)
    processor.process_all_items()

if (sys.argv[1].endswith('.pkl')):
    execute_service(sys.argv[2], sys.argv[1], sys.argv[3])
else:
    execute_service(sys.argv[1], sys.argv[2], sys.argv[3])