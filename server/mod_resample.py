import sys
import time
import matlab.engine
from shutil import copyfile
from utils.dc import DCMetric, DC, BpOps
from utils.mod_util import transform_to_tensor

MIN_SAMPLE_FREQ = 100

def execute_service(in_path, out_path, viz_out_path, resample_freq=200):

    fs = DCMetric("sampling rate")
    DC.register_metric(fs)
    DC.register_breakpoint(BpOps.always_ge, fs, MIN_SAMPLE_FREQ)

    model = out_path.partition('_')[0]
    out_file = out_path.partition('/')[2]
    viz_out_file = viz_out_path.partition('/')[2]
    eeg_good_folder = "eeg_good_outputs"
    eeg_bad_folder = "eeg_bad_outputs"
    if model == "1":
        print("eeg_good_pipeline")
        fs.setValues([200, 200])
        copyfile('./Data/' + eeg_good_folder + '/' + out_file, './Data/' + out_path)
        copyfile('./Data/' + eeg_good_folder + '/' + viz_out_file, './Data/' + viz_out_path)
        time.sleep(3)
        return
    elif model == "2":
        print("eeg_bad_pipeline")
        fs.setValues([200, 50])
        copyfile('./Data/' + eeg_bad_folder + '/' + out_file, './Data/' + out_path)
        copyfile('./Data/' + eeg_bad_folder + '/' + viz_out_file, './Data/' + viz_out_path)
        time.sleep(3)
        return

    eng = matlab.engine.start_matlab()
    fs_before, fs_after = eng.mod_resample(in_path, out_path, resample_freq, nargout=2)
    eng.quit()
    fs.setValues([fs_before, fs_after])

    file_in = "./Data/" + out_path + ".txt"
    file_out = "./Data/"+ viz_out_path
    transform_to_tensor(file_in, file_out, 200)

execute_service(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]))

DC.end(sys.argv[-1])