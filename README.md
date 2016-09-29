# Ubuntu Server Preseed
A series of scripts to get information about Ubuntu ISOs. Why? "If you have to do it more than twice, automated it!"

## Daily List (daily_list.py)
List of available Ubuntu daily ISOs, used by size. Works more than just ubuntu-sever, can use ubutnu, kubuntu, etc.

## Daily Size (daily_size.py)
Determines size difference of the last two daily ISOs by architechture.

## Stats (stats.py)
Produces size numbers and quantities about a particular ISO passed in.

## Manifest (manifest.py)
Produces manifest of pool with sizing information used for comparison.

## Diff (diff.py)
Given two manifest, determines updates, removals, and additions.

# TODO
* How to handle the livefs manifest already on the CD.
