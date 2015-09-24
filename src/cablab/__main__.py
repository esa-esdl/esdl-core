import sys


def main(args=None):
    if not args:
        args = sys.argv[1:]
    print(">> Welcome to the CAB-CLI CLI! <<")
    print("args =", args)
    # Do argument parsing here (eg. with argparse) and anything else
    # you want your project to do.
    import cablab


if __name__ == "__main__":
    main()
