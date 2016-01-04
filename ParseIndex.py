#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import threading

from MyConstants import CONSTS

records_map = {}


class Record(object):
    def __init__(self, publish_time, url, title):
        self.publish_time = publish_time
        self.url = url
        self.title = title

    def __str__(self):
        return '{ "publish_time":"%s", "url":"%s", "title":"%s" }' % (
                self.publish_time, self.url, self.title)


def genRecord(text):
    regx1 = '<li><span>(\d\d\d\d-\d\d-\d\d)</span>' \
            '<a href="(.*\.shtml)" target="_blank" title="(.+)">'
    regx2 = '<li class="bj2"><span>(\d\d\d\d-\d\d-\d\d)</span>' \
            '<a href="(.*\.shtml)" target="_blank" title="(.+)">'
    m = re.search(regx1, text)
    if m:
        try:
            return Record(m.group(1), m.group(2), m.group(3))
        except:
            pass
    else:
        m = re.search(regx2, text)
        if m:
            try:
                return Record(m.group(1), m.group(2), m.group(3))
            except:
                return None
        else:
            return None


def rel2AbsURL(baseURLPath, relURL):
    splits = relURL.split('/')
    base_splits = baseURLPath[baseURLPath.find('//')+2:].split('/')

    for _split in splits:
        if _split == '.':
            continue
        if _split == '..':
            assert(len(base_splits) > 0)
            base_splits.pop()
        else:
            base_splits.append(_split)
    return baseURLPath[:baseURLPath.find('//')+2] + '/'.join(base_splits)


def extract_news_links(index_file_path, entry_url):
    records = []
    url_prefix = entry_url[:entry_url.rfind('/')]
    fp = open(index_file_path)
    for line in fp.readlines():
        line = line.rstrip('\r\n')
        aRecord = genRecord(line)
        if aRecord is None:
            continue
        aRecord.url = rel2AbsURL(url_prefix, aRecord.url)
        records.append(aRecord)
    fp.close()
    return records


def readAllIndexes(entry_list_path):
    fp = open(entry_list_path, 'r')
    for line in fp.readlines():
        line = line.rstrip('\r\n')
        attrs = line.split(';')
        entry_name, entry_url = attrs[0], attrs[1]
        start, end = int(attrs[2]), int(attrs[3])

        entry_path = os.path.join(CONSTS['ROOT_INDEX_PATH'], entry_name)
        assert(os.path.exists(entry_path))

        global records_map
        if entry_name not in records_map:
            records_map[entry_name] = []

        for i in range(start-1, end):
            filename = 'index%d.shtml' % i
            if i == 0:
                filename = 'index.shtml'
            file_path = os.path.join(entry_path, filename)
            _records = extract_news_links(file_path, entry_url)
            length = len(_records)
            if length != 20:
                print 'Not 20 per page: %s with %d' % (file_path, length)
            records_map[entry_name].extend(_records)
    fp.close()


def mkdirIfNotExists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        return True
    return False


class ScriptThread(threading.Thread):
    def __init__(self, script_path):
        threading.Thread.__init__(self)
        self.script_path = script_path

    def run(self):
        _cmd = 'sh %s' % self.script_path
        os.system(_cmd)
        time.sleep(1)


def downloadYear(_year):
    global records_map

    threads = []
    for k, v in records_map.items():
        entry_name = k
        bYW = False
        if entry_name == 'yw':
            bYW = True
        entry_path = os.path.join(CONSTS['ROOT_DATA_PATH'], entry_name)
        mkdirIfNotExists(entry_path)

        script_path = os.path.join(entry_path,
                                   CONSTS['DATA_DOWNLOAD_SCRIPT_NAME'])
        fp = open(script_path, 'w')
        fp.write('#!/bin/bash\n')
        user_agent = 'Chrome/31.0.1650.63'
        cnt = 0
        for aRecord in v:
            if aRecord.publish_time[:4] == str(_year):
                if bYW and aRecord.url.find('/yw/') == -1:
                    continue
                filename = aRecord.url[aRecord.url.rfind('/')+1:]
                file_path = os.path.join(entry_path, filename)
                _cmd = 'curl -A "%s" -m 30 "%s" ' \
                       '| iconv -f gb18030 -t utf-8 > %s' % (user_agent,
                                                             aRecord.url,
                                                             file_path)
                fp.write(_cmd)
                fp.write('\n')
                cnt += 1
                if cnt == 10:
                    fp.write('sleep 3\n')
                    cnt = 0
        fp.write('exit 0')
        fp.close()
        threads.append(ScriptThread(script_path))
    for th in threads:
        th.start()
    for th in threads:
        th.join()


def outputYearCSV(_year):
    global records_map
    fp = open(str(_year)+'.csv', 'w')
    for k, v in records_map.items():
        for aRecord in v:
            if aRecord.publish_time[:4] == str(_year):
                fp.write('%s,%s,%s,%s\n' % (k, aRecord.publish_time,
                                            aRecord.url, aRecord.title))
    fp.close()


def usage():
    print 'Usage: ./ParseIndex.py <2013>'


def main(argv):
    _year = 2013
    try:
        _year = int(argv[1])
    except:
        usage()
        return -1
    global records_map
    records_map = {}

    readAllIndexes(CONSTS['ENTRY_LIST_FILENAME'])

    downloadYear(_year)
    outputYearCSV(_year)
    return 0

if __name__ == "__main__":
    main(sys.argv)
