# -*- coding: utf-8 -*-
__author__ = 'sertansenturk'

from symbtrdataextractor import extractor
import compmusic
import json
from docserver import util
from compmusic import dunya
dunya.set_token('69ed3d824c4c41f59f0bc853f696a7dd80707779')

class Metadata(compmusic.extractors.ExtractorModule):
    _version = "0.2"
    _sourcetype = "symbtrtxt"
    _slug = "metadata"
    _output = {
         "metadata": {"extension": "json", "mimetype": "application/json" }
         }

    def run(self, musicbrainzid, fname):
        symbtr = compmusic.dunya.makam.get_symbtr(musicbrainzid)
        symbtr_fname = symbtr['name'] 

        segmentsfile = util.docserver_get_filename(musicbrainzid, "segmentphraseseg", "segments", version="0.1")
        
        try:  # check if automatic phrase segmentation is available
            bounds = json.load(open(segmentsfile, 'r'))['boundary_noteIdx']
        except TypeError:  # not available
            bounds = []

        metadata = extractor.extract(fname, symbtr_fname, bounds)
         
        return {"metadata": metadata }
