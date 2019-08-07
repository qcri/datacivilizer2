import os
import signal
import shutil

import numpy as np
import torch

from tqdm import tqdm


class AverageMeter(object):
	"""Computes and stores the average and current value"""

	def __init__(self):
		self.reset()

	def reset(self):
		self.val = 0
		self.avg = 0
		self.sum = 0
		self.count = 0

	def update(self, val, n=1):
		self.val = val
		self.sum += val * n
		self.count += n
		self.avg = self.sum / self.count


def count_parameters(model):
	return sum(p.numel() for p in model.parameters() if p.requires_grad)


def save_checkpoint(state, is_best, filename='checkpoint.pth'):
	torch.save(state, filename)
	if is_best:
		directory = os.path.dirname(filename)
		shutil.copyfile(filename, os.path.join(directory, 'best_checkpoint.pth'))


# For using keyboard interrupt
def worker_init(x):
	signal.signal(signal.SIGINT, signal.SIG_IGN)


def accuracy(output, target):
	with torch.no_grad():
		# TODO: Assuming that target is soft label
		batch_size = target.size(0)
		pred = output.max(1, keepdim=True)[1]
		hard_label = target.max(1, keepdim=True)[1]
		correct = pred.eq(hard_label).sum()

		return correct * 100.0 / batch_size


def train(model, train_loader, criterion, optimizer, use_cuda):
	losses = AverageMeter()
	acc = AverageMeter()

	model.train()
	for data, target, _ in tqdm(train_loader, desc="Train"):

		if use_cuda:
			# data, target = data.cuda(non_blocking=True), target.cuda(non_blocking=True)
			data, target = data.cuda(), target.cuda()

		optimizer.zero_grad()
		output, _ = model(data)
		loss = criterion(output, target)
		assert not np.isnan(loss.item()), 'Model diverged with loss = NaN'

		loss.backward()
		optimizer.step()

		losses.update(loss.item(), data.size(0))
		acc.update(accuracy(output, target).item(), data.size(0))

	return losses.avg, acc.avg


def evaluate(model, test_loader, criterion, use_cuda, details=False, h5file=None):
	losses = AverageMeter()
	acc = AverageMeter()

	if details:
		idxs = []
		labels = []
		logits = []
		# features = []

	model.eval()
	with torch.no_grad():
		for data, target, indexing in tqdm(test_loader, desc="Eval"):
			if use_cuda:
				data, target = data.cuda(), target.cuda()
			output, feature = model(data)
			loss = criterion(output, target)
			losses.update(loss.item(), data.size(0))
			acc.update(accuracy(output, target).item(), data.size(0))

			if details:
				subject_key = list(indexing[0])
				segment_idx = list(indexing[1])

				idxs.extend(zip(subject_key, segment_idx))
				logits.append(output.detach().cpu())
				labels.append(target.detach().cpu())

				if h5file is not None:
					feature = feature.detach().cpu().numpy()
					for i, (sub_key, seg_idx) in enumerate(zip(subject_key, segment_idx)):
						feature_data = feature[i]
						h5file.create_dataset("{}/{}".format(sub_key, seg_idx), data=feature_data, dtype='float32')

	if details:
		return losses.avg, acc.avg, idxs, torch.cat(logits, 0), torch.cat(labels, 0)
	else:
		return losses.avg, acc.avg


def make_result_details(indexings, soft_labels, logits):

	labels = np.argmax(soft_labels.numpy(), axis=1).tolist()
	scores = torch.softmax(logits, dim=1).numpy()

	argsort = np.argsort(scores, axis=1)
	N = scores.shape[0]
	I = np.ogrid[:N]
	predictions = argsort[:, -1]
	second_argmax = argsort[:, -2]

	confidences = scores[I, predictions]
	margins = confidences - scores[I, second_argmax]
	entropies = -np.sum(scores * np.log(scores), axis=1)

	predictions = predictions.tolist()
	confidences = confidences.tolist()
	margins = margins.tolist()
	entropies = entropies.tolist()

	# results = [{'file': filename, 'lut_index_start': idx, 'label': label, 'prediction': prediction, 'confidence': confidence, 'margin': margin, 'entropy': entropy}
	# 		   for filename, idx, label, prediction, confidence, margin, entropy in zip(list_files, indices, labels, predictions, confidences, margins, entropies)]
	results = [(subject, idx, label, prediction, confidence, margin, entropy)
			   for (subject, idx), label, prediction, confidence, margin, entropy
			   in zip(indexings, labels, predictions, confidences, margins, entropies)]

	return results
