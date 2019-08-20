import sys
import time
import matlab.engine
from shutil import copyfile
from utils.dc import DCMetric, DC
from utils.mod_util import transform_to_tensor

def checkChannels(metric, montage_type):
    val = metric.getValue()
    if montage_type == "monopolar" or montage_type == "common_avg_ref" or montage_type == "car":
        return val == 19
    elif montage_type == "L-bipolar":
        return val == 18
    return False

def execute_service(in_path, out_path, viz_out_path, montage_type="monopolar"):

    num_channels = DCMetric("num_out_channels")
    DC.register_metric(num_channels)
    DC.register_breakpoint(checkChannels, num_channels, montage_type)

    model = out_path.partition('_')[0]
    out_file = out_path.partition('/')[2]
    viz_out_file = viz_out_path.partition('/')[2]
    eeg_good_folder = "eeg_good_outputs"
    if model == "1":
        print("eeg_good_pipeline")
        num_channels.setValue(19);
        copyfile('./Data/' + eeg_good_folder + '/' + out_file, './Data/' + out_path)
        copyfile('./Data/' + eeg_good_folder + '/' + viz_out_file, './Data/' + viz_out_path)
        return

    eng = matlab.engine.start_matlab()
    num_channels.setValue(eng.mod_montage(in_path, out_path, montage_type, nargout=1))
    eng.quit()

    file_in = "./Data/" + out_path + ".txt"
    file_out = "./Data/"+ viz_out_path
    transform_to_tensor(file_in, file_out, 200)

execute_service(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

DC.end(sys.argv[-1])