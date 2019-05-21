import matlab.engine
import sys

eng = matlab.engine.start_matlab()


def execute_service(in_path, out_path):

	# TODO: get args from JSON
	eng.mod_spectrogram(in_path, out_path, nargout=0)


execute_service(sys.argv[1], sys.argv[2])
