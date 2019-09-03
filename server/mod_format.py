import sys
import time
import matlab.engine
from shutil import copyfile
from utils.dc import DCMetric, DC, BpOps
from utils.mod_util import transform_to_tensor

# Example of custom operator used for a breakpoint
# def customOp(metric, constant1, constant2):
#     val = metric.getValue()
#     return constant1 < val and constant2 > val

def execute_service(in_path, out_path, viz_out_path):

    model = out_path.partition('_')[0]
    out_file = out_path.partition('/')[2]
    viz_out_file = viz_out_path.partition('/')[2]
    eeg_good_folder = "eeg_good_outputs"
    eeg_bad_folder = "eeg_bad_outputs"
    if model == "4":
        print("eeg_good_pipeline")
        copyfile('./Data/' + eeg_good_folder + '/' + out_file, './Data/' + out_path)
        copyfile('./Data/' + eeg_good_folder + '/' + viz_out_file, './Data/' + viz_out_path)
        time.sleep(3)
        return
    elif model == "5":
        print("eeg_bad_pipeline")
        copyfile('./Data/' + eeg_bad_folder + '/' + out_file, './Data/' + out_path)
        copyfile('./Data/' + eeg_bad_folder + '/' + viz_out_file, './Data/' + viz_out_path)
        time.sleep(3)
        return

    eng = matlab.engine.start_matlab()
    eng.mod_format(in_path, out_path, nargout=0)
    eng.quit()

    file_in = "./Data/" + out_path + ".txt"
    file_out = "./Data/"+ viz_out_path
    transform_to_tensor(file_in, file_out, 200)

    # Example of how to use add metrics
    # f1_metric = DCMetric("source_metric_1")
    # f2_metric = DCMetric("source_metric_2")
    # f1_metric.setValue(1.6)
    # f2_metric.setValue(1.3)
    # DC.register_metric(f1_metric)
    # DC.register_metric(f2_metric)
    # DC.register_breakpoint('<', f1_metric, 1)
    # DC.register_breakpoint(BpOps.always_ge, f2_metric, 0)
    # DC.register_breakpoint(customOp, f1_metric, 1, 2)

execute_service(sys.argv[1], sys.argv[2], sys.argv[3])

# Use this if metrics and/or breakpoints were added
# DC.end(sys.argv[-1])