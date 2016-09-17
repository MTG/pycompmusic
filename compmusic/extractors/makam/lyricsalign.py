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
from docserver import util
from compmusic import dunya
from compmusic.dunya import makam
import tempfile


from align.LyricsAligner  import  LyricsAligner, stereoToMono, loadMakamRecording
from align.ParametersAlgo import ParametersAlgo

# if on server: 
ParametersAlgo.FOR_MAKAM = 1 
ParametersAlgo.POLYPHONIC = 1
ParametersAlgo.WITH_DURATIONS = 1
ParametersAlgo.DETECTION_TOKEN_LEVEL= 'syllables'


dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")

WITH_SECTION_ANNOTATIONS = 1
PATH_TO_HCOPY= '/usr/local/bin/HCopy'
# ANDRES. On kora.s.upf.edu
PATH_TO_HCOPY= '/srv/htkBuilt/bin/HCopy'

class LyricsAlign(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "lyrics-align"
    _output = {
            "alignedLyricsSyllables": {"extension": "json", "mimetype": "application/json"},
            "sectionlinks": {"extension": "json", "mimetype": "application/json"},
            }
    




    def __init__(self, dataDir=None, hasSecondVerse=None, hasSectionNumberDiscrepancy=None, **kwargs):
        super(LyricsAlign, self).__init__()
#         self.dataOutputDir = dataOutputDir
#         self.hasSecondVerse = hasSecondVerse
#         self.hasSectionNumberDiscrepancy = hasSectionNumberDiscrepancy

        self.dataOutputDir = tempfile.mkdtemp()
        self.hasSecondVerse = False
        self.hasSectionNumberDiscrepancy = False

  

    def run(self, musicbrainzid, fname):
        
        citation = u"""
            Dzhambazov, G., & Serra X. (2015).  Modeling of Phoneme Durations for Alignment between Polyphonic Audio and Lyrics.
            Sound and Music Computing Conference 2015.
            """
        
        #### output
        ret = {'alignedLyricsSyllables':{}, 'sectionlinks':{} }
            
        
        recIDoutputDir = os.path.join(self.dataOutputDir, musicbrainzid)         
        if not os.path.isdir(recIDoutputDir):
                os.mkdir(recIDoutputDir)

        w = getWork(musicbrainzid)
        
        # TODO: mark second verse symbTr second verse and get from a separate reposotory 
# on dunya server. API might be outdated, as some symbtr names are changed. better use line below
        symbtrtxtURI = util.docserver_get_symbtrtxt(w['mbid'])
        
# on other computer. fetch directly from github
        symbtrtxtURI = downloadSymbTr(w['mbid'], recIDoutputDir, self.hasSecondVerse)
        
        if not symbtrtxtURI:
                sys.exit("no symbTr found for work {}".format(w['mbid']) )
        
        
        ############ score section metadata
        if WITH_SECTION_ANNOTATIONS:            #  becasue complying with  score metadata for symbTr1, on which annotations are done
            dir_ = 'scores/metadata/'
            sectionMetadataDict = get_section_metadata_dict(w['mbid'], dir_, recIDoutputDir, self.hasSectionNumberDiscrepancy)
        else:
            sectionMetadataDict = dunya.docserver.get_document_as_json(w['mbid'], "metadata", "metadata", 1, version="0.1") # NOTE: this is default for note onsets
                      
     
        ##################### audio section annotation  or result from section linking
        if WITH_SECTION_ANNOTATIONS:    #  because complying with section annotations
            try:
                dir_ = 'audio_metadata/'
                sectionLinksDict = get_section_annotaions_dict(musicbrainzid, dir_, self.dataOutputDir, self.hasSectionNumberDiscrepancy)
            except Exception,e:
                sys.exit("no section annotations found for audio {} ".format(musicbrainzid))
                 
        else:
            try:
                sectionLinksDict = dunya.docserver.get_document_as_json(musicbrainzid, "scorealign", "sectionlinks", 1, version="0.2")
            except dunya.conn.HTTPError:
                  logging.error("section link {} missing".format(musicbrainzid))
                  return ret
            if not sectionLinksDict:
                  logging.error("section link {} missing".format(musicbrainzid))
                  return ret
        
        try:    
            extractedPitch = dunya.docserver.get_document_as_json(musicbrainzid, "jointanalysis", "pitch", 1, version="0.1")
            extractedPitch = extractedPitch['pitch']
        except Exception,e:
            sys.exit("no initialmakampitch series could be downloaded.  ")
        
#  on dunya server       
        wavFileURI, created = util.docserver_get_wav_filename(musicbrainzid)

# on other computer
        
#         wavFileURI = get_audio(self.dataOutputDir,  musicbrainzid)
                 

        

        wavFileURIMono = stereoToMono(wavFileURI)
        if ParametersAlgo.WITH_ORACLE_ONSETS == 1:
            fetchNoteOnsetFile(musicbrainzid, recIDoutputDir)
        
        recording = loadMakamRecording(musicbrainzid, wavFileURIMono, symbtrtxtURI, sectionMetadataDict, sectionLinksDict,  WITH_SECTION_ANNOTATIONS)
        lyricsAligner = LyricsAligner(recording, WITH_SECTION_ANNOTATIONS, PATH_TO_HCOPY)
    
        totalDetectedTokenList, sectionLinksDict =  lyricsAligner.alignRecording( extractedPitch, self.dataOutputDir)
        lyricsAligner.evalAccuracy()

        
        ret['alignedLyricsSyllables'] = totalDetectedTokenList
        ret['sectionlinks'] = sectionLinksDict
#         print ret
        return ret


def getWork( musicbrainzid):
        rec_data = dunya.makam.get_recording(musicbrainzid)
        if len(rec_data['works']) == 0:
            raise Exception('No work on recording %s' % musicbrainzid)
        if len(rec_data['works']) > 1:
            raise Exception('More than one work for recording %s Not implemented!' % musicbrainzid)
        w = rec_data['works'][0]
        return w

def get_audio(dataDir, musicbrainzid):
        recIDoutputDir = os.path.join(dataDir, musicbrainzid)         
        if not os.path.isdir(recIDoutputDir):
            os.mkdir(recIDoutputDir)
        
        wavFileURI = os.path.join(recIDoutputDir, musicbrainzid + '.wav' )
        
        if ParametersAlgo.POLYPHONIC: 
            wavFileURI_as_fetched = download_wav(musicbrainzid, recIDoutputDir)
#             wavFileURI = wavFileURI_as_fetched
            os.rename(wavFileURI_as_fetched, wavFileURI)
        else: # acapella expect file to be already provided in dir
            
            if not os.path.isfile(wavFileURI):  
                sys.exit("acapella file {} not found".format(wavFileURI))
        return wavFileURI


def download_wav(musicbrainzid, outputDir):
        '''
        download wav for MB recording id from makam collection
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


def get_section_annotaions_dict( musicbrainzid, dir_, outputDir, hasSectionNumberDiscrepancy):
        URL = 'https://raw.githubusercontent.com/georgid/turkish_makam_section_dataset/master/' + dir_ + musicbrainzid + '.json'
        sectionAnnosURI = os.path.join(outputDir, musicbrainzid + '.json')
        fetchFileFromURL(URL, sectionAnnosURI)
        
#         if not hasSectionNumberDiscrepancy: # because score section metadata taken from sertan's github but section anno from georgis
#             raw_input("make sure you audio section Annotation... has same section letters as score section Metadata ")

        
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


def downloadSymbTr(workMBID, outputDirURI, hasSecondVerse):
    
    symbtr = compmusic.dunya.makam.get_symbtr(workMBID)
    symbTrCompositionName = symbtr['name']
    
    if workMBID == '30cdf1c2-8dc3-4612-9513-a5d7f523a889': # because of problem in work
        symbTrCompositionName = 'ussak--sarki--aksak--bu_aksam--tatyos_efendi'
    
    URL = 'https://raw.githubusercontent.com/MTG/SymbTr/master/txt/' + symbTrCompositionName + '.txt'
    outputFileURI = os.path.join(outputDirURI, symbTrCompositionName + '.txt')

    if hasSecondVerse: 
        raw_input("composition has a second verse not in github. copy symbTr manually to {}.\n  when done press a key ".format(outputFileURI))
    else:
        fetchFileFromURL(URL, outputFileURI)
        print "downloaded symbtr file  {}".format(outputFileURI)  

    return outputFileURI



def fetchNoteOnsetFile(musicbrainzid,  recIDoutputDir):
    '''
    fetch note onset annotations
    '''

             
    onsetPath = os.path.join(recIDoutputDir,  ParametersAlgo.ANNOTATION_ONSETS_EXT)
    if not os.path.isfile(onsetPath):
                work = getWork(musicbrainzid)
                symbtr = dunya.makam.get_symbtr(work['mbid'])
                symbTrCompositionName = symbtr['name']
                URL = 'https://raw.githubusercontent.com/MTG/turkish_makam_audio_score_alignment_dataset/vocal-only-annotation//data/' + symbTrCompositionName + '/' + musicbrainzid + '/' + ParametersAlgo.ANNOTATION_ONSETS_EXT
                
                # problem with symbTrComposition name
#                 URL = 'https://raw.githubusercontent.com/MTG/turkish_makam_audio_score_alignment_dataset/master/data/nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi/feda89e3-a50d-4ff8-87d4-c1e531cc1233/' + ParametersAlgo.ANNOTATION_ONSETS_EXT
                fetchFileFromURL(URL, onsetPath )
                





def fetchFileFromURL(URL, outputFileURI):
        print "fetching file from URL {} ...  ".format(URL) 
        try:
            response = urllib2.urlopen(URL)
            a = response.read()
        except Exception:
            "...maybe symbTr name has changed"
        
        with open(outputFileURI,'w') as f:
            f.write(a)


       
        


if __name__=='__main__':


    
#     if len(sys.argv) != 2:
#         sys.exit('usage: {} <localpath>')

    la = LyricsAlign()
    la.run('727cff89-392f-4d15-926d-63b2697d7f3f','b')
#     la.run('567b6a3c-0f08-42f8-b844-e9affdc9d215','b')
       
        



