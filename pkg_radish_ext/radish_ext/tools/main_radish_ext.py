# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import os
import sys

from radish.main import main as radish_main
from radish_ext.radish.stub_generator import not_implemented_steps_stub_generator

from radish_ext.sdk.l import Logging

log = Logging.get_logger(os.path.basename(__file__))


def main_radish_ext(*argv):
    if argv is not None:
        sys.argv += argv
    parser = argparse.ArgumentParser("""Radish ext main method wrapper
    
    There are special user data arguments handled for configuration read
    --user-data=cfg=config_file.yaml
        Configuration file:
            * full path to config file or located in package etc dir
    --user-data=package=radish_selenium
        python package name to look for configuration etc dir 
    """, add_help=False)
    parser.add_argument('--generate-steps-file', default=None, dest='generate_stub_path',
                        help='generate steps file with not implemented steps stub')
    main_wrapper_args, radish_args = parser.parse_known_args(sys.argv)

    log.info('main_arguments: {0}\nradish arguments {1}'.format(main_wrapper_args, radish_args))

    parser.add_argument('--help', '-h', default=False, action='store_true', dest='help')
    main_wrapper_args, radish_args = parser.parse_known_args(sys.argv)
    args = radish_args[1:]

    if main_wrapper_args.generate_stub_path is not None:
        log.debug(f"Genreate steps to file: {main_wrapper_args.generate_stub_path}")
        not_implemented_steps_stub_generator(main_wrapper_args.generate_stub_path)
    if main_wrapper_args.help:
        parser.print_help()
        return radish_main()
    log.debug(args)
    return radish_main(args)


# Execute this file to get radish
if __name__ == "__main__":
    sys.exit(main_radish_ext())
