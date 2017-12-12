import json
import os
import tempfile
import urllib2

import pydub
from symbtrsynthesis.adaptivesynthesizer import AdaptiveSynthesizer
from symbtrsynthesis.musicxmlreader import MusicXMLReader

import compmusic.dunya.conn
import compmusic.extractors
from compmusic import dunya
from settings import token

dunya.set_token(token)


class ScoreSynthesis(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "symbtrxml"
    _slug = "synthesis"
    _output = {
        'mp3': {"extension": "mp3", "mimetype": "audio/mp3",
                "parts": True},
        'onsets': {"extension": "json", "mimetype": "application/json"}
    }

    @staticmethod
    def get_dataset():
        response = urllib2.urlopen(
            'https://raw.githubusercontent.com/MTG/otmm_tuning_intonation'
            '_dataset/atli2017synthesis_fma/dataset.json')
        return json.loads(response.read())

    def run(self, workid, fname):
        # get metadata
        metadata = json.loads(compmusic.dunya.docserver.file_for_document(
            workid, 'scoreanalysis', 'metadata'))
        makam = metadata['makam']['attribute_key']

        # get symbtr slug
        symbtr_slug = compmusic.dunya.makam.get_symbtr(workid)['name']

        # read musicxml
        (measures, makam_dummy, usul, form, time_sigs, keysig, work_title,
         composer, lyricist, bpm, tnc_sym) = MusicXMLReader.read(fname)

        # synthesize according to AEU theory
        mp3s = []
        audio_temp, onsets = self.synth(bpm, measures, tnc_sym, symbtr_slug,
                                        None)
        mp3s.append(audio_temp)

        # get the recordings in the tuning intonation dataset
        dataset = self.get_dataset()

        # check if it is in selected makams
        if makam in dataset.keys():
            recids = dataset[makam]
            for recid in recids:
                # get the mbid from the musicbrainz url
                mbid = os.path.split(recid)[-1]

                audio_temp, onsets = self.synth(
                    bpm, measures, tnc_sym, symbtr_slug, mbid)
                mp3s.append(audio_temp)

        return {'mp3': mp3s, 'onsets': onsets}

    @staticmethod
    def synth(bpm, measures, tnc_sym, work_title, mbid=None):
        try:  # load the tuning
            stablenotes = json.loads(compmusic.dunya.file_for_document(
                mbid, 'audioanalysis', 'note_models'))
        except dunya.conn.HTTPError:
            stablenotes = None

        # synthesize according to the given tuning
        audio_wav, onsets = AdaptiveSynthesizer.synth_from_tuning(
            measures=measures, bpm=bpm, stable_notes=stablenotes,
            tonic_sym=tnc_sym, synth_type='karplus', verbose=True)

        # mp3 conversion
        audio_obj = pydub.AudioSegment(data=audio_wav)

        fp, tmpname = tempfile.mkstemp(".mp3")
        os.close(fp)

        # export mp3
        if mbid is None:
            comment = 'Synth wrt AEU'
        else:
            comment = 'Synth wrt %s' % mbid

        tags = {'title': work_title, 'comments': comment}
        audio_obj.export(tmpname, format='mp3', tags=tags)

        audio = open(tmpname, "rb").read()
        os.unlink(tmpname)

        return audio, onsets
