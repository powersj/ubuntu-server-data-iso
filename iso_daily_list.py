#!/usr/bin/env python
"""
Outputs all available daily ISOs and specifies which is current and pending.

Optionally can print out the latest two ISOs for use in doing diffs.
"""
import argparse
import logging
import re
import sys
import requests


def _request_url(url):
    """
    Using requests to get a specific URL.
    """
    result = requests.get(url)
    if result.status_code != requests.codes.ok:
        logging.info('[%s] error getting to URL: %s', result.status_code, url)
        sys.exit(1)

    return result.text


def get_daily_releases(url):
    """
    From the URL get the list of releases.
    """
    text = _request_url(url)

    regex = r'([0-9]{8}\.*[0-9]*)'
    matches = sorted(list(set(re.findall(regex, text))))

    return matches


def get_daily_iso_url(flavor, release):
    """
    Return the URL to the daily ISO for the specified flavor.
    """
    if release:
        logging.debug('Ubuntu %s ISO List', flavor)
    else:
        logging.debug('Ubuntu %s (%s) ISO List', flavor, release)

    if release:
        base_url = 'http://cdimage.ubuntu.com/%s/%s' % (flavor, release)
    else:
        base_url = 'http://cdimage.ubuntu.com/%s' % (flavor)

    daily_list = ['ubuntu-server', 'ubuntu-base']
    daily_live_list = ['kubuntu', 'lubuntu', 'mythbuntu', 'trusty', 'ubuntu',
                       'ubuntu-base', 'ubuntu-gnome', 'ubuntu-mate',
                       'ubuntu-server', 'ubuntukylin', 'xenial', 'xubuntu']

    if flavor in daily_list:
        url = base_url + '/daily'
    elif flavor in daily_live_list:
        url = base_url + '/daily-live'
    else:
        logging.info('Flavor not valid. Choose from:')
        logging.info('%s', sorted(daily_list + daily_live_list))
        sys.exit(1)

    return url


def print_report(url, matches):
    """
    Print full report of releases and what is marked
    as current and pending.
    """
    current = _request_url(url + '/current/MD5SUMS')
    pending = _request_url(url + '/pending/MD5SUMS')

    releases = {}
    for release in matches:
        md5_url = url + '/' + release + '/MD5SUMS'
        md5 = _request_url(md5_url)

        flags = []
        if md5 == current:
            flags.append('current')
        if md5 == pending:
            flags.append('pending')

        rel_url = url + '/' + release

        releases[rel_url] = flags

    len_url = len(url) + len(max(matches, key=len)) + 2

    for url, flags in sorted(releases.iteritems(), reverse=True):
        if flags:
            logging.info('%-*s %s', len_url, url, flags)
        else:
            logging.info('%-*s', len_url, url)


def main(flavor, release=None, compare=False, verbose=False):
    """
    List available daily ISOs.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(stream=sys.stdout, format='%(message)s',
                        level=log_level)

    url = get_daily_iso_url(flavor, release)
    matches = get_daily_releases(url)

    if compare:
        logging.info('%s/%s %s/%s', url, matches[-1], url, matches[-2])
    else:
        print_report(url, matches)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('flavor', default='ubuntu-server', nargs='?',
                        help='Ubuntu ISO flavor to check')
    PARSER.add_argument('-c', '--compare', action='store_true',
                        help='show last two ISOs for comparison')
    PARSER.add_argument('-r', '--release',
                        help='specify a release otherwise development release')
    PARSER.add_argument('-v', '--verbose', action='store_true',
                        help='verbose output')

    ARGS = PARSER.parse_args()
    main(ARGS.flavor, ARGS.release, ARGS.compare, ARGS.verbose)
