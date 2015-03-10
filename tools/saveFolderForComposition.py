'''
Created on Jan 21, 2015

Script to store score and audio for given  symbTrName and list of recordingIDs
It creates folder structure

@author: joro
'''



import musicbrainzngs as mb
import os
import sys
import shutil
import unidecode


# this code needed if pycompmusic is copied (not installed as dependecy) in parent URI
parentDir = os.path.abspath(os.path.join( os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir, os.path.pardir)) 
pathPyCompMusic = os.path.join(parentDir, 'pycompmusic')
if not pathPyCompMusic in sys.path:
    sys.path.append(pathPyCompMusic)

import compmusic.file
from compmusic.dunya.makam import download_mp3
from compmusic.dunya.conn import set_token


mb.set_useragent("Dunya", "0.1")
mb.set_rate_limit(False)
mb.set_hostname("musicbrainz.s.upf.edu")

set_token('0d8cd9be63c10c5dc67f70e1052acec836de29bd')



def storeScoreAndAudio(symbTrNameNoExt, recIDs, rootTargetdir ):
    '''
    params symbTrNameNoExt
    '''
    
    symbTrNameNoExt = os.path.basename(symbTrNameNoExt)
    
    
    targetDir = makeDir(symbTrNameNoExt, rootTargetdir)   
    saveScores(symbTrNameNoExt, symbTrDir, targetDir )
   
    saveAudio(targetDir, recIDs)
#     download_mp3(recID, targetDir)



def saveAudio(targetDir, listRecIDs):
    
    isThereAtLeastOneAudioFIle=False
    
    # download audio
    for recID in listRecIDs:
        # write the file temporary
        localUrlAudio =   download_mp3(recID, targetDir )
        
        
        # rename according to release and artist
        try:
            metadata = compmusic.file_metadata(localUrlAudio)
        except Exception: 
            pass
            print "symbTr file ", targetDir, " and recID ", recID,  " has Problem with metadata...", "\n" 
            os.remove(localUrlAudio)
            continue
            
        
        artistName = metadata["meta"]["artist"]
        artistName = unidecode.unidecode(artistName)
        artistName = artistName.replace("/", "_")
        artistName = artistName.replace(" ", "_")
        
        # release name 
#         releaseName = metadata["meta"]["release"]
#         releaseName = unidecode.unidecode(releaseName)
        
        titleName = metadata["meta"]["title"]
        titleName = unidecode.unidecode(titleName)
        titleName = titleName.replace("/", "_")
        titleName = titleName.replace(" ", "_")
        
       
        fileName = '{0}.mp3'.format(titleName)
        newDirUrl = '{0}/{1}'.format(targetDir, artistName)
        if not os.path.exists(newDirUrl): os.makedirs(newDirUrl)
        
        newLocalUrlAudio = os.path.join(newDirUrl,fileName )
        shutil.move(localUrlAudio, newLocalUrlAudio)
        isThereAtLeastOneAudioFIle = True
       
        
    return isThereAtLeastOneAudioFIle 

def makeDir(symbTrNameNoExt, rootTargetdir):
    targetDir = os.path.join(rootTargetdir, symbTrNameNoExt)
    try:
        os.makedirs(targetDir)
    except:
        pass
    return targetDir


def saveScores(symbTrNameNoExt, symbTrDir, targetDir):
    
    try:
        shutil.copy(os.path.join(symbTrDir, symbTrNameNoExt+".txt"), targetDir)
    except IOError:
        pass
    
    try:
        shutil.copy(os.path.join(symbTrDir, symbTrNameNoExt+".pdf"), targetDir)
    except IOError:
        pass
    
    return targetDir


if __name__=="__main__":
    
    symbTrDir = "/Users/joro/Documents/Phd/UPF/symbTrFromMTG/symbTr_phraseSegmented/"
    rootTargetdir = 'resultsTest'

#     symbTrNameNoExt = 'rast--sarki--curcuna--nihansin_dideden--haci_faik_bey'
#     recID = '1701ceba-bd5a-477e-b883-5dacac67da43'


    symbTrNameNoExt = 'nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi'
    recID = 'feda89e3-a50d-4ff8-87d4-c1e531cc1233'
    
#     symbTrNameNoExt = 'rast--turku--semai--gul_agaci--necip_mirkelamoglu'
#     recID = '338e24ba-1f19-49a1-ad6a-2b89e0e09c38'

    storeScoreAndAudio(symbTrNameNoExt, [recID], rootTargetdir )

    
    