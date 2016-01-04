#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re

from MyConstants import CONSTS


def genRecord(text):
    regx = r'http:\/\/www\.caas\.cn\/ysxw\/\w+\/\d+\.shtml'
    m = re.search(regx, text)
    if m:
        try:
            return m.group(0)
        except:
            return None
    else:
        return None


def _check():
    fp = open(CONSTS['ENTRY_LIST_FILENAME'], 'r')
    to_download_set = set([])
    downloaded_set = set([])
    for line in fp.readlines():
        line = line.rstrip('\r\n')
        attrs = line.split(';')
        entry_name = attrs[0]
        entry_path = os.path.join(CONSTS['ROOT_DATA_PATH'], entry_name)
        for filename in os.listdir(entry_path):
            if filename.endswith('.shtml'):
                filepath = os.path.join(entry_path, filename)
                filelen = os.path.getsize(filepath)
                if (filelen > 10000):
                    url = CONSTS['URL_PREFIX']+'/'+entry_name+'/'+filename
                    downloaded_set.add(url)
            elif filename == 'download_data.sh':
                dfile_path = os.path.join(entry_path, filename)
                dfp = open(dfile_path, 'r')
                ###########################################################
                for dline in dfp.readlines():
                    dline = dline.rstrip('\r\n')
                    durl = genRecord(dline)
                    if durl is not None:
                        to_download_set.add(durl)
                ###########################################################
                dfp.close()
    fp.close()

    print len(downloaded_set)
    print len(to_download_set)


def main(argv):
    _check()

if __name__ == "__main__":
    main(sys.argv)
