"""
Reusable functions
"""
import logging
import os
import requests
import subprocess
import shutil
import sys


def cleanup(folder):
    """
    """
    shutil.rmtree(folder)


def extract(filename):
    """
    Extracts the given ISO to a folder and returns that folder's name.
    """
    dest = os.path.basename(os.path.splitext(filename)[0])

    if os.path.exists(dest):
        cleanup(dest)
    if not os.path.exists(dest):
        os.mkdir(dest)

    run('bsdtar xfp %s -C %s' % (filename, dest))
    run('chmod -R +w %s' % dest)

    return dest


def human_size(size):
    """
    Round bytes to nearest MB
    """
    return int(round(size / 1048576.0))


def request_url(url):
    """
    Using requests to get a specific URL.
    """
    result = requests.get(url)
    if result.status_code != requests.codes.ok:
        logging.info('[%s] error getting to URL: %s', result.status_code, url)
        sys.exit(1)

    return result.text


def run(command):
    """
    """
    try:
        child = subprocess.Popen(command, shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

        (stdout, stderr) = child.communicate()
        return_code = child.returncode
    except OSError as e:
        logging.critical('Command failed: `%s`' % command)
        logging.critical('Error: %s: %s' % (e.errno, e.strerror))
        sys.exit(1)

    if return_code != 0:
        logging.critical('Command failed: `%s`' % command)
        logging.critical(stderr)
        sys.exit(1)
    else:
        logging.debug(command)
        logging.debug(stdout)
        logging.debug(return_code)
