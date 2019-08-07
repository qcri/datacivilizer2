from collections import OrderedDict

import torch
import torch.nn as nn
import torch.nn.functional as F


class _DenseLayer(nn.Sequential):
	def __init__(self, num_input_features, growth_rate, bn_size, drop_rate, conv_bias, batch_norm):
		super(_DenseLayer, self).__init__()
		if batch_norm:
			self.add_module('norm1', nn.BatchNorm1d(num_input_features)),
		# self.add_module('relu1', nn.ReLU()),
		self.add_module('elu1', nn.ELU()),
		self.add_module('conv1', nn.Conv1d(num_input_features, bn_size * growth_rate, kernel_size=1, stride=1, bias=conv_bias)),
		if batch_norm:
			self.add_module('norm2', nn.BatchNorm1d(bn_size * growth_rate)),
		# self.add_module('relu2', nn.ReLU()),
		self.add_module('elu2', nn.ELU()),
		self.add_module('conv2', nn.Conv1d(bn_size * growth_rate, growth_rate, kernel_size=3, stride=1, padding=1, bias=conv_bias)),
		# self.add_module('conv2', nn.Conv1d(bn_size * growth_rate, growth_rate, kernel_size=7, stride=1, padding=3, bias=conv_bias)),
		self.drop_rate = drop_rate

	def forward(self, x):
		# print("Dense Layer Input: ")
		# print(x.size())
		new_features = super(_DenseLayer, self).forward(x)
		# print("Dense Layer Output:")
		# print(new_features.size())
		if self.drop_rate > 0:
			new_features = F.dropout(new_features, p=self.drop_rate, training=self.training)
		return torch.cat([x, new_features], 1)


class _DenseBlock(nn.Sequential):
	def __init__(self, num_layers, num_input_features, bn_size, growth_rate, drop_rate, conv_bias, batch_norm):
		super(_DenseBlock, self).__init__()
		for i in range(num_layers):
			layer = _DenseLayer(num_input_features + i * growth_rate, growth_rate, bn_size, drop_rate, conv_bias, batch_norm)
			self.add_module('denselayer%d' % (i + 1), layer)


class _Transition(nn.Sequential):
	def __init__(self, num_input_features, num_output_features, conv_bias, batch_norm):
		super(_Transition, self).__init__()
		if batch_norm:
			self.add_module('norm', nn.BatchNorm1d(num_input_features))
		# self.add_module('relu', nn.ReLU())
		self.add_module('elu', nn.ELU())
		self.add_module('conv', nn.Conv1d(num_input_features, num_output_features, kernel_size=1, stride=1, bias=conv_bias))
		self.add_module('pool', nn.AvgPool1d(kernel_size=2, stride=2))


