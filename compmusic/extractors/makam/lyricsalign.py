# -*- coding: utf-8 -*-
# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/
#
# If you are using this extractor please cite the following paper:
#
# Dzhambazov, G., & Serra X. (2015).  Modeling of Phoneme Durations for Alignment between Polyphonic Audio and Lyrics.
#            Sound and Music Computing Conference 2015.

import sys
import os
import json
import logging
import subprocess
from fetch_tools import getWork, fetchNoteOnsetFile, \
    get_section_annotaions_dict, downloadSymbTr, get_section_metadata_dict, \
    fetch_audio_wav
from fetch_tools import ON_SERVER

parentDir = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir, os.path.pardir, os.path.pardir,
                 os.path.pardir))
pathAlignmentDur = os.path.join(parentDir, 'AlignmentDuration')

if pathAlignmentDur not in sys.path:
    sys.path.append(pathAlignmentDur)

import compmusic.extractors
from compmusic import dunya
from compmusic.dunya import makam
import tempfile

from align.LyricsAligner import LyricsAligner, stereoToMono, loadMakamRecording
from align.ParametersAlgo import ParametersAlgo

ParametersAlgo.FOR_MAKAM = 1
ParametersAlgo.POLYPHONIC = 1
ParametersAlgo.WITH_DURATIONS = 1
ParametersAlgo.DETECTION_TOKEN_LEVEL = 'syllables'
WITH_SECTION_ANNOTATIONS = 1

if ON_SERVER:  # run with dunya-web on /srv/dunya
    PATH_TO_HCOPY = '/srv/htkBuilt/bin/HCopy'

else:
    # run locally for testing
    PATH_TO_HCOPY = '/usr/local/bin/HCopy'

dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")


class LyricsAlign(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "lyrics-align"
    _output = {
        "alignedLyricsSyllables": {"extension": "json", "mimetype": "application/json"},
        "sectionlinks": {"extension": "json", "mimetype": "application/json"},  # rifined section links
    }

    def __init__(self, dataDir=None, hasSecondVerseProblem=None, hasSectionNumberDiscrepancy=None, **kwargs):
        super(LyricsAlign, self).__init__()
        #         self.dataOutputDir = dataOutputDir
        #         self.hasSecondVerseProblem = hasSecondVerseProblem
        #         self.hasSectionNumberDiscrepancy = hasSectionNumberDiscrepancy

        self.dataOutputDir = tempfile.mkdtemp()
        self.hasSecondVerse = False
        self.hasSectionNumberDiscrepancy = False

    def run(self, musicbrainzid, fname):

        #### output
        ret = {'alignedLyricsSyllables': {}, 'sectionlinks': {}}

        recIDoutputDir = os.path.join(self.dataOutputDir, musicbrainzid)
        if not os.path.isdir(recIDoutputDir):
            os.mkdir(recIDoutputDir)

        w = getWork(musicbrainzid)

        # TODO: mark IDs with second verse symbTr missing and get from a separate reposotory 
        # on dunya server. API might be outdated, as some symbtr names are changed. better use line below
        #         symbtrtxtURI = util.docserver_get_symbtrtxt(w['mbid'])

        #  prefer to fetch symbTr directly from github, as Dunya might not be updated with lyrics changes, etc.
        symbtrtxtURI = downloadSymbTr(w['mbid'], recIDoutputDir, self.hasSecondVerse)

        if not symbtrtxtURI:
            sys.exit("no symbTr found for work {}".format(w['mbid']))

        ############ score section metadata
        if WITH_SECTION_ANNOTATIONS:  # becasue complying with  score metadata for symbTr1, on which annotations are done
            dir_ = 'scores/metadata/'
            sectionMetadataDict = get_section_metadata_dict(w['mbid'], dir_, recIDoutputDir,
                                                            self.hasSectionNumberDiscrepancy)
        else:
            sectionMetadataDict = dunya.docserver.get_document_as_json(w['mbid'], "metadata", "metadata", 1,
                                                                       version="0.1")  # NOTE: this is default for note onsets

        ##################### audio section annotation  or result from section linking
        if WITH_SECTION_ANNOTATIONS:  # because complying with section annotations
            try:
                dir_ = 'audio_metadata/'
                sectionLinksDict = get_section_annotaions_dict(musicbrainzid, dir_, self.dataOutputDir,
                                                               self.hasSectionNumberDiscrepancy)
            except Exception as e:
                sys.exit("no section annotations found for audio {} ".format(musicbrainzid))

        else:
            try:
                sectionLinksDict = dunya.docserver.get_document_as_json(musicbrainzid, "joinanalysis", "sections", 1,
                                                                        version="0.2")
            except dunya.conn.HTTPError:
                logging.error("section link {} missing".format(musicbrainzid))
                return ret
            if not sectionLinksDict:
                logging.error("section link {} missing".format(musicbrainzid))
                return ret

        try:
            extractedPitch = dunya.docserver.get_document_as_json(musicbrainzid, "jointanalysis", "pitch", 1,
                                                                  version="0.1")
            extractedPitch = extractedPitch['pitch']
        except Exception as e:
            sys.exit("no initialmakampitch series could be downloaded.  ")

        if ON_SERVER:
            from docserver import util
            wavFileURI, created = util.docserver_get_wav_filename(musicbrainzid)
        #
        else:
            wavFileURI = fetch_audio_wav(self.dataOutputDir, musicbrainzid, ParametersAlgo.POLYPHONIC)

        wavFileURIMono = stereoToMono(wavFileURI)
        if ParametersAlgo.WITH_ORACLE_ONSETS == 1:
            fetchNoteOnsetFile(musicbrainzid, recIDoutputDir, ParametersAlgo.ANNOTATION_RULES_ONSETS_EXT)

        recording = loadMakamRecording(musicbrainzid, wavFileURIMono, symbtrtxtURI, sectionMetadataDict,
                                       sectionLinksDict, WITH_SECTION_ANNOTATIONS)
        lyricsAligner = LyricsAligner(recording, WITH_SECTION_ANNOTATIONS, PATH_TO_HCOPY)

        totalDetectedTokenList, sectionLinksDict = lyricsAligner.alignRecording(extractedPitch, self.dataOutputDir)
        #         lyricsAligner.evalAccuracy()

        ret['alignedLyricsSyllables'] = totalDetectedTokenList
        ret['sectionlinks'] = sectionLinksDict
        print(ret)
        return ret


if __name__ == '__main__':
    #     if len(sys.argv) != 2:
    #         sys.exit('usage: {} <localpath>')

    la = LyricsAlign()
    la.run('727cff89-392f-4d15-926d-63b2697d7f3f', 'b')
#     la.run('567b6a3c-0f08-42f8-b844-e9affdc9d215','b')
