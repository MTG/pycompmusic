# -*- coding: utf-8 -*-
import os, unicodedata, string, sys

# WORKS FOR FULL PATHS

validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
#validFoldernameChars = "-_.()/& %s%s" % (string.ascii_letters, string.digits)

def cleanFilePath(filepath):
	return unicodedata.normalize('NFKD', filepath).encode('ASCII', 'ignore')

def removeDisallowedFilenameChars(filename):
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleanedFilename if c in validFilenameChars)

def fixfile(filename):
	filename = removeDisallowedFilenameChars(filename)
	return filename.replace(" ", "_").replace(".", "_")

def fixpath(path):
	return cleanFilePath(path).replace(" ", "_").replace(".", "_")

if __name__ == "__main__":
	pass
	'''
	#fullpath = os.listdir("/Users/msordo/Music/iTunes/iTunes Music/")
	#path = u"Bajeddoub & Souiri/L'Art Du Mawwâl/04 ʿÎdû ilayya l-wiṣâl_Renouvelez Votre Union.mp3"
	if len(sys.argv) < 2:
		print 'Usage: python %s "rootpath"' % sys.argv[0]
		print 'Example: python %s "Bajeddoub & Souiri/L\'Art Du Mawwâl/04 ʿÎdû ilayya l-wiṣâl_Renouvelez Votre Union.mp3"'
		sys.exit(1)
	rootpath = sys.argv[1].decode("utf-8")
	path = sys.argv[2].decode("utf-8")
	print path
	print fixpath(rootpath, path)
	'''