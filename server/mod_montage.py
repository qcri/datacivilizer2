import matlab.engine
import sys
from utils.mod_util import transform_to_tensor

eng = matlab.engine.start_matlab()


def execute_service(in_path, out_path, montage_type="monopolar"):

    # TODO: get args from JSON
    eng.mod_montage(in_path, out_path, montage_type, nargout=0)


execute_service(sys.argv[1], sys.argv[2], sys.argv[3])

file_in = "./Data/" + sys.argv[2] + ".txt"
file_out = "./Data/"+ sys.argv[2].split(".mat")[0] +".json"

transform_to_tensor(file_in, file_out, 1000, 1020)