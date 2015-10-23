import sys

import cablab


def main(args=None):
    if not args:
        args = sys.argv[1:]
    print(">> Welcome to the CAB-LAB CLI! <<")
    print("args =", args)
    # Do argument parsing here (eg. with argparse) and anything else
    # you want your project to do.

    print('IMAGE_PROVIDERS =', cablab.IMAGE_PROVIDERS)


# check if I'm invoked as script
if __name__ == "__main__":
    main()
