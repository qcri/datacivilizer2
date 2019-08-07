import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot_learning_curves(train_losses, valid_losses, train_accuracies, valid_accuracies):

	fig0 = plt.figure(figsize=(8, 6))
	plt.plot(np.arange(len(train_losses)), np.array(train_losses), label='Training Loss')
	plt.plot(np.arange(len(valid_losses)), np.array(valid_losses), label='Validation Loss')
	plt.title("Loss Curve", fontsize=18)
	plt.xlabel('epoch', fontsize=14)
	plt.ylabel('Loss', fontsize=14)
	plt.xticks(fontsize=12)
	plt.yticks(fontsize=12)
	plt.legend(loc="best", fontsize=14)
	plt.tight_layout()

	fig1 = plt.figure(figsize=(8, 6))
	plt.plot(np.arange(len(train_accuracies)), np.array(train_accuracies), label='Training Accuracy')
	plt.plot(np.arange(len(valid_accuracies)), np.array(valid_accuracies), label='Validation Accuracy')
	plt.title("Accuracy Curve", fontsize=18)
	plt.xlabel('epoch', fontsize=14)
	plt.ylabel('Accuracy', fontsize=14)
	plt.xticks(fontsize=12)
	plt.yticks(fontsize=12)
	plt.legend(loc="best", fontsize=14)
	plt.tight_layout()

	return fig0, fig1

