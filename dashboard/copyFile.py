import sys
from shutil import copyfile

def main(in_file, out_file):
    print("Copying " + in_file + " to " + out_file)
    copyfile(in_file, out_file)
    print("Copy complete")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])