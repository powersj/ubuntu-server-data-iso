#!/usr/bin/env python3
"""
Outputs differences two daily ISO sizes.
"""
import argparse
import logging
import re
import sys
from util import request_url


def get_iso_sizes(url):
    """
    Reviews all the size information for the architechtures.
    """
    architechtures = ['amd64', 'i386', 'arm64', 'powerpc', 'ppc64el', 's390x']
    text = request_url(url)

    sizes = {}
    for arch in architechtures:
        regex = (arch + r'.iso<\/a>\s*[0-9]{2}-[A-Z][a-z]{2}'
                 r'-[0-9]{4}\s[0-9]{2}:[0-9]{2}\s*.*[0-9][MG]')
        matches = sorted((list(set(re.findall(regex, text)))))

        if len(matches) == 1:
            unit = matches[0].split(' ')[-1][-1]
            size = matches[0].split(' ')[-1][:-1]

            if unit == 'G':
                sizes[arch] = float(size)
            else:
                sizes[arch] = int(size)

        elif len(matches) > 1:
            logging.info('Error: more than one match for %s', arch)
            sys.exit(1)
        else:
            logging.debug('No results for %s', arch)

    return sizes


def main(old_url, new_url, debug=False):
    """
    Print out the size differences in ISOs between two releases.
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(stream=sys.stdout, format='%(message)s',
                        level=log_level)

    new_sizes = get_iso_sizes(new_url)
    old_sizes = get_iso_sizes(old_url)

    logging.info('Daily ISO Size Diff')
    logging.info('---')
    logging.info('old: %s', old_url)
    logging.info('new: %s', new_url)
    logging.info('---')
    logging.info('        OLD --> NEW [DIFF]')

    for key, new_size in new_sizes.items():
        if key in old_sizes:
            old_size = old_sizes[key]
            diff = float(new_size - old_size)
            if diff:
                logging.info('%7s %3s --> %3s [%+2.1f]',
                             key, old_size, new_size, diff)

    logging.info('')


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('old', help='older ISO URL for comparison')
    PARSER.add_argument('new', help='newer ISO URL for comparison')
    PARSER.add_argument('-d', '--debug', action='store_true',
                        help='debug output')

    ARGS = PARSER.parse_args()
    main(ARGS.old, ARGS.new, ARGS.debug)
