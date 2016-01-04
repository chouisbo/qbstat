#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import threading

from MyConstants import CONSTS

all_scripts = []


def mkdirIfNotExists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        return True
    return False


def generateIndexDownloadScript(entry_name, entry_path, start, end):
    script_path = os.path.join(entry_path,
                               CONSTS['INDEX_DOWNLOAD_SCRIPT_NAME'])
    fp = open(script_path, 'w')
    fp.write('#!/bin/bash\n')
    user_agent = 'Chrome/31.0.1650.63'
    url_path = '%s/%s/' % (CONSTS['URL_PREFIX'], entry_name)

    for i in range(start-1, end):
        filename = 'index%d.shtml' % i
        if i == 0:
            filename = 'index.shtml'
        file_path = os.path.join(entry_path, filename)
        _cmd = 'curl -A "%s" -m 30 "%s" | iconv -f gb18030 -t utf-8 > %s' % (
                user_agent, url_path+filename, file_path)
        fp.write(_cmd)
        fp.write('\n')

    fp.write('exit 0')
    fp.close()
    return script_path


def generateAllIndexes(entry_list_path):
    fp = open(entry_list_path, 'r')
    for line in fp.readlines():
        line = line.rstrip('\r\n')
        attrs = line.split(';')
        entry_name, start, end = attrs[0], int(attrs[2]), int(attrs[3])

        # mkdir if not exists
        entry_path = os.path.join(CONSTS['ROOT_INDEX_PATH'], entry_name)
        mkdirIfNotExists(entry_path)

        # generate index download script
        global all_scripts
        all_scripts.append(
            generateIndexDownloadScript(entry_name, entry_path, start, end))
    fp.close()


class ScriptThread(threading.Thread):
    def __init__(self, script_path):
        threading.Thread.__init__(self)
        self.script_path = script_path

    def run(self):
        _cmd = 'sh %s' % self.script_path
        os.system(_cmd)
        time.sleep(1)


def main(argv):
    global all_scripts
    all_scripts = []

    generateAllIndexes(CONSTS['ENTRY_LIST_FILENAME'])

    # multi thread running to download all index files
    threads = []
    for script_path in all_scripts:
        threads.append(ScriptThread(script_path))
    for th in threads:
        th.start()
    for th in threads:
        th.join()


if __name__ == "__main__":
    main(sys.argv)
