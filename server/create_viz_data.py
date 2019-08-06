from utils.mod_util import transform_to_tensor

def main():
    transform_to_tensor('./Data/0_2/out_-1_100.mat.txt', './Data/out_-1.json', 0, 1687)

if __name__ == "__main__":
    main()