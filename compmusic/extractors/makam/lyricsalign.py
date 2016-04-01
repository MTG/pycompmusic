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


from align.LyricsAligner  import downloadSymbTr,  alignRecording, download_wav, stereoToMono
# from align.MakamScore import loadMakamScore2

dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")

WITH_SECTION_ANNOTATIONS = 1


class LyricsAlign(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "lyrics-align"
    _output = {
            "alignedLyricsSyllables": {"extension": "json", "mimetype": "application/json"},
            "sectionlinks": {"extension": "json", "mimetype": "application/json"},
            }
    






    def run(self, musicbrainzid, fname):
        
        citation = u"""
            Dzhambazov, G., & Serra X. (2015).  Modeling of Phoneme Durations for Alignment between Polyphonic Audio and Lyrics.
            Sound and Music Computing Conference 2015.
            """
            
        rec_data = dunya.makam.get_recording(musicbrainzid )
        
        if len(rec_data['works']) == 0:
                raise Exception('No work on recording %s' % musicbrainzid)
        
        if len(rec_data['works']) > 1:
                raise Exception('More than one work for recording %s Not implemented!' % musicbrainzid)
        
        w = rec_data['works'][0]
        outputDir = tempfile.mkdtemp()
# on dunya server
        symbtrtxtURI = util.docserver_get_symbtrtxt(w['mbid'])
        
# on other computer
#         symbtrtxtURI = downloadSymbTr(w['mbid'], outputDir )
        
        if not symbtrtxtURI:
                sys.exit("no symbTr found for work {}".format(w['mbid']) )
        
        # TODO: if symbTr does not have second verse, continue
        

        sectionMetadata = dunya.docserver.get_document_as_json(w['mbid'], "metadata", "metadata", 1, version="0.1")
                
        #### alternative if sectionMetadata not found
#         from symbtrdataextractor import extractor
#         autoSegBounds = ''
#         symbtrtxtURINoExt = os.path.splitext(os.path.basename(symbtrtxtURI))[0]
#         sectionMetadataURI, isDataValid = extractor.extract(symbtrtxtURI, symbtrname=symbtrtxtURINoExt, seg_note_idx=autoSegBounds,
#                             mbid=w['mbid'], extract_all_labels=False, melody_sim_thres=0.25, 
#                             lyrics_sim_thres=0.25, get_recording_rels=False)
        
        
     
        
        if WITH_SECTION_ANNOTATIONS:    
            #### get section annotation file: TODO: create a makam/extractor instead 
            sectionAnnosDict = get_section_annotaions_dict(musicbrainzid, outputDir) 
            sectionLinksDict = sectionAnnosDict
        else:
            sectionLinksDict = dunya.docserver.get_document_as_json(musicbrainzid, "scorealign", "sectionlinks", 1, version="0.2")
            
        extractedPitch = dunya.docserver.get_document_as_json(musicbrainzid, "initialmakampitch", "pitch", 1, version="0.6")
         
        
#  on dunya server       
        wavFileURI, created = util.docserver_get_wav_filename(musicbrainzid)

# on other computer         
#         wavFileURI = download_wav(musicbrainzid, outputDir)



        wavFileURIMono = stereoToMono(wavFileURI)               
        totalDetectedTokenList, sectionLinksDict = alignRecording(symbtrtxtURI, sectionMetadata, sectionLinksDict, wavFileURIMono, extractedPitch, outputDir, WITH_SECTION_ANNOTATIONS)

        ret = {'alignedLyricsSyllables':{}, 'sectionlinks':{} }
        ret['alignedLyricsSyllables'] = totalDetectedTokenList
        ret['sectionlinks'] = sectionLinksDict
        return ret


def get_section_annotaions_dict( musicbrainzid, outputDir):
        URL = 'https://raw.githubusercontent.com/georgid/turkish_makam_section_dataset/master/audio_metadata/' + musicbrainzid + '.json'
        sectionAnnosURI = os.path.join(outputDir, musicbrainzid + '.json')
        if not os.path.isfile(sectionAnnosURI):
            print "fetching sections  annotation from URL {}...".format(URL)
            fetchFileFromURL(URL, sectionAnnosURI)
        with open(sectionAnnosURI) as f3:
            sectionAnnosDict = json.load(f3) # use annotations instead of links
        return sectionAnnosDict

def fetchFileFromURL(URL, outputFileURI):
        response = urllib2.urlopen(URL)
        a = response.read()
        with open(outputFileURI,'w') as f:
            f.write(a)

if __name__=='__main__':
    la = LyricsAlign()
    la.run('727cff89-392f-4d15-926d-63b2697d7f3f','b')   
        
