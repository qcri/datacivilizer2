import matlab.engine
import time
import sys
from utils.dc import DCMetric, DC
from utils.mod_util import transform_to_tensor

print("Starting matlab engine")
start = time.time()

eng = matlab.engine.start_matlab()

end = time.time()
print("Execution time: " + str(end - start))

# def customOp(metric, constant1, constant2):
#     val = metric.getValue()
#     return constant1 < val and constant2 > val

def execute_service(in_path, out_path, viz_out_path):

    eng.mod_format(in_path, out_path, nargout=0)

    file_in = "./Data/" + out_path + ".txt"
    file_out = "./Data/"+ viz_out_path
    transform_to_tensor(file_in, file_out, 200)

    # f1_metric = DCMetric("source_metric_1")
    # f2_metric = DCMetric("source_metric_2")
    # f1_metric.setValue(1.6)
    # f2_metric.setValue(1.3)
    # DC.register_metric(f1_metric)
    # DC.register_metric(f2_metric)
    # DC.register_breakpoint(customOp, f1_metric, 1, 2)


print("Executing function")
start = time.time()

execute_service(sys.argv[1], sys.argv[2], sys.argv[3])

end = time.time()
print("Execution time: " + str(end - start))

# DC.end(sys.argv[-1])