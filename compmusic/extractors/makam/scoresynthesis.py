import json
import urllib2
import os
import tempfile

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

    def set_settings(self):
        response = urllib2.urlopen(
            'https://raw.githubusercontent.com/MTG/otmm_tuning_intonation_'
            'dataset/master/dataset.json')
        self.dataset = json.loads(response.read())

    def run(self, workid, fname):
        # try:
        # get metadata
        metadata = json.loads(compmusic.dunya.docserver.file_for_document(
            workid, 'scoreanalysis', 'metadata'))
        makam = metadata['makam']['attribute_key']

        # fetch score
        musicxml = compmusic.dunya.docserver.file_for_document(
            recordingid=workid, thetype='score', subtype='xmlscore')

        # read musicxml
        (measures, makam_dummy, usul, form, time_sigs, keysig, work_title,
         composer, lyricist, bpm, tnc_sym) = MusicXMLReader.read(musicxml)

        # synthesize according to AEU theory
        self.set_settings()
        audio_mp3, onsets = self.synth(bpm, measures, tnc_sym, None)

        # check if it is in selected makams
        if makam in self.dataset.keys():
            recids = self.dataset[makam]
            for recid in recids:
                # get the mbid from the musicbrainz url
                mbid = os.path.split(recid)[-1]

                # load the tuning analysis
                stablenotes = json.loads(compmusic.dunya.file_for_document(
                    mbid, 'audioanalysis', 'note_models'))

                audio_mp3, onsets = self.synth(
                    bpm, measures, tnc_sym, stablenotes)

        return {'mp3': audio_mp3, 'onsets': onsets}

        # except compmusic.dunya.conn.HTTPError:
        #     print(workid, 'does not exist')

    def synth(self, bpm, measures, tnc_sym, stablenotes=None):
        # synthesize according to the given tuning
        audio_wav, onsets = AdaptiveSynthesizer.synth_from_tuning(
            measures=measures, bpm=bpm, stable_notes=stablenotes,
            tonic_sym=tnc_sym, synth_type='karplus', verbose=True)

        # mp3 conversion
        audio_obj = pydub.AudioSegment(data=audio_wav)

        fp, tmpname = tempfile.mkstemp(".mp3")
        os.close(fp)
        audio_obj.export(tmpname, format='mp3')

        audio = open(tmpname, "rb").read()
        os.unlink(tmpname)
        
        return audio, onsets
