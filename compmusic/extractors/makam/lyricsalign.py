import os
import sys
from compmusic.extractors.wav import Mp3ToWav
# parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir,  os.path.pardir,  os.path.pardir,  os.path.pardir)) 
# pathAlignmentDur = os.path.join(parentDir, 'AlignmentDuration')
# if pathAlignmentDur not in sys.path:
#     sys.path.append(pathAlignmentDur)


import compmusic.extractors
# from docserver import util
from compmusic import dunya
from compmusic.dunya import makam
import tempfile


from align.LyricsAligner  import downloadSymbTr,  alignRecording, download_wav

dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")



class LyricsAlign(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "lyrics-align"
    _output = {
            "alignedLyricsSyllables": {"extension": "json", "mimetype": "application/json"},
            }
    



    def run(self, musicbrainzid, fname):
        
        rec_data = dunya.makam.get_recording(musicbrainzid )
        
        if len(rec_data['works']) == 0:
                raise Exception('No work on recording %s' % musicbrainzid)
        
        if len(rec_data['works']) > 1:
                raise Exception('More than one work for recording %s Not implemented!' % musicbrainzid)
        
        w = rec_data['works'][0]
        outputDir = tempfile.mkdtemp()
# on dunya server
#         symbtrtxtURI = util.docserver_get_symbtrtxt(w['mbid'])
        
# on other computer
        
        symbtrtxtURI = downloadSymbTr(w['mbid'], outputDir )
        
        if not symbtrtxtURI:
                sys.exit("no symbTr found for work {}".format(w['mbid']) )
        
        # TODO: if symbTr does not have second verse, continue
        
        sectionLinks = dunya.docserver.get_document_as_json(musicbrainzid, "scorealign", "sectionlinks", 1, version="0.2")

        sectionMetadataURI = dunya.docserver.get_document_as_json(w['mbid'], "metadata", "metadata", 1, version="0.1")
        
        #### alternative if sectionMetadata not found
#         from symbtrdataextractor import extractor
#         autoSegBounds = ''
#         symbtrtxtURINoExt = os.path.splitext(os.path.basename(symbtrtxtURI))[0]
#         sectionMetadataURI, isDataValid = extractor.extract(symbtrtxtURI, symbtrname=symbtrtxtURINoExt, seg_note_idx=autoSegBounds,
#                             mbid=w['mbid'], extract_all_labels=False, melody_sim_thres=0.25, 
#                             lyrics_sim_thres=0.25, get_recording_rels=False)
        
        
        extractedPitch = dunya.docserver.get_document_as_json(musicbrainzid, "initialmakampitch", "pitch", 1, version="0.6")
         
        
#  on dunya server       
#         wavFileURI, created = util.docserver_get_wav_filename(musicbrainzid)

# on other computer         
        wavFileURI = download_wav(musicbrainzid, outputDir)
               
        
        totalDetectedTokenList = alignRecording(symbtrtxtURI, sectionMetadataURI, sectionLinks, wavFileURI, extractedPitch, outputDir)

        ret = {'alignedLyricsSyllables':{} }
        ret['alignedLyricsSyllables'] = totalDetectedTokenList
        return ret





        
if __name__=='__main__':
        la = LyricsAlign()
        la.run('b49c633c-5059-4658-a6e0-9f84a1ffb08b', 'testName') 
        