class DenseNetEnconder(nn.Module):
	def __init__(self, growth_rate=32, block_config=(4, 4, 4, 4, 4, 4, 4),  #block_config=(6, 12, 24, 48, 24, 20, 16),  #block_config=(6, 12, 24, 16),
				 in_channels=16, num_init_features=64, bn_size=4, drop_rate=0.2, conv_bias=True, batch_norm=False):

		super(DenseNetEnconder, self).__init__()

		# First convolution
		first_conv = OrderedDict([('conv0', nn.Conv1d(in_channels, num_init_features, kernel_size=7, stride=2, padding=3, bias=conv_bias))])
		# first_conv = OrderedDict([('conv0', nn.Conv1d(in_channels, num_init_features, groups=in_channels, kernel_size=7, stride=2, padding=3, bias=conv_bias))])
		# first_conv = OrderedDict([('conv0', nn.Conv1d(in_channels, num_init_features, kernel_size=15, stride=2, padding=7, bias=conv_bias))])

		# first_conv = OrderedDict([
		# 	('conv0-depth', nn.Conv1d(in_channels, 32, groups=in_channels, kernel_size=7, stride=2, padding=3, bias=conv_bias)),
		# 	('conv0-point', nn.Conv1d(32, num_init_features, kernel_size=1, stride=1, bias=conv_bias)),
		# ])

		if batch_norm:
			first_conv['norm0'] = nn.BatchNorm1d(num_init_features)
		# first_conv['relu0'] = nn.ReLU()
		first_conv['elu0'] = nn.ELU()
		first_conv['pool0'] = nn.MaxPool1d(kernel_size=3, stride=2, padding=1)

		self.densenet = nn.Sequential(first_conv)

		num_features = num_init_features
		for i, num_layers in enumerate(block_config):
			block = _DenseBlock(num_layers=num_layers, num_input_features=num_features,
								bn_size=bn_size, growth_rate=growth_rate, drop_rate=drop_rate, conv_bias=conv_bias, batch_norm=batch_norm)
			self.densenet.add_module('denseblock%d' % (i + 1), block)
			num_features = num_features + num_layers * growth_rate
			if i != len(block_config) - 1:
				trans = _Transition(num_input_features=num_features, num_output_features=num_features // 2, conv_bias=conv_bias, batch_norm=batch_norm)
				self.densenet.add_module('transition%d' % (i + 1), trans)
				num_features = num_features // 2

		# Final batch norm
		if batch_norm:
			self.densenet.add_module('norm{}'.format(len(block_config) + 1), nn.BatchNorm1d(num_features))
		# self.features.add_module('norm5', BatchReNorm1d(num_features))

		# self.densenet.add_module('relu{}'.format(len(block_config) + 1), nn.ReLU())
		self.densenet.add_module('elu{}'.format(len(block_config) + 1), nn.ELU())
		self.densenet.add_module('pool{}'.format(len(block_config) + 1), nn.AvgPool1d(kernel_size=7, stride=3))  # stride originally 1

		self.num_features = num_features

		# Official init from torch repo.
		for m in self.modules():
			if isinstance(m, nn.Conv1d):
				nn.init.kaiming_normal_(m.weight.data)
			elif isinstance(m, nn.BatchNorm1d):
				m.weight.data.fill_(1)
				m.bias.data.zero_()
			elif isinstance(m, nn.Linear):
				m.bias.data.zero_()

	def forward(self, x):
		features = self.densenet(x)
		# print("Final Output")
		# print(features.size())
		return features.view(features.size(0), -1)


class DenseNetClassifier(nn.Module):
	# def __init__(self, growth_rate=16, block_config=(3, 6, 12, 8),  #block_config=(6, 12, 24, 48, 24, 20, 16),  #block_config=(6, 12, 24, 16),
	# 			 in_channels=18, num_init_features=32, bn_size=2, drop_rate=0, conv_bias=False, drop_fc=0.5, num_classes=6):
	def __init__(self, growth_rate=32, block_config=(4, 4, 4, 4, 4, 4, 4),
				 in_channels=18, num_init_features=64, bn_size=4, drop_rate=0.5, conv_bias=True, batch_norm=False, drop_fc=0.5, num_classes=6):

		super(DenseNetClassifier, self).__init__()

		self.features = DenseNetEnconder(growth_rate=growth_rate, block_config=block_config, in_channels=in_channels,
										 num_init_features=num_init_features, bn_size=bn_size, drop_rate=drop_rate,
										 conv_bias=conv_bias, batch_norm=batch_norm)

		# dimensional reduction
		self.reduced_features = nn.Sequential(
			nn.Dropout(p=drop_fc),
			nn.Linear(self.features.num_features, 64),
			nn.ELU()
		)

		self.num_features = 64  # self.features.num_features

		# Linear layer
		self.classifier = nn.Sequential(
			nn.Dropout(p=drop_fc),
			nn.Linear(self.num_features, num_classes)
		)

		# Official init from torch repo.
		for m in self.modules():
			if isinstance(m, nn.Conv1d):
				nn.init.kaiming_normal_(m.weight.data)
			elif isinstance(m, nn.BatchNorm1d):
				m.weight.data.fill_(1)
				m.bias.data.zero_()
			elif isinstance(m, nn.Linear):
				m.bias.data.zero_()

	def forward(self, x):
		# print("Input Size")
		# print(x.size())
		features = self.features(x)
		features = self.reduced_features(features)
		out = self.classifier(features)
		# print("Features Size")
		# print(features.size())
		# print("Output Size")
		# print(out.size())
		return out, features

# class DenseNetClassifier(nn.Module):
# 	# def __init__(self, growth_rate=16, block_config=(3, 6, 12, 8),  #block_config=(6, 12, 24, 48, 24, 20, 16),  #block_config=(6, 12, 24, 16),
# 	# 			 in_channels=18, num_init_features=32, bn_size=2, drop_rate=0, conv_bias=False, drop_fc=0.5, num_classes=6):
# 	# def __init__(self, growth_rate=32, block_config=(4, 4, 4, 4, 4, 4, 4),
# 	# 			 in_channels=18, num_init_features=64, bn_size=4, drop_rate=0.2, conv_bias=True, batch_norm=False, drop_fc=0.5, num_classes=6):
# 	def __init__(self, growth_rate=24, block_config=(6, 12, 24, 48, 36, 32, 24),#(6, 12, 24, 16),
# 				 in_channels=18, num_init_features=32, bn_size=4, drop_rate=0.2, conv_bias=True, batch_norm=False,
# 				 drop_fc=0.5, num_classes=6):
#
# 		super(DenseNetClassifier, self).__init__()
#
# 		self.features = DenseNetEnconder(growth_rate=growth_rate, block_config=block_config, in_channels=in_channels,
# 										 num_init_features=num_init_features, bn_size=bn_size, drop_rate=drop_rate,
# 										 conv_bias=conv_bias, batch_norm=batch_norm)
#
# 		# dimensional reduction
# 		self.reduced_features = nn.Sequential(
# 			nn.Dropout(p=drop_fc),
# 			nn.Linear(self.features.num_features, 64),
# 			nn.ELU()
# 		)
# 		self.num_features = 64
#
# 		# Linear layer
# 		self.classifier = nn.Sequential(
# 			nn.Dropout(p=drop_fc),
# 			nn.Linear(self.num_features, num_classes)
# 		)
#
# 		# Official init from torch repo.
# 		for m in self.modules():
# 			if isinstance(m, nn.Conv1d):
# 				nn.init.kaiming_normal_(m.weight.data)
# 			elif isinstance(m, nn.BatchNorm1d):
# 				m.weight.data.fill_(1)
# 				m.bias.data.zero_()
# 			elif isinstance(m, nn.Linear):
# 				m.bias.data.zero_()
#
# 	def forward(self, x):
# 		# print("Input Size")
# 		# print(x.size())
# 		features = self.features(x)
# 		features = self.reduced_features(features)
# 		out = self.classifier(features)
# 		# print("Features Size")
# 		# print(features.size())
# 		# print("Output Size")
# 		# print(out.size())
# 		return out, features
