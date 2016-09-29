#!/usr/bin/env python3
"""
Produces a manifest of a given ISO.
"""
import argparse
import glob
import os
import logging
import sys
from util import cleanup, extract, human_size


def manifest(target):
    """
    Produces a manifest of the target dir.
    """
    files = []
    for file in glob.glob(target, recursive=True):
        if os.path.isfile(file):
            name = os.path.basename(file).split('_')[0]
            version = os.path.basename(file).split('_')[1]
            size = human_size(os.path.getsize(file))
            files.append((name, version, size))

    for file in sorted(files):
        logging.info('%s,%s,%s' % (file[0], file[1], file[2]))


def main(filename, udeb=False, debug=False):
    """
    Information about a particular ISO.
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.basicConfig(stream=sys.stdout, format='%(message)s',
                        level=log_level)

    folder = extract(filename)
    extension = 'udeb' if udeb else 'deb'
    manifest('%s/**/*.%s' % (os.path.join(folder, 'pool'), extension))

    cleanup(folder)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('filename', help='ISO file to manifest')
    PARSER.add_argument('-d', '--debug', action='store_true',
                        help='debug output')
    PARSER.add_argument('-u', '--udeb', action='store_true',
                        help='search for udebs instead')
    ARGS = PARSER.parse_args()

    main(ARGS.filename, ARGS.udeb, ARGS.debug)
