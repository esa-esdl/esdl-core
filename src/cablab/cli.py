import sys
import argparse

import cablab


def main(args=None):
    if not args:
        args = sys.argv[0:]

    parser = argparse.ArgumentParser(description='Generates a new CAB-LAB data cube or updates an existing one')
    parser.add_argument('-l', '--list', help="lists all available data cube source providers", action="store_true")
    parser.add_argument('-c', '--cube_conf', metavar='CONFIG', help="data cube configuration file")
    parser.add_argument('cube_dir', metavar='TARGET', help="data cube root directory")
    parser.add_argument('sources', metavar='SOURCE', type=str, nargs='*', help='<provider name>:<source directory>, use -l to list provider names')
    args_obj = parser.parse_args(args)
    if args_obj.list:
        print('source data providers (%d):' % len(cablab.IMAGE_PROVIDERS))
        for name in cablab.IMAGE_PROVIDERS.keys():
            print('  %s' % name)


if __name__ == "__main__":
    main()
