# -*- coding: utf-8 -*-

import os, shutil, sys
from fixpath import fixpath, fixfile

def getPaths(srcDir):
	srcPaths = []
	artists = os.listdir("%s" % (srcDir))
	for artist in sorted(artists):
		if not artist.startswith("."):
			albums = os.listdir("%s/%s" % (srcDir, artist))
			for album in sorted(albums):
				if not album.startswith("."):
					name = ("%s/%s" % (artist, album))
					srcPaths.append(name)
	return srcPaths

def removeSpecialChars(srcDir, path, destDir):
	fixedPath = fixpath(path)

	# create folders if they don't exist
	folders = fixedPath.split("/")
	curPath = destDir
	for folder in folders:
		if not os.path.exists(curPath + "/" + folder):
			os.mkdir(curPath + "/" + folder)
		curPath += "/" + folder

	srcFiles = os.listdir(srcDir + "/" + path)
	for filename in srcFiles:
		if filename.endswith(".mp3") and not filename.startswith("."):
			filename = filename[:-4]
			srcFilePath = srcDir + "/" + path + "/" + filename + ".mp3"
			destFilePath = destDir + "/" + fixedPath + "/" + fixfile(filename.strip()) + ".mp3"
			shutil.move(srcFilePath, destFilePath)

if __name__ == "__main__":
	srcDir=sys.argv[1].rstrip("/")
	destDir=sys.argv[2].rstrip("/")
	srcPaths=getPaths(srcDir)
	for path in srcPaths: #Artist/Album
		print srcDir+"/"+path
		removeSpecialChars(u"%s"%srcDir, u"%s"%path.decode("UTF-8"), destDir)
