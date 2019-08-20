import sys
import time
import matlab.engine
from shutil import copyfile
from utils.mod_util import transform_to_tensor

def execute_service(in_path, out_path, viz_out_path):

    model = out_path.partition('_')[0]
    out_file = out_path.partition('/')[2]
    viz_out_file = viz_out_path.partition('/')[2]
    eeg_good_folder = "eeg_good_outputs"
    if model == "1":
        print("eeg_good_pipeline")
        copyfile('./Data/' + eeg_good_folder + '/' + out_file, './Data/' + out_path)
        copyfile('./Data/' + eeg_good_folder + '/' + viz_out_file, './Data/' + viz_out_path)
        return

    eng = matlab.engine.start_matlab()
    eng.mod_clip(in_path, out_path, nargout=0)
    eng.quit()

    file_in = "./Data/" + out_path + ".txt"
    file_out = "./Data/"+ viz_out_path
    transform_to_tensor(file_in, file_out, 200)

execute_service(sys.argv[1], sys.argv[2], sys.argv[3])