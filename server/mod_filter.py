import matlab.engine
import sys
from utils.dc import DCMetric, DC, BpOps
from utils.mod_util import transform_to_tensor
import time

print("Starting matlab engine")
start = time.time()

eng = matlab.engine.start_matlab()

end = time.time()
print("Execution time: " + str(end - start))

def execute_service(in_path, out_path, notch_freq=60.0, high_pass_freq=0.5, low_pass_freq=40.0):

    # TODO: get args from JSON
    eng.mod_filter(in_path, out_path, notch_freq, high_pass_freq, low_pass_freq, nargout=0)

    # Example of how to use add metrics
    f1_metric = DCMetric("filter_metric_1")
    f2_metric = DCMetric("filter_metric_2")
    f1_metric.setValue(0.6)
    f2_metric.setValue(0.3)
    DC.register_metric(f1_metric)
    DC.register_metric(f2_metric)
    DC.register_breakpoint('>', f1_metric, 1)
    DC.register_breakpoint(BpOps.always_ge, f2_metric, 0)

print("Executing function")
start = time.time()

execute_service(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))

end = time.time()
print("Execution time: " + str(end - start))

print("Do rest")
start = time.time()

# Use this if metrics and/or breakpoints were added
DC.end(sys.argv[-1])

# TODO: get visualization data
file_in = "./Data/" + sys.argv[2] + ".txt"
file_out = "./Data/"+ sys.argv[2].split(".mat")[0] +".json"

transform_to_tensor(file_in, file_out, 1000, 1020)

end = time.time()
print("Execution time: " + str(end - start))
