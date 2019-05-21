import matlab.engine
import sys

eng = matlab.engine.start_matlab()


def execute_service(in_path, out_path):

	# TODO: get args from JSON
	eng.mod_computeFeatures(in_path, out_path, nargout=0)


execute_service(sys.argv[1], sys.argv[2])
