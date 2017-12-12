# -*- coding: utf-8 -*-
__author__ = 'sertansenturk'

from __future__ import print_function

from tomato.symbolic.symbtranalyzer import SymbTrAnalyzer

import compmusic
from compmusic import dunya
from settings import token

dunya.set_token(token)


class ScoreAnalysis(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "symbtrtxt"
    _slug = "scoreanalysis"
    _output = {
        "metadata": {"extension": "json", "mimetype": "application/json"}
    }

    def run(self, musicbrainzid, fname):
        symbtr = compmusic.dunya.makam.get_symbtr(musicbrainzid)
        symbtr_fname = symbtr['name']
        scoreAnalyzer = SymbTrAnalyzer(verbose=True)

        mu2_file = fname.replace('symbtrtxt', 'symbtrmu2').replace('.txt', '.mu2')
        print(mu2_file)
        # score analysis
        score_features, boundaries, work_mbid = scoreAnalyzer.analyze(
            fname, mu2_file, symbtr_name=symbtr_fname)
        return {'metadata': score_features}
