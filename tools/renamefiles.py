# -*- coding: utf-8 -*-

"""
Rename audio directories and files that have been named
by picard
"""

import os
import shutil
import sys
import unicodedata
import string
import argparse

validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)

def fixfile(filename):
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    filename = ''.join([c for c in cleanedFilename if c in validFilenameChars])
    fparts = os.path.splitext(filename)
    newfname = fparts[0].replace(" ", "_").replace(".", "_")
    return "%s%s" % (newfname, fparts[1])

def fixpath(filepath):
    filepath = unicodedata.normalize('NFKD', filepath).encode('ASCII', 'ignore')
    return filepath.replace(" ", "_").replace(".", "_")

def removeSpecialChars(srcDir, destDir):
    if not srcDir.endswith("/"):
        srcDir += "/"
    for dirpath, dirnames, filenames in os.walk(srcDir):
        if len(filenames):
            dirpath = dirpath[len(srcDir):]
            if isinstance(dirpath, str):
                dirpath = dirpath.decode("utf-8")
            fixedPath = fixpath(dirpath)
            target_dir = os.path.join(destDir, fixedPath)
            try:
                os.makedirs(target_dir)
            except os.error:
                pass
            for f in filenames:
                if f.endswith(".mp3"):
                    if isinstance(f, str):
                        f = f.decode("utf-8")
                    destfile = fixfile(f)
                    destFilePath = os.path.join(target_dir, destfile)
                    srcFilePath = os.path.join(dirpath, f)
                    print "%s -> %s" % (srcFilePath, destFilePath)
                    shutil.move(srcFilePath, destFilePath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('dest')
    args = parser.parse_args()
    removeSpecialChars(args.source, args.dest)
