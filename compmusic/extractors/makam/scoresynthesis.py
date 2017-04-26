import json
import urllib2

import compmusic.dunya.conn
import compmusic.dunya.docserver
import compmusic.extractors
import pydub

from symbtrsynthesis.adaptivesynthesizer import AdaptiveSynthesizer
from symbtrsynthesis.musicxmlreader import MusicXMLReader


class ScoreSynthesis(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "symbtrxml"
    _slug = "synthesis"

    def set_settings(self, recid='aeu'):
        self._output = {recid: {'mp3': {"extension": "mp3",
                                        "mimetype": "audio/mp3"},
                                'onsets': {"extension": "json",
                                           "mimetype": "application/json"}}
                        }

    def set_parameters(self, measures, bpm, stablenotes, tnc_sym):
        self.measures = measures
        self.bpm = bpm
        self.stablenotes = stablenotes
        self.tnc_sym = tnc_sym

    def run(self, musicbrainzid, fname):
        try:
            # synthesize
            audio_karplus, onsets_karplus = AdaptiveSynthesizer.synth_from_tuning(
                measures=self.measures, bpm=self.bpm,
                stable_notes=self.stablenotes, tonic_sym=self.tnc_sym,
                synth_type='karplus', verbose=True)

            # mp3 conversion
            audio_obj = pydub.AudioSegment(data=audio_karplus)
            audio_mp3 = audio_obj.export()

            return {musicbrainzid: {'mp3': audio_mp3,
                                    'onsets': onsets_karplus}
                    }

        except compmusic.dunya.conn.HTTPError:
            print(workid, 'is not exist')

if __name__ == "__main__":
    token = ''
    compmusic.dunya.conn.set_token(token)

    # fetch symbtrs
    symbtrs = compmusic.dunya.get_collection('makam-symbtr')['documents']

    response = urllib2.urlopen('https://raw.githubusercontent.com/MTG/otmm_tuning_intonation_dataset/master/dataset.json')
    dataset = json.loads(response.read())
    MAKAMS = dataset.keys()


    synthesizer = ScoreSynthesis()

    for xx, symbtr in enumerate(symbtrs):
        workid = symbtr['external_identifier']

        try:
            # get metadata
            metadata = json.loads(compmusic.dunya.docserver.file_for_document(
                workid, 'scoreanalysis', 'metadata'))
            makam = metadata['makam']['attribute_key']

            # fetch score
            musicxml = compmusic.dunya.docserver.file_for_document(
                recordingid=workid, thetype='score', subtype='xmlscore')

            # read musicxml
            (measures, makam, usul, form, time_sigs, keysig, work_title,
             composer, lyricist, bpm, tnc_sym) = MusicXMLReader.read(musicxml)

            # check if it is in selected makams
            if makam in MAKAMS:
                recids = dataset[makam]
                for recid in recids:
                    stablenotes = json.loads(compmusic.dunya.file_for_document(
                        recid, 'audioanalysis', 'note_models'))

                    synthesizer.set_settings(recid)
                    synthesizer.set_parameters(measures=measures, bpm=bpm,
                                               stablenotes=stablenotes,
                                               tnc_sym=tnc_sym)
                    print(xx, makam, recid)
                    synthesizer.run(recid, None)
            print('aeu', makam)

            synthesizer.set_settings()
            synthesizer.set_parameters(measures=measures, bpm=bpm,
                                       stablenotes=None, tnc_sym=tnc_sym)
            synthesizer.run('aeu', None)

        except compmusic.dunya.conn.HTTPError:
            print(workid, 'is not exist')
