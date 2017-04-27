import json
import urllib2

from compmusic import dunya
from settings import token
import compmusic.dunya.conn
import compmusic.extractors
import pydub

from symbtrsynthesis.adaptivesynthesizer import AdaptiveSynthesizer
from symbtrsynthesis.musicxmlreader import MusicXMLReader

dunya.set_token(token)

class ScoreSynthesis(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "symbtrxml"
    _slug = "synthesis"
    _output = {
            'mp3': {"extension": "mp3", "mimetype": "audio/mp3"},
            'onsets': {"extension": "json", "mimetype": "application/json"}
    }

    def set_settings(self, recid='aeu'):
        response = urllib2.urlopen(
            'https://raw.githubusercontent.com/MTG/otmm_tuning_intonation_'
            'dataset/master/dataset.json')
        self.dataset = json.loads(response.read())

    def run(self, workid, fname):
        try:
            # get metadata
            metadata = json.loads(dunya.docserver.file_for_document(
                workid, 'scoreanalysis', 'metadata'))
            makam = metadata['makam']['attribute_key']

            # fetch score
            musicxml = dunya.docserver.file_for_document(
                recordingid=workid, thetype='score', subtype='xmlscore')

            # read musicxml
            (measures, makam, usul, form, time_sigs, keysig, work_title,
             composer, lyricist, bpm, tnc_sym) = MusicXMLReader.read(musicxml)

            # synthesize according to AEU theory
            self.set_settings()
            audio_mp3, onsets = self.synth(bpm, measures, tnc_sym, None)

            # check if it is in selected makams
            if makam in self.dataset.keys():
                recids = self.dataset[makam]
                for recid in recids:
                    stablenotes = json.loads(compmusic.dunya.file_for_document(
                        recid, 'audioanalysis', 'note_models'))

                    self.set_settings(recid)

                    audio_mp3, onsets = self.synth(
                        bpm, measures, tnc_sym, stablenotes)

            return {'mp3': audio_mp3, 'onsets': onsets}

        except compmusic.dunya.conn.HTTPError:
            print(workid, 'does not exist')

    def synth(self, bpm, measures, tnc_sym, stablenotes=None):
        # synthesize according to the given tuning
        audio_karplus, onsets_karplus = AdaptiveSynthesizer. \
            synth_from_tuning(measures=measures, bpm=bpm,
                              stable_notes=stablenotes,
                              tonic_sym=tnc_sym, synth_type='karplus',
                              verbose=True)
        # mp3 conversion
        audio_obj = pydub.AudioSegment(data=audio_karplus)
        audio_mp3 = audio_obj.export()

        return audio_mp3, onsets_karplus
