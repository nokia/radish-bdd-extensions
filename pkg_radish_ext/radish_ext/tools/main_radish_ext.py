# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import os
import sys

from radish.main import main as radish_main

from radish_ext.sdk.l import Logging

log = Logging.get_logger(os.path.basename(__file__))


def main(*argv):
    if argv is not None:
        sys.argv += argv
    parser = argparse.ArgumentParser("Radish csfpy main method wrapper", add_help=False)
    parser.add_argument('--help', '-h', default=False, action='store_true', dest='help')
    main_wrapper_args, radish_args = parser.parse_known_args(sys.argv)
    args = radish_args[1:]
    if main_wrapper_args.help:
        parser.print_help()
        return radish_main()
    log.debug(args)
    return radish_main(args)


# Execute this file to get radish
if __name__ == "__main__":
    sys.exit(main())
