import numpy

import compmusic.extractors

from tomato.audio.predominantmelody import PredominantMelody
from tomato.audio.pitchdistribution import PitchDistribution


class AndalusianPitch(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "andalusianpitch"
    _output = {
        "pitch": {"extension": "json", "mimetype": "application/json"},
        "pitch_distribution": {"extension": "json", "mimetype": "application/json"},
    }

    def run(self, musicbrainzid, fname):
        predominant_melody = PredominantMelody()

        features = predominant_melody.extract(fname)

        pitch = features.get('pitch', None)
        if pitch:
            pitch = list(numpy.array(pitch)[:, 1])

        pitch_distribution = PitchDistribution.from_hz_pitch(pitch)
        pitch_distribution.cent_to_hz()

        return {"pitch": pitch, "pitch_distribution": pitch_distribution.vals}
