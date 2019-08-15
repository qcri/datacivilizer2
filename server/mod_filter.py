import matlab.engine
import sys
import time
from utils.mod_util import transform_to_tensor

print("Starting matlab engine")
start = time.time()

eng = matlab.engine.start_matlab()

end = time.time()
print("Execution time: " + str(end - start))

def execute_service(in_path, out_path, viz_out_path, notch_freq=60.0, high_pass_freq=0.5, low_pass_freq=40.0):

    # TODO: get args from JSON
    eng.mod_filter(in_path, out_path, notch_freq, high_pass_freq, low_pass_freq, nargout=0)

    file_in = "./Data/" + out_path + ".txt"
    file_out = "./Data/"+ viz_out_path
    transform_to_tensor(file_in, file_out, 200)

print("Executing function")
start = time.time()

execute_service(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]))

end = time.time()
print("Execution time: " + str(end - start))