import matlab.engine
import sys

eng = matlab.engine.start_matlab()


def execute_service(in_path, out_path, viz_out_path, nw=2):

    # TODO: get args from JSON
    eng.mod_spectrogram(in_path, out_path, viz_out_path, nw, nargout=0)

execute_service(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]))
