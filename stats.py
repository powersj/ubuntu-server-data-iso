#!/usr/bin/env python3
"""
Produces a manifest of a given ISO.
"""
import argparse
import glob
import hashlib
import os
import logging
import sys
from util import human_size, extract, cleanup


def get_folder_size(path):
    """
    Recursivly find a folder size.
    """
    if not os.path.exists(path):
        return 0

    total = 0

    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir() and not os.path.islink(entry.path):
            total += get_folder_size(entry.path)

    return total


def stats_iso(filename, folder):
    """
    Overall statistics of the ISO file itself.
    """
    media_info = os.path.join(folder, '.disk/info')
    logging.info(' '.join(open(media_info, "r").read().split()))
    md5 = hashlib.md5(open(filename, 'rb').read()).hexdigest()
    logging.info('%s (%s)' % (os.path.basename(filename), md5))


def stats_dirs(iso):
    """
    Overall statistics of the ISO file itself.
    """
    logging.info('---')
    dirs = ['.', 'boot', 'dists', 'doc', 'EFI', 'install',
            'isolinux', 'pics', 'preseed', 'pool']

    for folder in dirs:
        path = os.path.join(iso, folder)
        logging.info('%-10s [%4s MB]' % (folder, human_size(get_folder_size(path))))


def stats_pool(pool):
    """
    Produce pool directory statistics.
    """
    if not os.path.exists(pool):
        logging.critical('Pool folder does not exist at: %s', pool)
        sys.exit(1)

    logging.info('---')
    logging.info('Files in pool [%4s]', sum(os.path.isfile(f) for f in
                           glob.glob('%s/**/*' % pool, recursive=True)))
    logging.info('Total .deb    [%4s]', len(glob.glob('%s/**/*.deb' % pool, recursive=True)))
    logging.info('Total .udeb   [%4s]', len(glob.glob('%s/**/*.udeb' % pool, recursive=True)))


def stats_squashfs(squashfs):
    """
    Produce squashfs statistics.
    """
    try:
        size_file = os.path.join(squashfs, 'filesystem.size')
        size = human_size(int(''.join(open(size_file, "r").read().split())))
    except FileNotFoundError:
        size = 0

    logging.info('livefs     [%4s MB]' % size)


def main(filename, debug=False):
    """
    Information about a particular ISO.
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.basicConfig(stream=sys.stdout, format='%(message)s',
                        level=log_level)

    folder = extract(filename)

    logging.info('ISO Stats')
    stats_iso(filename, folder)
    stats_dirs(folder)
    stats_squashfs(os.path.join(folder, 'install'))
    stats_pool(os.path.join(folder, 'pool'))

    logging.info('')

    cleanup(folder)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('filename', help='ISO file to manifest')
    PARSER.add_argument('-d', '--debug', action='store_true',
                        help='debug output')
    ARGS = PARSER.parse_args()

    main(ARGS.filename, ARGS.debug)
