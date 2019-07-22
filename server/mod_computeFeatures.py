import matlab.engine
import sys

eng = matlab.engine.start_matlab()


def execute_service(in_path_1, in_path_2, out_path, delta_low, delta_high, theta_low, theta_high, alpha_low, alpha_high, beta_low, beta_high):

	# TODO: get args from JSON
	eng.mod_computeFeatures(in_path_1, in_path_2, out_path, delta_low, delta_high, theta_low, theta_high, alpha_low, alpha_high, beta_low, beta_high, nargout=0)


execute_service(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7]), float(sys.argv[8]), float(sys.argv[9]), float(sys.argv[10]), float(sys.argv[11]))
