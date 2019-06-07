import argparse
import os
import sys

from pkg_resources import iter_entry_points

from .version import version as __version__
from .cube import Cube
from .cube_config import CubeConfig
from .cube_provider import CubeSourceProvider


def _load_source_providers():
    source_provider_classes = dict()
    for entry_point in iter_entry_points(group='esdl.source_providers', name=None):
        source_provider_class = entry_point.load()
        if issubclass(source_provider_class, CubeSourceProvider):
            source_provider_classes[entry_point.name] = source_provider_class
        else:
            print('warning: esdl.source_providers: requires a \'%s\' but got a \'%s\'' % (
                CubeSourceProvider, type(source_provider_class)))
    return source_provider_classes


SOURCE_PROVIDERS = _load_source_providers()


def _parse_source_arg(source: str):
    from collections import OrderedDict
    parts = source.split(os.pathsep)
    name = parts[0]
    if not name:
        return name, None, None, 'SOURCE name must not be empty'
    args = list()
    kwargs = OrderedDict()
    error_msg = None
    for p in parts[1:]:
        kv = p.split('=', maxsplit=1)
        if len(kv) == 2:
            k, v = kv
            if not k:
                error_msg = 'empty keyword in SOURCE'
                break
            kwargs[k] = v
        elif len(kv) == 1:
            args.append(kv)
        else:
            error_msg = 'illegal empty SOURCE'
            break
    return name, args, kwargs, error_msg


def main(args=None):
    if not args:
        args = sys.argv[1:]

    print('ESDL command-line interface, version %s' % __version__)

    """
    Configure and run argument parser

    More arguments can also be added to the SOURCE parameter. Existing arguments:
      - dir                   : to specify the source directory (required)
      - var                   : to specify the desired variable name (for gleam and mpibgc providers)
      - resampling_order      : to specify the re-sampling order (space_first or time_first).
                                The default is time_first.
        # Usage examples:
    cube-gen "esdc-31d-1deg-1x180x360-1.0.1_1" "burnt_area:dir=data-source/BurntArea"
    cube-gen "esdc-31d-1deg-1x180x360-1.0.1_1" "evaporative_stress:dir=data-source/evaporative_stress:var=S"
    cube-gen "esdc-31d-1deg-1x180x360-1.0.1_1" "soil_moisture:dir=data-source/ECV_sm:resampling_order=space_first"
    """
    parser = argparse.ArgumentParser(
        description='Generates a new ESDL data cube or updates an existing one.')
    parser.add_argument('-l', '--list', action='store_true',
                        help="list all available source providers")
    parser.add_argument('-G', '--dont-clear-cache', action='store_true',
                        help="do not clear data cache before updating the cube (faster)")
    parser.add_argument('-c', '--cube-conf', metavar='CONFIG',
                        help="data cube configuration file")
    parser.add_argument('cube_dir', metavar='TARGET', nargs='?',
                        help="data cube root directory")
    parser.add_argument('cube_sources', metavar='SOURCE', nargs='*',
                        help='<provider name>:dir=<directory>, use -l to list source provider names')
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
            source_name, source_args, source_kwargs, source_error_msg = _parse_source_arg(source)
            if source_error_msg:
                parser.error(source_error_msg)
            source_class = SOURCE_PROVIDERS.get(source_name)
            if source_class:
                source_provider_infos.append(
                    (source_name, source_class, source_args, source_kwargs))
            else:
                parser.error("no source provider installed with name '%s'" % source_name)

    #
    # Run tool
    #
    if not list_mode and not cube_dir:
        parser.print_usage()
        sys.exit(1)

    if list_mode:
        print('source data providers (%d):' % len(SOURCE_PROVIDERS))
        for source_name, value in SOURCE_PROVIDERS.items():
            print('  %s -> %s.%s' % (source_name, value.__module__, value.__name__))
    if cube_dir:
        if is_new:
            if cube_config_file:
                cube_config = CubeConfig.load(cube_config_file)
            else:
                cube_config = CubeConfig()
            cube = Cube.create(cube_dir, cube_config)
        else:
            cube = Cube.open(cube_dir)

        source_providers = [cls(cube.config, *args, name=name, **kwargs)
                            for name, cls, args, kwargs in source_provider_infos]

        for source_provider in source_providers:
            cube.update(source_provider)


if __name__ == "__main__":
    main()
