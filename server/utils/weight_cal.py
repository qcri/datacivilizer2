import numpy as np
def compute_class_weight(index_set, alpha=1.0):
    soft_labels = np.stack([laplace_smoothing(vote, alpha=alpha) for subject, segment_idx, vote in index_set])
    pseudo_counts = np.sum(soft_labels, axis=0)
    total = np.sum(pseudo_counts)

    # class_weights = np.ones_like(counts, dtype=np.float32) / counts
    class_weights = total / (pseudo_counts.shape[0] * pseudo_counts)  # same with above one after normalization

    return class_weights, pseudo_counts


def laplace_smoothing(observations, alpha=1.0):
    # assuming that 'observations' is a numpy 1d array
    return (observations + alpha) / (np.sum(observations) + alpha*observations.shape[0])
