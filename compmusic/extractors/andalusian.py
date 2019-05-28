import numpy
import copy

import compmusic.extractors
from tomato.audio.predominantmelody import PredominantMelody
from tomato.audio.pitchdistribution import PitchDistribution
from tomato.audio.pitchfilter import PitchFilter

class AndalusianPitch(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "andalusianpitch"
    _output = {
        "settings": {"extension": "json", "mimetype": "application/json"},
        "pitch_filt": {"extension": "json", "mimetype": "application/json"},
        "pitch_distribution": {"extension": "json", "mimetype": "application/json"},
    }

    def run(self, musicbrainzid, fname):
        predominant_melody = PredominantMelody()

        results = predominant_melody.extract(fname)
        settings = results['settings'] 
        pitch = results['pitch']

        # Compute pitch filtered
        pitch_filter = PitchFilter()
        pitch_filt= pitch_filter.run(pitch)

        pitch_distribution = PitchDistribution.from_hz_pitch(pitch_filt)
        pitch_distribution.cent_to_hz()
        pitch_distribution = pitch_distribution.vals

        # Skip the time stamp and pitch salience and cast pitch values
        pitch_filt= [int(p[1]) for p in pitch_filt]

        return {"settings": settings, "pitch_filt": pitch_filt, "pitch_distribution": pitch_distribution}

