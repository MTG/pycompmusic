# -*- coding: utf-8 -*-
__author__ = 'sertansenturk'

from symbtrdataextractor import extractor
import compmusic
from compmusic import dunya
dunya.set_token('69ed3d824c4c41f59f0bc853f696a7dd80707779')

class Metadata(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "txt"
    _slug = "metadata"

    _output = {
         "metadata": {"extension": "json", "mimetype": "application/json" }
         }

    def run(self, musicbrainzid, fname):
        symbtr = compmusic.dunya.makam.get_symbtr(musicbrainzid)
        symbtr_fname = symbtr['name'] + ".txt"

        metadata = extractor.extract(fname, symbtr_fname)
         
        return {"metadata": metadata }
