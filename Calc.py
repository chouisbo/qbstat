#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys


def usage():
    print 'Usage: ./Calc.py <2014>'


def loadNameMaps():
    danwei_list, idx_map, reverse_idx_map = [], {}, {}
    fp = open('short_name.idx', 'r')
    for line in fp.readlines():
        line = line.rstrip('\r\n')
        attrs = line.split(',')
        fullname, shortname = attrs[0], attrs[1]
        if fullname in idx_map:
            assert(False)
        if shortname in reverse_idx_map:
            assert(False)
        danwei_list.append(shortname)
        idx_map[fullname] = shortname
        reverse_idx_map[shortname] = fullname
    fp.close()
    return danwei_list, idx_map, reverse_idx_map


def loadLanmuMap():
    lanmu_list, lanmu_name_map = [], {}
    fp = open('entry.list', 'r')
    for line in fp.readlines():
        line = line.rstrip('\r\n')
        attrs = line.split(';')
        lanmu, lanmuname = attrs[0], attrs[4]
        if lanmu in lanmu_name_map:
            assert(False)
        lanmu_list.append(lanmu)
        lanmu_name_map[lanmu] = lanmuname
    fp.close()
    return lanmu_list, lanmu_name_map


def init_map(danwei_list):
    _map = {}
    for danwei in danwei_list:
        _map[danwei] = 0
    return _map


def main(argv):

    try:
        _year = int(argv[1])
    except:
        usage()
        return -1

    danwei_list, idx_map, reverse_idx_map = loadNameMaps()
    lanmu_list, lanmu_name_map = loadLanmuMap()

    lanmu_map = {}

    fp = open('calc%d.csv' % _year, 'r')
    line_no = 0
    for line in fp.readlines():
        line_no += 1
        line = line.rstrip('\r\n')
        attrs = line.split(',')
        lanmu, danweis = attrs[0], attrs[6]
        if lanmu not in lanmu_map:
            lanmu_map[lanmu] = init_map(danwei_list)
        for danwei in danweis.split(';'):
            # print '%d,%s,%s' % (line_no,lanmu, danwei)
            try:
                lanmu_map[lanmu][danwei] += 1
            except KeyError:
                print '%d,%s,%s' % (line_no, lanmu, danwei)
    fp.close()

    print ','+','.join(danwei_list)

    for lanmu in lanmu_list:
        try:
            _line = '%s' % lanmu_name_map[lanmu]
        except KeyError:
            print lanmu
        for danwei in danwei_list:
            _line += ',%d' % lanmu_map[lanmu][danwei]
        print _line

    return 0

if __name__ == "__main__":
    main(sys.argv)
