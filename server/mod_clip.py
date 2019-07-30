import matlab.engine
import sys
from utils.mod_util import transform_to_tensor
import time

print("Starting matlab engine")
start = time.time()

eng = matlab.engine.start_matlab()

end = time.time()
print("Execution time: " + str(end - start))

def execute_service(in_path, out_path):

	# TODO: get args from JSON
	eng.mod_clip(in_path, out_path, nargout=0)

print("Executing function")
start = time.time()

execute_service(sys.argv[1], sys.argv[2])

end = time.time()
print("Execution time: " + str(end - start))

print("Do rest")
start = time.time()

file_in = "./Data/" + sys.argv[2] + ".txt"
file_out = "./Data/"+ sys.argv[2].split(".mat")[0] +".json"

transform_to_tensor(file_in, file_out, 1000, 1020)

end = time.time()
print("Execution time: " + str(end - start))