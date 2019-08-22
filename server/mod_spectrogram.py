import sys
import matlab.engine
from shutil import copyfile

eng = matlab.engine.start_matlab()


def execute_service(in_path, out_path, viz_out_path, nw=2):

    model = out_path.partition('_')[0]
    out_file = out_path.partition('/')[2]
    viz_out_file = viz_out_path.partition('/')[2]
    if model == "7":
        print("spectrogram")
        copyfile('./Data/spectrogram_outputs/' + out_file, './Data/' + out_path)
        copyfile('./Data/spectrogram_outputs/' + viz_out_file, './Data/' + viz_out_path)
        return

    # TODO: get args from JSON
    eng.mod_spectrogram(in_path, out_path, viz_out_path, nw, nargout=0)

execute_service(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]))
