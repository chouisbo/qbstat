#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys


def usage():
    print 'Usage: ./MergeCSV.py <2013>'


def main(argv):

    try:
        _year = int(argv[1])
    except:
        usage()
        return -1

    _map = {}
    fp = open('stat.csv', 'r')
    for line in fp.readlines():
        line = line.rstrip('\r\n')
        attrs = line.split(',')
        url, others = attrs[0], ','.join(attrs[1:])
        if url not in _map:
            _map[url] = []
        _map[url].append(others)
    fp.close()

    fp = open('%d.csv' % _year, 'r')
    fpw = open('merge%d.csv' % _year, 'w')
    for line in fp.readlines():
        line = line.rstrip('\r\n')
        url = line.split(',')[2]
        if url in _map:
            for el in _map[url]:
                fpw.write(line+','+el+'\n')
        else:
            fpw.write(line+'\n')
            print line
    fpw.close()
    fp.close()

    return 0

if __name__ == "__main__":
    main(sys.argv)
