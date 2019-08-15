import matlab.engine
import sys
import time
from utils.dc import DCMetric, DC, BpOps
from utils.mod_util import transform_to_tensor

print("Starting matlab engine")
start = time.time()

eng = matlab.engine.start_matlab()

end = time.time()
print("Execution time: " + str(end - start))

MIN_SAMPLE_FREQ = 100

def execute_service(in_path, out_path, viz_out_path, resample_freq=200):

    fs = DCMetric("sampling rate")
    DC.register_metric(fs)
    DC.register_breakpoint(BpOps.always_ge, fs, MIN_SAMPLE_FREQ)

    fs_before, fs_after = eng.mod_resample(in_path, out_path, resample_freq, nargout=2)
    fs.setValues([fs_before, fs_after])

    file_in = "./Data/" + out_path + ".txt"
    file_out = "./Data/"+ viz_out_path
    transform_to_tensor(file_in, file_out, 200)

print("Executing function")
start = time.time()

execute_service(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]))


end = time.time()
print("Execution time: " + str(end - start))

DC.end(sys.argv[-1])