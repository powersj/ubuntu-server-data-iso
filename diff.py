#!/usr/bin/env python3
"""
Diff two ISO pool manifest files.
"""
import argparse
import csv
import logging
import sys


def read_manifest(filename):
    """
    Reads in the manifest into a dictionary of package
    with version and size keys.
    """
    packages = {}
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            packages[row[0]] = {}
            packages[row[0]]['version'] = row[1]
            packages[row[0]]['size'] = int(row[2])

    return packages


def find_pkg_added(new, added):
    """
    Prints all added packages with version and size.
    """
    logging.info('Added')
    logging.info('---')
    for pkg in sorted(added):
        logging.info('[%+3i] %-40s %40s', new[pkg]['size'],
                     pkg, new[pkg]['version'])
    logging.info('')


def find_pkg_removed(old, removed):
    """
    Prints all removed packages with version and size.
    """
    logging.info('Removed')
    logging.info('---')
    for pkg in sorted(removed):
        logging.info('[%+3i] %-40s %40s', 0 - old[pkg]['size'],
                     pkg, old[pkg]['version'])

    logging.info('')


def find_pkg_updated(old, new, common):
    """
    Prints all updated packages with version and size.
    """
    logging.info('Updated')
    logging.info('---')
    for pkg in sorted(common):
        if old[pkg]['version'] != new[pkg]['version']:
            logging.info('[%+3i] %-40s %40s %40s',
                         (new[pkg]['size'] - old[pkg]['size']),
                         pkg, old[pkg]['version'], new[pkg]['version'])
    logging.info('')


def set_math(old_iso, new_iso):
    """
    Given the keys determines what has changed.
    """
    old = old_iso.keys()
    new = new_iso.keys()

    common = old & new
    removed = old - new
    added = new - old

    added_size = 0
    for pkg in added:
        added_size += new_iso[pkg]['size']

    removed_size = 0
    for pkg in removed:
        removed_size -= old_iso[pkg]['size']

    updated = 0
    updated_size = 0
    for pkg in common:
        if new_iso[pkg]['version'] != old_iso[pkg]['version']:
            updated += 1
            updated_size += (new_iso[pkg]['size'] - old_iso[pkg]['size'])

    logging.info('Overall Stats')
    logging.info('---')
    logging.info('Total Old:   %4s', len(old))
    logging.info('Total New:   %4s', len(new))
    logging.info('Unchanged:   %4s', len(common) - updated)
    logging.info('Added:       %4s [%+4i MB]', len(added), added_size)
    logging.info('Removed:     %4s [%+4i MB]', len(removed), removed_size)
    logging.info('Changed:     %4s [%+4i MB]', updated, updated_size)
    logging.info('')

    return common, removed, added


def main(old_manifest, new_manifest, debug=False):
    """
    Diffs two ISO manifest files for a pretty report.
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.basicConfig(stream=sys.stdout, format='%(message)s',
                        level=log_level)

    old = read_manifest(old_manifest)
    new = read_manifest(new_manifest)

    common, removed, added = set_math(old, new)
    find_pkg_added(new, added)
    find_pkg_removed(old, removed)
    find_pkg_updated(old, new, common)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('old', help='older ISO manifest for comparison')
    PARSER.add_argument('new', help='newer ISO manifest for comparison')
    PARSER.add_argument('-d', '--debug', action='store_true',
                        help='debug output')

    ARGS = PARSER.parse_args()

    main(ARGS.old, ARGS.new, ARGS.debug)
