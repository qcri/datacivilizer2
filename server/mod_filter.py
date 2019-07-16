import matlab.engine
import sys
from dcmetric import DCMetric, DC

from mod_util import transform_to_tensor
eng = matlab.engine.start_matlab()

def execute_service(in_path, out_path):

    # TODO: get args from JSON
    eng.mod_filter(in_path, out_path, nargout=0)

    # Example of how to use add metrics
    # f1_metric = DCMetric("f1_score")
    # f1_metric.setValue(3000)
    # DC.register_metric(f1_metric)

execute_service(sys.argv[1], sys.argv[2])
# Use this if metrics were added
# DC.save_metrics(sys.argv[-1])

file_in = "./Data/" + sys.argv[2] + ".txt"
file_out = "./Data/"+ sys.argv[2].split(".mat")[0] +".json"

transform_to_tensor(file_in, file_out, 1000, 1020)