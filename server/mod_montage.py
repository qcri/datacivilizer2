import matlab.engine
import sys
import time
from utils.dc import DCMetric, DC
from utils.mod_util import transform_to_tensor

print("Starting matlab engine")
start = time.time()

eng = matlab.engine.start_matlab()

end = time.time()
print("Execution time: " + str(end - start))

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

    # TODO: get args from JSON
    num_channels.setValue(eng.mod_montage(in_path, out_path, montage_type, nargout=1))

    file_in = "./Data/" + out_path + ".txt"
    file_out = "./Data/"+ viz_out_path
    transform_to_tensor(file_in, file_out, 200)

print("Executing function")
start = time.time()

execute_service(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

end = time.time()
print("Execution time: " + str(end - start))

DC.end(sys.argv[-1])