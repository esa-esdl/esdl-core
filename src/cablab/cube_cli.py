import argparse
import os
import sys

import cablab
from cablab import Cube, CubeConfig
from cablab.util import Config

__VERSION__ = '0.1'


def main(args=None):
    if not args:
        args = sys.argv[1:]

    print('CAB-LAB command-line interface, version %s' % __VERSION__)

    #
    # Configure and run argument parser
    #
    parser = argparse.ArgumentParser(description='Generates a new CAB-LAB data cube or updates an existing one.')
    parser.add_argument('-l', '--list', action='store_true',
                        help="list all available source providers")
    parser.add_argument('-c', '--cube-conf', metavar='CONFIG',
                        help="data cube configuration file")
    parser.add_argument('cube_dir', metavar='TARGET', nargs='?',
                        help="data cube root directory")
    parser.add_argument('cube_sources', metavar='SOURCE', nargs='*',
                        help='<provider name>:<directory>, use -l to list source provider names')
    args_obj = parser.parse_args(args)

    #
    # Validate and process arguments
    #
    is_new = False
    cube_dir = args_obj.cube_dir
    cube_config_file = args_obj.cube_conf
    cube_sources = args_obj.cube_sources
    source_provider_infos = []
    list_mode = args_obj.list
    if cube_config_file and not os.path.isfile(cube_config_file):
        parser.error('CONFIG file not found: %s' % cube_config_file)
    if not cube_dir and (cube_config_file or cube_sources):
        parser.error('TARGET directory must be provided')
    if cube_dir:
        is_new = not os.path.exists(cube_dir) or not os.listdir(cube_dir)
        if not is_new and cube_config_file:
            parser.error('TARGET directory must be empty')
        for source in cube_sources:
            source_provider_name, source_args = source.split(':', maxsplit=1)
            source_provider_class = cablab.SOURCE_PROVIDERS.get(source_provider_name)
            if not os.path.isabs(source_args):
                source_args = Config.instance().get_cube_source_path(source_args)
            if source_provider_class:
                source_provider_infos.append((source_provider_name, source_provider_class, source_args))
            else:
                parser.error('no source provider installed with name \'%s\'' % source_provider_name)

    #
    # Run tool
    #
    if not list_mode and not cube_dir:
        parser.print_usage()
        sys.exit(1)

    if list_mode:
        print('source data providers (%d):' % len(source_provider_infos))
        for source_provider_info in source_provider_infos:
            print('  %s --> %s(%s)' % source_provider_info)
    if cube_dir:
        if is_new:
            if cube_config_file:
                cube_config = CubeConfig.load(cube_config_file)
            else:
                cube_config = CubeConfig()
            cube = Cube.create(cube_dir, cube_config)
        else:
            cube = Cube.open(cube_dir)

        source_providers = [cls(cube.config, name, args) for name, cls, args in source_provider_infos]

        for source_provider in source_providers:
            cube.update(source_provider)


if __name__ == "__main__":
    main()
