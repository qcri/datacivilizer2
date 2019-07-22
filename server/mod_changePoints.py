import matlab.engine
import sys

eng = matlab.engine.start_matlab()


def execute_service(in_path, out_path, thr=0.5):

	# TODO: get args from JSON
	eng.mod_changePoints(in_path, out_path, thr, nargout=0)


execute_service(sys.argv[1], sys.argv[2], float(sys.argv[3]))
