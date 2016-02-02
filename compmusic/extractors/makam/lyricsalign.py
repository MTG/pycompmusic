import os
import sys
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 
# pathPycompmusic = os.path.join(parentDir, 'pycompmusic')
# if pathPycompmusic not in sys.path:
#     sys.path.append(pathPycompmusic)


import compmusic.extractors
from docserver import util
from compmusic import dunya
from compmusic.dunya import makam
import tempfile

currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )
modelDIR = currDir + '/model/'
HMM_LIST_URI = modelDIR + '/monophones0'
MODEL_URI = modelDIR + '/hmmdefs9gmm9iter'

from align.MakamScore import loadMakamScore, loadMakamScore2
from hmm.examples.main import loadSmallAudioFragment
from align.Decoder import Decoder
from align.SectionLink import SectionLink
dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")


from utilsLyrics.Utilz import writeListOfListToTextFile, writeListToTextFile,\
    getMeanAndStDevError, getSectionNumberFromName, readListOfListTextFile, readListTextFile, getMelodicStructFromName, tokenList2TabFile

from htkparser.htk_converter import HtkConverter


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
        symbtrtxtURI = util.docserver_get_symbtrtxt(w['mbid'])
        if not symbtrtxtURI:
                return
        
        # TODO: if symbTr does not have second verse, continue
        sectionLinksURI = dunya.docserver.get_document_as_json(musicbrainzid, "scorealign", "sectionlinks", 1, version="0.2")

        sectionMetadataURI = dunya.docserver.get_document_as_json(w['mbid'], "metadata", "metadata", 1, version="0.1")
        
        sectionMetadataURI = dunya.docserver.get_document_as_json(w['mbid'], "metadata", "metadata", 1, version="0.1")
        audioFileURI, created = util.docserver_get_wav_filename(musicbrainzid)

        outputDir = tempfile.mkdtemp()
        
        totalDetectedTokenList = alignRecording(symbtrtxtURI, sectionMetadataURI, sectionLinksURI, audioFileURI, outputDir)

        ret = {'alignedLyricsSyllables':{} }
        ret['alignedLyricsSyllables'] = totalDetectedTokenList
        return ret


# TODO: delete output        
#         if os.path.isfile(os.path.join(output, 'sectionLinks.json')):
#                 os.remove(os.path.join(output, 'sectionLinks.json'))
        
        
        
def alignRecording(symbtrtxtURI, sectionMetadataURI, sectionLinksURI, audioFileURI, outputDir):
         
        htkParser = HtkConverter()
        htkParser.load(MODEL_URI, HMM_LIST_URI)
        
        recordingNoExtURI = os.path.splitext(audioFileURI)[0]
        
        sectionLinks = _loadsectionTimeStampsLinksNew( sectionLinksURI) 
        makamScore = loadMakamScore2(symbtrtxtURI, sectionMetadataURI )
        
        tokenLevelAlignedSuffix = '.alignedLyrics' 
        totalDetectedTokenList = []
        for  currSectionLink in sectionLinks :
            
    
            lyrics = makamScore.getLyricsForSection(currSectionLink.melodicStructure)
    
            lyricsStr = lyrics.__str__()
        
            if not lyricsStr or lyricsStr=='None' or  lyricsStr =='_SAZ_':
                print("skipping sectionLink {} with no lyrics ...".format(currSectionLink.melodicStructure))
                continue
            
            withSynthesis = True
            withOracle = False
            oracleLyrics = ''
            usePersistentFiles = True
            detectedTokenList, detectedPath, maxPhiScore = alignSectionLink( lyrics, withSynthesis, withOracle, oracleLyrics, [],  usePersistentFiles, tokenLevelAlignedSuffix, recordingNoExtURI, currSectionLink, htkParser)
            
            totalDetectedTokenList.extend(detectedTokenList)
        
        return totalDetectedTokenList
            
def  alignSectionLink( lyrics, withSynthesis, withOracle, lyricsWithModelsORacle, listNonVocalFragments,   usePersistentFiles, tokenLevelAlignedSuffix,  URIrecordingNoExt, currSectionLink, htkParser):
        '''
        wrapper top-most logic method
        '''
        if withOracle:
    
            # synthesis not needed really in this setting. workaround because without synth takes whole recording  
            withSynthesis = 1
            
    #     read from file result
        URIRecordingChunkResynthesizedNoExt =  URIrecordingNoExt + "_" + str(currSectionLink.beginTs) + '_' + str(currSectionLink.endTs)
        detectedAlignedfileName = URIRecordingChunkResynthesizedNoExt + tokenLevelAlignedSuffix
        if not os.path.isfile(detectedAlignedfileName):
            #     ###### extract audio features
            lyricsWithModels, obsFeatures, URIrecordingChunk = loadSmallAudioFragment(lyrics,  URIrecordingNoExt, URIRecordingChunkResynthesizedNoExt, bool(withSynthesis), currSectionLink, htkParser)
            
        # DEBUG: score-derived phoneme  durations
    #     lyricsWithModels.printPhonemeNetwork()
    #     lyricsWithModels.printWordsAndStates()
            alpha = 0.97
            decoder = Decoder(lyricsWithModels, URIRecordingChunkResynthesizedNoExt, alpha)
        #  TODO: DEBUG: do not load models
        # decoder = Decoder(lyrics, withModels=False, numStates=86)
        #################### decode
            
            if withOracle:
                detectedTokenList = decoder.decodeWithOracle(lyricsWithModelsORacle, URIRecordingChunkResynthesizedNoExt )
            else:
                detectedTokenList = decoder.decodeAudio(obsFeatures, listNonVocalFragments, usePersistentFiles)
            
            phiOptPath = decoder.path.phiOptPath
            detectedPath = decoder.path.pathRaw
            tokenList2TabFile(detectedTokenList, URIRecordingChunkResynthesizedNoExt, tokenLevelAlignedSuffix, currSectionLink.beginTs)
         
           
            
        ### VISUALIZE result 
    #         decoder.lyricsWithModels.printWordsAndStatesAndDurations(decoder.path)
        
        else:   
                print "{} already exists. No decoding".format(detectedAlignedfileName)
                detectedTokenList = readListOfListTextFile(detectedAlignedfileName)
                if withOracle:
                    outputURI = URIRecordingChunkResynthesizedNoExt + '.path_oracle'
                else:
                    outputURI = URIRecordingChunkResynthesizedNoExt + '.path'
                
                detectedPath = readListTextFile(outputURI)
                
                # TODO: store persistently
                phiOptPath = 0
       
    
        return detectedTokenList, detectedPath, phiOptPath


def _loadsectionTimeStampsLinksNew(URILinkedSectionsFile):
        import json
        with open(URILinkedSectionsFile) as b:
            sectionLinks = json.load(b)
    
        sectionsLinks = []               
        sectionLinks = sectionLinks['links']
        for sectionAnno in sectionLinks:
                        
                        melodicStruct = sectionAnno['name']
                        
                        beginTimeStr = str(sectionAnno['time'][0])
                        beginTimeStr = beginTimeStr.replace("[","")
                        beginTimeStr = beginTimeStr.replace("]","")
                        beginTs =  float(beginTimeStr)
                            
                        endTimeStr = str(sectionAnno['time'][1])
                        endTimeStr = endTimeStr.replace("[","")
                        endTimeStr = endTimeStr.replace("]","")
                        endTs =  float(endTimeStr)
                        currSectionLink = SectionLink (melodicStruct, beginTs, endTs) 
                        sectionsLinks.append(currSectionLink )
                    
        return sectionsLinks
