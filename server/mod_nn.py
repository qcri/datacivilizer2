import os
import sys
import pickle
import argparse
import matplotlib
matplotlib.use('Agg')
from shutil import copyfile
import matplotlib.pyplot as plt
from timeit import default_timer as timer

import torch
import torch.backends.cudnn as cudnn
from torch.utils.data import DataLoader
import torch.optim as optim
from tensorboardX import SummaryWriter

from utils.weight_cal import compute_class_weight
from utils.dataset import MontagePickleDataset
from utils.model import count_parameters, save_checkpoint, train, evaluate
from utils.plot import plot_learning_curves
from utils.DenseNet import DenseNetClassifier
from utils.Loss import WeightedKLDivWithLogitsLoss

from tqdm import tqdm

def run_nn(in_data_dir, index_file, out_path, run_dir, save_path_name='save', resume=None, batch_size=256, epochs=50, start_epoch=0, lr=1e-4, wd=1e-3, workers=12, no_cuda=True, seed=1):

    # parser = argparse.ArgumentParser()
    # parser.add_argument('path', default='/home/dell/eeg-data-sample/', type=str, help='path to the main dir of the experiment')
    # parser.add_argument('--save', default='', type=str, metavar='PATH', help='save path under the main exp path')
    # parser.add_argument('--resume', default='', type=str, metavar='PATH', help='path to a checkpoint (default: none)')

    # parser.add_argument('--batch-size', type=int, default=256, help='input batch size for training (default: 512)')
    # parser.add_argument('--epochs', type=int, default=50, help='number of epochs to train (default: 100)')
    # parser.add_argument('--start-epoch', default=0, type=int, help='manual epoch number (useful on restarts)')

    # parser.add_argument('--lr', type=float, default=1e-4, help='learning rate (default: 1e-4)')
    # parser.add_argument('--wd', default=1e-3, type=float, help='weight decay (default: 1e-3)')

    # parser.add_argument('--workers', type=int, default=12, help='number of data loading workers (default: 12)')
    # parser.add_argument('--no-cuda', action='store_true', default=False, help='disables CUDA training')
    # parser.add_argument('--seed', type=int, default=1, help='random seed (default: 1)')

    # args = parser.parse_args()
    # if args.save == '':
    #     args.save = os.path.join(os.path.dirname(args.path),
    #                              '1DenseNet_sample_butter')
    # else:
    #     args.save = os.path.join(os.path.dirname(args.path), args.save)

    save_path = os.path.join('./Data/', run_dir, save_path_name)

    torch.manual_seed(seed)
    use_cuda = not no_cuda and torch.cuda.is_available()
    cudnn.benchmark = True if use_cuda else False

    print("===> Loading Datasets...")
    print("\t===> Loading data index info")

    with open(os.path.join('./Data/', index_file), "rb") as f:
        data_splits = pickle.load(f)
    print(len(data_splits['train']))
    
    label_h5_path = os.path.join('./Data/', "labels.h5")
    print(data_splits['train'][0])
    print("\t===> Construct train set")
    train_set = MontagePickleDataset(in_data_dir, list_index=data_splits['train'],
                                     label_h5_path=label_h5_path, transform=None)

    train_loader = DataLoader(dataset=train_set, batch_size=batch_size, shuffle=True, num_workers=workers)

    print("\t===> Construct validation set")
    val_set = MontagePickleDataset(in_data_dir, list_index=data_splits['validation'],
                                   label_h5_path=label_h5_path, transform=None)
    val_loader = DataLoader(dataset=val_set, batch_size=batch_size, shuffle=False, num_workers=workers)
    print("===> Dataset loaded!")

    # class_weights, pseudo_counts = compute_class_weight(data_splits['train'], alpha=0.2)
    # pickle.dump(class_weights, open("/home/dell/eeg-data-sample/class_weights_random_sample_without_zero.pkl", "wb"),
    #             pickle.HIGHEST_PROTOCOL)

    with open(os.path.join('./Data/', "class_weights.pkl"), "rb") as f:
        class_weights = pickle.load(f)
    class_weights = torch.from_numpy(class_weights).float()
    print("===> Class Weights: {}".format(class_weights))

    # Create model
    print('===> Building a Model')
    model = DenseNetClassifier()
    if use_cuda:
        model.cuda()
    print('===> Model built!')
    print('\t===> contains {} trainable params'.format(count_parameters(model)))
    # print('\t===> DenseNet Final Features: {}'.format(model.features.num_features))

    criterion = WeightedKLDivWithLogitsLoss(class_weights)
    if use_cuda:
        criterion.cuda()

    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=wd)

    os.makedirs(save_path, exist_ok=True)

    best_val_epoch = 0
    best_val_loss = sys.float_info.max
    best_val_acc = 0.0

    train_losses, train_accuracies = [], []
    val_losses, val_accuracies = [], []

    # optionally resume from a checkpoint
    if resume:
        if os.path.isfile(resume):
            print("===> Loading Checkpoint to Resume '{}'".format(resume))
            checkpoint = torch.load(resume)
            start_epoch = checkpoint['epoch'] + 1
            best_val_epoch = checkpoint['best_epoch']
            best_val_loss = checkpoint['best_valid_loss']
            best_val_acc = checkpoint['best_valid_accuracy']
            model.load_state_dict(checkpoint['state_dict'])
            optimizer.load_state_dict(checkpoint['optimizer'])
            # scheduler.load_state_dict(checkpoint['scheduler'])
            print("\t===> Loaded Checkpoint '{}' (epoch {})".format(resume, checkpoint['epoch']))
        else:
            raise FileNotFoundError("\t====> no checkpoint found at '{}'".format(resume))

    start_time = timer()

    writer = SummaryWriter()
    for epoch in tqdm(range(start_epoch, epochs), desc="Epochs"):

        # Training
        train_loss, train_acc = train(model, train_loader, criterion, optimizer, use_cuda)
        train_losses.append(train_loss)
        train_accuracies.append(train_acc)

        val_loss, val_acc = evaluate(model, val_loader, criterion, use_cuda)
        val_losses.append(val_loss)
        val_accuracies.append(val_acc)

        print("train", train_loss, train_acc)
        print("val", val_loss, val_acc)
        # print("criterion", criterion)

        writer.add_scalar('train_loss', train_loss, epoch)
        writer.add_scalar('train_acc', train_acc, epoch)
        writer.add_scalar('validation_loss', val_loss, epoch)
        writer.add_scalar('validation_acc', val_acc, epoch)
        # writer.add_scalar('learning_rate', lr, epoch)

        is_best = val_loss < best_val_loss
        # is_best = val_acc > best_val_acc
        if is_best:
            best_val_epoch = epoch
            best_val_loss = val_loss
            best_val_acc = val_acc
            print("***IS BEST***")
            with open(os.path.join(save_path, 'train_result.txt'), 'w') as f:
                f.write('Best Validation Epoch: {}\n'.format(epoch))
                f.write('Train Loss: {}\n'.format(train_loss))
                f.write('Train Accuracy: {}\n'.format(train_acc))
                f.write('Validation Loss: {}\n'.format(val_loss))
                f.write('Validation Accuracy: {}\n'.format(val_acc))

            torch.save(model, os.path.join(save_path, 'entire_model.pth'))

        save_checkpoint({
            'epoch': epoch,
            'arch': str(model.__class__.__name__),
            'state_dict': model.state_dict(),
            'best_epoch': best_val_epoch,
            'best_valid_loss': best_val_loss,
            'best_valid_accuracy': best_val_acc,
            'optimizer': optimizer.state_dict(),
            # 'scheduler': scheduler.state_dict(),
        }, is_best, filename=os.path.join(save_path, 'checkpoint.pth.tar'))

        loss_curve, acc_curve = plot_learning_curves(train_losses, val_losses, train_accuracies, val_accuracies)
        loss_curve.savefig(os.path.join(save_path, "loss.eps"), format='eps', bbox_inches='tight')
        acc_curve.savefig(os.path.join(save_path, "acc.eps"), format='eps', bbox_inches='tight')
        plt.close(loss_curve)
        plt.close(acc_curve)

    end_time = timer()
    print("\nDone! - Elapsed Time: {} minutes".format((end_time - start_time) / 60))
    writer.export_scalars_to_json("./all_scalars.json")
    writer.close()

