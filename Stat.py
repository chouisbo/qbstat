#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re

from MyConstants import CONSTS


def loadNameMaps(filepath):
    idx_map, reverse_idx_map = {}, {}
    fp = open(filepath, 'r')
    for line in fp.readlines():
        line = line.rstrip('\r\n')
        attrs = line.split(',')
        fullname, shortname = attrs[0], attrs[1]
        if fullname in idx_map:
            assert(False)
        if shortname in reverse_idx_map:
            assert(False)
        idx_map[fullname] = shortname
        reverse_idx_map[shortname] = fullname
    fp.close()
    return idx_map, reverse_idx_map


def loadErrorNameMaps(filepath):
    idx_map = {}
    fp = open(filepath, 'r')
    for line in fp.readlines():
        line = line.rstrip('\r\n')
        attrs = line.split(',')
        fullname, shortname = attrs[0], attrs[1]
        if fullname in idx_map:
            assert(False)
        idx_map[fullname] = shortname
    fp.close()
    return idx_map


def extractOriginSourceAndDate(filepath):
    fp = open(filepath, 'r')
    content = fp.read()
    fp.close()
    content = content[content.find('<div id="author">'):]
    source = content[content.find('文章来源：')+15:content.find('&nbsp;')]
    content = content[content.find('发布时间：')+15:]
    date = content[:content.find('&nbsp;')]
    return source, date


def source_filtering(source):
    pass


def _stat():
    idx_map, reverse_idx_map = loadNameMaps('short_name.idx')
    error_idx_map = loadErrorNameMaps('error_short_name.idx')

    # for k,v in idx_map.items(): print '%s=>%s' % (k,v)
    # for k,v in reverse_idx_map.items(): print '%s=>%s' % (k,v)
    fp = open(CONSTS['ENTRY_LIST_FILENAME'], 'r')
    csvfp = open('stat.csv', 'w')
    for line in fp.readlines():
        line = line.rstrip('\r\n')
        attrs = line.split(';')
        entry_name = attrs[0]
        # if entry_name == 'yw': continue # skip yw
        entry_path = os.path.join(CONSTS['ROOT_DATA_PATH'], entry_name)
        for filename in os.listdir(entry_path):
            if filename.endswith('.shtml'):
                url = CONSTS['URL_PREFIX']+'/'+entry_name+'/'+filename
                filepath = os.path.join(entry_path, filename)
                originSource, date = extractOriginSourceAndDate(filepath)
                # Optimization  With getShortSources
                res = getShortSources(url, originSource, idx_map,
                                      reverse_idx_map, error_idx_map)
                if len(res) == 0:
                    print "[Error] URL=>%s, OriginSource=>%s, " \
                          "Date=>%s" % (url, originSource, date)
                    csvfp.write('%s,%s,%s,%s,%s,%d\n' %
                                (url, filepath, originSource, "", date, 1))
                else:
                    for el in res:
                        # csvfp.write('%s,%s,%s,%s,%s\n' %
                        # (url, filepath, source, short_source, date))
                        csvfp.write('%s,%s,%s,%s,%s,%d\n' %
                                    (url, filepath, el[0], el[1], date, 0))
    csvfp.close()
    fp.close()


def getShortSources(url, originSource, idx_map,
                    reverse_idx_map, error_idx_map):
    res, _sources, _splitters, tmpSource = [], [], ['、', ' '], originSource

    # regex replace noises
    result, number = re.subn(r"<.+?>", '', tmpSource)
    if number > 0:
        tmpSource = result

    # splitting test
    for el in _splitters:
        _sources = tmpSource.split(el)
        if len(_sources) > 1:
            break

    for _source in _sources:
        if _source in idx_map:
            # print "ShortSource => %s" % idx_map[_source]
            res.append((_source, idx_map[_source]))
        elif _source in reverse_idx_map:
            # print "Source => %s" % reverse_idx_map[_source]
            res.append((reverse_idx_map[_source], _source))
        else:
            # Using Error Idxmap
            if _source in error_idx_map:
                short_source = error_idx_map[_source]
                print "[Warn] Using Error idxMap to " \
                      "[%s] From %s To %s" % (url, _source, short_source)
                res.append((_source, short_source))
            # print "[Error] Unkown Source or ShortSource=>%s" % _source
            pass

    return res


def _test():
    # For getShortSources Testing
    idx_map, reverse_idx_map = loadNameMaps('short_name.idx')
    error_idx_map = loadErrorNameMaps('error_short_name.idx')
    testFilelist = [
        './test/233937.shtml',  # Normal
        './test/239414.shtml',  # parts split by ' '
        './test/242896.shtml',  # parts split by '、'
        # Noise like 中国农业科学院
        # <a href="http://www.caas.cn/jg/yzgsw/53865.shtml" target="_blank">
        # 农业信息研究所</a>
        './test/233837.shtml',
        # Using Error Idxmap <=> Edit-Distance 中国农业科学院油料研究所
        './test/238752.shtml'
    ]
    for filepath in testFilelist:
        print "###################  Testing %s #################" % filepath
        originSource, date = extractOriginSourceAndDate(filepath)
        res = getShortSources(filepath, originSource,
                              idx_map, reverse_idx_map, error_idx_map)
        if len(res) == 0:
            print "getShortSources %s Error!"
        else:
            for el in res:
                print "%s <=> %s" % (el[0], el[1])


def main(argv):
    # _test()
    _stat()

if __name__ == "__main__":
    main(sys.argv)
