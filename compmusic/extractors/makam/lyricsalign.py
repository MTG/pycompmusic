'''
Created on Feb 3, 2016

@author: joro
'''

import sys
import os
import urllib2
import json
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


from align.LyricsAligner  import downloadSymbTr,  LyricsAligner, download_wav, stereoToMono, loadMakamRecording
from align.ParametersAlgo import ParametersAlgo
ParametersAlgo.FOR_MAKAM = 1 


dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")

WITH_SECTION_ANNOTATIONS = 1
PATH_TO_HCOPY= '/usr/local/bin/HCopy'
# ANDRES. On kora.s.upf.edu
# PATH_TO_HCOPY= '/srv/htkBuilt/bin/HCopy'

class LyricsAlign(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "lyrics-align"
    _output = {
            "alignedLyricsSyllables": {"extension": "json", "mimetype": "application/json"},
            "sectionlinks": {"extension": "json", "mimetype": "application/json"},
            }
    




    def __init__(self, dataDir):
        self.dataDir = dataDir




    def run(self, musicbrainzid, fname):
        
        citation = u"""
            Dzhambazov, G., & Serra X. (2015).  Modeling of Phoneme Durations for Alignment between Polyphonic Audio and Lyrics.
            Sound and Music Computing Conference 2015.
            """
            
        w = getWork(musicbrainzid)
        outputDir = tempfile.mkdtemp()

        # TODO: mark second verse symbTr second verse and get from a separate reposotory 
# on dunya server
#         symbtrtxtURI = util.docserver_get_symbtrtxt(w['mbid'])
        
# on other computer
        symbtrtxtURI = downloadSymbTr(w['mbid'], outputDir )
        
        if not symbtrtxtURI:
                sys.exit("no symbTr found for work {}".format(w['mbid']) )
        

        if WITH_SECTION_ANNOTATIONS:            #  becasue complying with  score metadata for symbTr1, on which annotations are done
            dir_ = 'scores/metadata/'
            sectionMetadataDict = get_section_annotaions_dict(w['mbid'], dir_, outputDir)
        else:
            sectionMetadataDict = dunya.docserver.get_document_as_json(w['mbid'], "metadata", "metadata", 1, version="0.1")
                      
        
     
        
        if WITH_SECTION_ANNOTATIONS:    #  because complying with section annotations
            #### get section annotation file 
            try:
                dir = 'audio_metadata/'
                sectionAnnosDict = get_section_annotaions_dict(musicbrainzid, dir, outputDir)
            except Exception,e:
                sys.exit("no section annotations found for audio {} ".format(musicbrainzid))
                 
            sectionLinksDict = sectionAnnosDict
        else:
            sectionLinksDict = dunya.docserver.get_document_as_json(musicbrainzid, "scorealign", "sectionlinks", 1, version="0.2")
        try:    
            extractedPitch = dunya.docserver.get_document_as_json(musicbrainzid, "initialmakampitch", "pitch", 1, version="0.6")
        except Exception,e:
            sys.exit("no initialmakampitch series could be downloaded.  ")
        
#  on dunya server       
        wavFileURI, created = util.docserver_get_wav_filename(musicbrainzid)

# on other computer         
#         wavFileURI = download_wav(musicbrainzid, outputDir)



        wavFileURIMono = stereoToMono(wavFileURI)
        if ParametersAlgo.WITH_ORACLE_ONSETS == 1:

            fetchNoteOnsetFile(musicbrainzid, self.dataDir)
        
        recording = loadMakamRecording(musicbrainzid, wavFileURIMono, symbtrtxtURI, sectionMetadataDict, sectionLinksDict,  WITH_SECTION_ANNOTATIONS)
        lyricsAligner = LyricsAligner(recording, WITH_SECTION_ANNOTATIONS, PATH_TO_HCOPY)
    
        totalDetectedTokenList, sectionLinksDict =  lyricsAligner.alignRecording( extractedPitch, outputDir)
        

        ret = {'alignedLyricsSyllables':{}, 'sectionlinks':{} }
        ret['alignedLyricsSyllables'] = totalDetectedTokenList
        ret['sectionlinks'] = sectionLinksDict
        return ret


def getWork( musicbrainzid):
        rec_data = dunya.makam.get_recording(musicbrainzid)
        if len(rec_data['works']) == 0:
            raise Exception('No work on recording %s' % musicbrainzid)
        if len(rec_data['works']) > 1:
            raise Exception('More than one work for recording %s Not implemented!' % musicbrainzid)
        w = rec_data['works'][0]
        return w

def get_section_annotaions_dict( musicbrainzid, dir_, outputDir):
        URL = 'https://raw.githubusercontent.com/georgid/turkish_makam_section_dataset/master/' + dir_ + musicbrainzid + '.json'
        sectionAnnosURI = os.path.join(outputDir, musicbrainzid + '.json')
        if not os.path.isfile(sectionAnnosURI):
            print "fetching sections  annotation from URL {}...".format(URL)
            fetchFileFromURL(URL, sectionAnnosURI)
        with open(sectionAnnosURI) as f3:
            sectionAnnosDict = json.load(f3) # use annotations instead of links
        return sectionAnnosDict


def fetchNoteOnsetFile(musicbrainzid,  datasetDir):
    '''
    fetch note onset annotations
    '''
    recIDoutputDir = os.path.join(datasetDir, musicbrainzid)         
    if not os.path.isdir(recIDoutputDir):
                os.mkdir(recIDoutputDir)
             
    onsetPath = os.path.join(recIDoutputDir,  musicbrainzid + '.alignedNotes.txt')
    if not os.path.isfile(onsetPath):
                work = getWork(musicbrainzid)
                symbtr = dunya.makam.get_symbtr(work['mbid'])
                symbTrCompositionName = symbtr['name']
                URL = 'https://raw.githubusercontent.com/MTG/turkish_makam_audio_score_alignment_dataset/master/data/' + symbTrCompositionName + '/' + musicbrainzid + '/' + 'alignedNotes.txt' 
                
                # problem with symbTrComposition name
                URL = 'https://raw.githubusercontent.com/MTG/turkish_makam_audio_score_alignment_dataset/master/data/nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi/feda89e3-a50d-4ff8-87d4-c1e531cc1233/alignedNotes.txt'
                print "fetching notes score annotation from URL {}...".format(URL)
                fetchFileFromURL(URL, onsetPath )
                



def fetchFileFromURL(URL, outputFileURI):
        response = urllib2.urlopen(URL)
        a = response.read()
        with open(outputFileURI,'w') as f:
            f.write(a)

if __name__=='__main__':
    
#     if len(sys.argv) != 2:
#         sys.exit('usage: {} <localpath>')
#     la = LyricsAlign(sys.argv[1])
    
    la = LyricsAlign('/Users/joro/Downloads/ISTANBULSymbTr2/')
#     la.run('727cff89-392f-4d15-926d-63b2697d7f3f','b')
    la.run('567b6a3c-0f08-42f8-b844-e9affdc9d215','b')
       
        