def execute_service(in_data_dir, index_file, matrix_img_file, graph_data_file, histogram_data_file):

    # For demo purposes, just copy precomputed output to the run directory
    model = matrix_img_file.partition('_')[0]
    if model == "0":
        print("ml_nn_pipeline")
        precomp_matrix_img_path = 'ml_outputs/ml1_viz_-2.png'
        precomp_graph_data_path = 'ml_outputs/ml1_viz_-2_new.csv'
        precomp_hist_data_path = 'ml_outputs/ml1_viz_-2.json'
    elif model == "1":
        print("ml_bcnn_pipeline")
        precomp_matrix_img_path = 'ml_outputs/ml2_viz_-2.png'
        precomp_graph_data_path = 'ml_outputs/ml2_viz_-2_new.csv'
        precomp_hist_data_path = 'ml_outputs/ml2_viz_-2.json'
    elif model == "2":
        print("ml_fmnn_pipeline")
        precomp_matrix_img_path = 'ml_outputs/ml3_viz_-2.png'
        precomp_graph_data_path = 'ml_outputs/ml3_viz_-2_new.csv'
        precomp_hist_data_path = 'ml_outputs/ml3_viz_-2.json'
    else:
        print("ml_bcfmnn_pipeline")
        precomp_matrix_img_path = 'ml_outputs/viz_-2.png'
        precomp_graph_data_path = 'ml_outputs/viz_-2_new.csv'
        precomp_hist_data_path = 'ml_outputs/viz_-2.json'
    copyfile('./Data/' + precomp_matrix_img_path, './Data/' + matrix_img_file)
    copyfile('./Data/' + precomp_graph_data_path, './Data/' + graph_data_file)
    copyfile('./Data/' + precomp_hist_data_path, './Data/' + histogram_data_file)
    return

    run_dir, _, _ = out_path.partition('/')
    run_nn(in_data_dir, index_file, out_path, run_dir)

if __name__ == '__main__':
    torch.multiprocessing.freeze_support()

    if (sys.argv[1].endswith('.pkl')):
        execute_service(sys.argv[2], sys.argv[1], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        execute_service(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])