import matlab.engine
import sys
from utils.mod_util import transform_to_tensor

eng = matlab.engine.start_matlab()


def execute_service(in_path, out_path, resample_freq=200):

    # TODO: get args from JSON
    eng.mod_resample(in_path, out_path, resample_freq, nargout=0)


execute_service(sys.argv[1], sys.argv[2], float(sys.argv[3]))


file_in = "./Data/" + sys.argv[2] + ".txt"
file_out = "./Data/"+ sys.argv[2].split(".mat")[0] +".json"

transform_to_tensor(file_in, file_out, 1000, 1020)