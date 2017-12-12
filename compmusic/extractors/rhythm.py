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

import numpy as np

import compmusic.extractors
import rhythmlib as ap


class RhythmExtract(compmusic.extractors.ExtractorModule):
    _version = "0.3"
    _sourcetype = "mp3"
    _slug = "rhythm"
    _output = {"sections": {"extension": "json", "mimetype": "application/json"},
               "aksharaPeriod": {"extension": "json", "mimetype": "application/json"},
               "aksharaTicks": {"extension": "json", "mimetype": "application/json"},
               "APcurve": {"extension": "json", "mimetype": "application/json"}}

    def run(self, musicbrainzid, fname):
        params = ap.params
        self.logger.info('Started Processing...')
        self.logger.info(fname)
        # Extract Onset functions
        onsFns = ap.getOnsetFunctions(fname)
        onsFn = onsFns[:, 6].copy()
        onsTs = onsFns[:, 0].copy()
        onsFnLow = onsFns[:, 1].copy()
        onsFn = ap.normMax(ap.smoothNovelty(onsFn, params.onsParams.pdSmooth))
        onsFnLow = ap.normMax(ap.smoothNovelty(onsFnLow, params.onsParams.pdSmooth))
        sectStart = np.array([0.0])
        sectEnd = np.array([])
        # Get section boundaries if necessary
        if onsTs[-1] > params.songLenMin:
            offsetIndex = ap.getKritiStartBoundary(onsFnLow, onsTs)
            offsetTime = onsTs[offsetIndex] - onsTs[0]
            sectStart = np.append(sectStart, [offsetTime])
            sectEnd = np.append(sectEnd, [onsTs[offsetIndex] - onsTs[0]])
        else:
            offsetIndex = 0
            offsetTime = onsTs[offsetIndex] - onsTs[0]
        onsFn = onsFn[offsetIndex:]
        onsTs = onsTs[offsetIndex:]
        sectEnd = np.append(sectEnd, [onsTs[-1]])
        # Obtain the tempo, akshara pulse
        # k,v = ap.findpeaks(x=onsFn.copy(), imode = 'n', pmode = 'p', wdTol = params.onsParams.wtol, ampTol = params.onsParams.thresE,prominence = params.onsParams.pkProm)
        TG, TCts, BPM = ap.tempogram_viaDFT(fn=onsFn.copy(), param=params.TGons.params)
        TG = np.abs(ap.normalizeFeature(TG, 2))
        TCRaw = ap.getTempoCurve(TG.copy(), params.TCparams)
        TCperRaw = 60.0 / TCRaw
        mmpFromTC = ap.getMatraPeriodEstimateFromTC(TCperRaw, params.TCparams)
        TCper, TCcorrFlag = ap.correctOctaveErrors(TCperRaw, mmpFromTC, params.TCparams.octCorrectParam)
        TC = 60.0 / TCper
        akCandLocs, akCandTs, akCandWts, akCandTransMat = ap.estimateAksharaCandidates(onsTs, onsFn.copy(), TCper, TCts,
                                                                                       mmpFromTC, params.aksharaParams)
        akCands = params.akCands
        akCands.Locs = akCandLocs
        akCands.ts = akCandTs
        akCands.Wts = akCandWts
        akCands.TransMat = akCandTransMat
        akCands.TransMatCausal = np.triu(akCandTransMat + akCandTransMat.transpose())
        akCands.pers = TCper[ap.getNearestIndices(akCandTs, TCts)]
        aksharaLocs, aksharaTimes = ap.DPSearch(akCands, params.aksharaParams)
        # Correct for all the offsets now and save to a dictionary
        aksharaTimes = aksharaTimes + offsetTime
        TCts = TCts + offsetTime
        secStart = np.array([0.0])
        sections = {"startTime": 0, "endTime": 0, "label": ""}
        sections["startTime"] = np.round(sectStart, params.roundOffLen)
        sections["endTime"] = np.round(sectEnd, params.roundOffLen)
        labelStr = ("Alapana", "Kriti")
        if sectEnd.size == 2:
            sections["label"] = labelStr
        else:
            sections["label"] = labelStr[1]
        TCts = np.round(TCts, params.roundOffLen)
        TCper = np.round(TCper, params.roundOffLen)

        APcurve = [[TCts[t], TCper[t]] for t in range(TCts.size)]
        ticks = np.round(aksharaTimes, params.roundOffLen).tolist()
        ticks = list(set(ticks))

        return {"sections": sections,
                "aksharaPeriod": np.asscalar(np.round(mmpFromTC, params.roundOffLen)),
                "aksharaTicks": ticks,
                "APcurve": APcurve
                }
