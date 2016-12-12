'''
Created on Feb 3, 2016

@author: joro
'''

import sys
import os
import urllib2
import json
import logging
import subprocess
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir,  os.path.pardir,  os.path.pardir,  os.path.pardir))
pathAlignmentDur = os.path.join(parentDir, 'AlignmentDuration')
print pathAlignmentDur

if pathAlignmentDur not in sys.path:
    sys.path.append(pathAlignmentDur)


import compmusic.extractors
# from docserver import util
from compmusic import dunya
from compmusic.dunya import makam
import tempfile





dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")

WITH_SECTION_ANNOTATIONS = 1
PATH_TO_HCOPY= '/usr/local/bin/HCopy'
# ANDRES. On kora.s.upf.edu
# PATH_TO_HCOPY= '/srv/htkBuilt/bin/HCopy'



def getWork( musicbrainzid):
        try:
            rec_data = dunya.makam.get_recording(musicbrainzid)
            if len(rec_data['works']) == 0:
                raise Exception('No work on recording %s' % musicbrainzid)
            if len(rec_data['works']) > 1:
                raise Exception('More than one work for recording %s Not implemented!' % musicbrainzid)
            w = rec_data['works'][0]
        except Exception:
            sys.exit('no recording with this UUID found or no works related')
            w = {}
            w['mbid'] = ''
        return w

def fetch_audio_wav(data_output_Dir, musicbrainzid, for_polyphonic):
        '''
        fetch the audio for the wav file from server or repo
        '''
        recIDoutputDir = os.path.join(data_output_Dir, musicbrainzid)        
        if not os.path.isdir(recIDoutputDir):
            os.mkdir(recIDoutputDir)
       
        wavFileURI = os.path.join(recIDoutputDir, musicbrainzid + '.wav' )
       
        if for_polyphonic:
            wavFileURI_as_fetched = download_wav(musicbrainzid, recIDoutputDir)
#             wavFileURI = wavFileURI_as_fetched
            os.rename(wavFileURI_as_fetched, wavFileURI)
        else: # acapella expect file to be already provided in dir
           
            if not os.path.isfile(wavFileURI): 
                sys.exit("acapella file {} not found".format(wavFileURI))
        return wavFileURI


def download_wav(musicbrainzid, outputDir):
        '''
        download mp3 and convert to wav. for MB recording ID from makam collection
        '''
        mp3FileURI = dunya.makam.download_mp3(musicbrainzid, outputDir)
    ###### mp3 to Wav: way 1
    #         newName = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.mp3')
    #         os.rename(mp3FileURI, newName )
    #         mp3ToWav = Mp3ToWav()
    #         wavFileURI = mp3ToWav.run('dummyMBID', newName)
       
        ###### mp3 to Wav: way 2
        wavFileURI = os.path.splitext(mp3FileURI)[0] + '.wav'
        if os.path.isfile(wavFileURI):
            return wavFileURI
           
        pipe = subprocess.Popen(['/usr/local/bin/ffmpeg', '-i', mp3FileURI, wavFileURI])
        pipe.wait()
   
        return wavFileURI


def get_section_annotaions_dict( musicbrainzid, dir_, outputDir, hasSectionNumberDiscrepancy=False):
        '''
        fetch manual section annotations in audio from a repo.
        Annotations made by sertan. They follow the division of score into sections decided by sertan.   
        '''
        URL = 'https://raw.githubusercontent.com/georgid/turkish_makam_section_dataset/master/' + dir_ + musicbrainzid + '.json'
        sectionAnnosURI = os.path.join(outputDir, musicbrainzid + '.json')
        fetchFileFromURL(URL, sectionAnnosURI)
       
        if not hasSectionNumberDiscrepancy: # because score section metadata taken from sertan's github but section anno from georgis
            raw_input("make sure you audio section Annotation... has same section letters as score section Metadata ")

       
        with open(sectionAnnosURI) as f3:
            sectionAnnosDict = json.load(f3) # use annotations instead of links
        return sectionAnnosDict


def get_section_metadata_dict( workmbid, dir_, outputDir, hasSectionNumberDiscrepancy):
       
        symbtr = dunya.makam.get_symbtr(workmbid)
        symbTrCompositionName = symbtr['name']
