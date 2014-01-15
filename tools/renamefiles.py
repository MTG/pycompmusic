# -*- coding: utf-8 -*-
# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
# 
# This file is part of Dunya
# 
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

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
