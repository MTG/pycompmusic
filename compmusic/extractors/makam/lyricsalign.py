import os
import sys
from compmusic.extractors.wav import Mp3ToWav
import subprocess
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir,  os.path.pardir,  os.path.pardir,  os.path.pardir)) 
pathAlignmentDur = os.path.join(parentDir, 'AlignmentDuration')
if pathAlignmentDur not in sys.path:
    sys.path.append(pathAlignmentDur)


import compmusic.extractors
# from docserver import util
from compmusic import dunya
from compmusic.dunya import makam
import tempfile
import essentia.standard

from align.LyricsAligner  import constructSymbTrTxtURI, alignRecording

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
        #symbtrtxtURI = util.docserver_get_symbtrtxt(w['mbid'])
        
        URI_dataset = '/Users/joro/Downloads/turkish-makam-lyrics-2-audio-test-data-synthesis/'
        symbtrtxtURI, symbTrCompositionName  = constructSymbTrTxtURI(URI_dataset, w['mbid'])
        
        if not symbtrtxtURI:
                return
        
        # TODO: if symbTr does not have second verse, continue
        sectionLinks = dunya.docserver.get_document_as_json(musicbrainzid, "scorealign", "sectionlinks", 1, version="0.2")

        sectionMetadataURI = dunya.docserver.get_document_as_json(w['mbid'], "metadata", "metadata", 1, version="0.1")
        
        extractedPitch = dunya.docserver.get_document_as_json(musicbrainzid, "initialmakampitch", "pitch", 1, version="0.6")
         
        outputDir = tempfile.mkdtemp()
        
#  on dunya server       
#         wavFileURI, created = util.docserver_get_wav_filename(musicbrainzid)

# on other computer         
        wavFileURI = self.download_wav(musicbrainzid, outputDir)
               
        
        totalDetectedTokenList = alignRecording(symbtrtxtURI, sectionMetadataURI, sectionLinks, wavFileURI, extractedPitch, outputDir)

        ret = {'alignedLyricsSyllables':{} }
        ret['alignedLyricsSyllables'] = totalDetectedTokenList
        return ret


    def download_wav(self, musicbrainzid, outputDir):
        mp3FileURI = dunya.makam.download_mp3(musicbrainzid, outputDir)
    ###### mp3 to Wav: way 1
    #         newName = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.mp3')
    #         os.rename(mp3FileURI, newName )
    #         mp3ToWav = Mp3ToWav()
    #         wavFileURI = mp3ToWav.run('dummyMBID', newName)
        
        ###### mp3 to Wav: way 2
        wavFileURI = os.path.splitext(mp3FileURI)[0] + '.wav'
        pipe = subprocess.Popen(['/usr/local/bin/ffmpeg', '-i', mp3FileURI, wavFileURI])
        pipe.wait()
    
    ### stereo to mono
        sampleRate = 44100
        loader = essentia.standard.MonoLoader(filename=wavFileURI, sampleRate=sampleRate)
        audio = loader()
        monoWriter = essentia.standard.MonoWriter(filename=wavFileURI)
        monoWriter(audio)
        return wavFileURI

# TODO: delete output        
#         if os.path.isfile(os.path.join(output, 'sectionLinks.json')):
#                 os.remove(os.path.join(output, 'sectionLinks.json'))
        
if __name__=='__main__':
        la = LyricsAlign()
        la.run('b49c633c-5059-4658-a6e0-9f84a1ffb08b', 'testName') 
        