#         symbTrCompositionName  = 'ussak--sarki--aksak--bu_aksam--tatyos_efendi'
       
        if hasSectionNumberDiscrepancy:
            raw_input("make sure you first run exendSectionLinks... then press key")
            # my derived with extendsecitonLinksnewNames metadata
            URL = 'https://raw.githubusercontent.com/georgid/turkish_makam_section_dataset/master/' + dir_ + workmbid + '.json'
       
        else:
            #  use sertans derived metadata with symbTrdataExtractor
            URL = 'https://raw.githubusercontent.com/sertansenturk/turkish_makam_corpus_stats/master/data/SymbTrData/' + symbTrCompositionName + '.json'

        sectionAnnosURI = os.path.join(outputDir, symbTrCompositionName + '.json')
       
        fetchFileFromURL(URL, sectionAnnosURI)
       
       
        with open(sectionAnnosURI) as f3:
            sectionAnnosDict = json.load(f3) # use annotations instead of links
        return sectionAnnosDict


def downloadSymbTr(workMBID, outputDirURI, hasSecondVerseProblem):
   
    symbtr = compmusic.dunya.makam.get_symbtr(workMBID)
    symbTrCompositionName = symbtr['name']
   
    if workMBID == '30cdf1c2-8dc3-4612-9513-a5d7f523a889': # because of problem in work
        symbTrCompositionName = 'ussak--sarki--aksak--bu_aksam--tatyos_efendi'
   
    URL = 'https://raw.githubusercontent.com/MTG/SymbTr/master/txt/' + symbTrCompositionName + '.txt'
    outputFileURI = os.path.join(outputDirURI, symbTrCompositionName + '.txt')

    if hasSecondVerseProblem:
        raw_input("composition has a second verse not in github. copy symbTr manually to {}.\n  when done press a key ".format(outputFileURI))
    else:
        fetchFileFromURL(URL, outputFileURI)
        print "downloaded symbtr file  {}".format(outputFileURI) 

    return outputFileURI



def fetchNoteOnsetFile(musicbrainzid,  outputDir, alignment_file_name):
    '''
    fetch note onset annotations
    or only vocal onset annotations
    '''

            
    onsetPath = os.path.join(outputDir, alignment_file_name )
    if not os.path.isfile(onsetPath):
                work = getWork(musicbrainzid)
                symbtr = dunya.makam.get_symbtr(work['mbid'])
                symbTrCompositionName = symbtr['name']
                URL = 'https://raw.githubusercontent.com/MTG/turkish_makam_audio_score_alignment_dataset/vocal-only-annotation//data/' + symbTrCompositionName + '/' + musicbrainzid + '/' + alignment_file_name
#                 URL = 'https://raw.githubusercontent.com/MTG/turkish_makam_audio_score_alignment_dataset/master/data/' + symbTrCompositionName + '/' + musicbrainzid + '/' + alignment_file_name
               
                # problem with symbTrComposition name
                fetchFileFromURL(URL, onsetPath )
    return onsetPath         





def fetchFileFromURL(URL, outputFileURI):
        print "fetching file from URL {} ...  ".format(URL)
        try:
            response = urllib2.urlopen(URL)
            a = response.read()
        except Exception:
            "...maybe symbTr name has changed?"
       
        with open(outputFileURI,'w') as f:
            f.write(a)


def doitAllRecs(la, recMBIDs):

    for recMBID in  recMBIDs:
        la = LyricsAlign(dataDir, recMBIDs[recMBID][1], recMBIDs[recMBID][2] ) 
        ret = la.run(recMBID, 'testName')
#         with open('/Users/joro/Downloads/bu_aksam_gun.json', 'w') as f:
#             json.dump( ret, f, indent=4 )
#         raw_input('press enter...')

      
       


if __name__=='__main__':


   
#     if len(sys.argv) != 2:
#         sys.exit('usage: {} <localpath>')
#     la = LyricsAlign(sys.argv[1])
   



   
    doitAllRecs(dataDir, recMBIDs)
   
#     la.run('727cff89-392f-4d15-926d-63b2697d7f3f','b')
#     la.run('567b6a3c-0f08-42f8-b844-e9affdc9d215','b')
       