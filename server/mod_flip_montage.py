import sys
import numpy as np

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

def execute_service(in_path, out_path):

    # TODO
    pass

execute_service(sys.argv[1], sys.argv[2])