import compmusic.essentia
import numpy as np
import imagelib as ap

class RhythmExtract(compmusic.essentia.EssentiaModule):
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "rhythm"
    __output__ = {"sections": {"extension": "json", "mimetype": "application/json"},
                    "aksharaPeriod": {"extension": "json", "mimetype": "application/json"},
                    "aksharaTicks": {"extension": "json", "mimetype": "application/json"},
                    "APcurve": {"extension": "json", "mimetype": "application/json"}}

    def run(self, fname):
        params = ap.params
        self.logger.info('Started Processing...')
        self.logger.info(fname)
        # Extract Onset functions
        onsFns = ap.getOnsetFunctions(fname)
        onsFn = onsFns[:,6].copy()
        onsTs = onsFns[:,0].copy()
        onsFnLow = onsFns[:,1].copy()
        onsFn = ap.normMax(ap.smoothNovelty(onsFn,params.onsParams.pdSmooth))
        onsFnLow = ap.normMax(ap.smoothNovelty(onsFnLow,params.onsParams.pdSmooth))
        sectStart = np.array([0.0])
        sectEnd = np.array([])
        # Get section boundaries if necessary
        if onsTs[-1] > params.songLenMin:
            offsetIndex = ap.getKritiStartBoundary(onsFnLow,onsTs)
            offsetTime = onsTs[offsetIndex]-onsTs[0]
            sectStart = np.append(sectStart,[offsetTime])
            sectEnd = np.append(sectEnd,[onsTs[offsetIndex]-onsTs[0]])
        else:
            offsetIndex = 0
            offsetTime = onsTs[offsetIndex]-onsTs[0]
        onsFn = onsFn[offsetIndex:]
        onsTs = onsTs[offsetIndex:]
        sectEnd = np.append(sectEnd,[onsTs[-1]])
        # Obtain the tempo, akshara pulse
        # k,v = ap.findpeaks(x=onsFn.copy(), imode = 'n', pmode = 'p', wdTol = params.onsParams.wtol, ampTol = params.onsParams.thresE,prominence = params.onsParams.pkProm)
        TG, TCts, BPM = ap.tempogram_viaDFT(fn=onsFn.copy(), param = params.TGons.params)
        TG = np.abs(ap.normalizeFeature(TG,2))
        TCRaw = ap.getTempoCurve(TG.copy(),params.TCparams)
        TCperRaw = 60.0/TCRaw
        mmpFromTC = ap.getMatraPeriodEstimateFromTC(TCperRaw,params.TCparams)
        TCper, TCcorrFlag = ap.correctOctaveErrors(TCperRaw,mmpFromTC,params.TCparams.octCorrectParam)
        TC = 60.0/TCper
        akCandLocs, akCandTs, akCandWts, akCandTransMat = ap.estimateAksharaCandidates(onsTs, onsFn.copy(), TCper, TCts, mmpFromTC, params.aksharaParams)
        akCands = params.akCands
        akCands.Locs = akCandLocs
        akCands.ts = akCandTs
        akCands.Wts = akCandWts
        akCands.TransMat = akCandTransMat
        akCands.TransMatCausal = np.triu(akCandTransMat + akCandTransMat.transpose())
        akCands.pers = TCper[ap.getNearestIndices(akCandTs,TCts)]
        aksharaLocs, aksharaTimes = ap.DPSearch(akCands,params.aksharaParams)
        # Correct for all the offsets now and save to a dictionary
        aksharaTimes = aksharaTimes + offsetTime
        TCts = TCts + offsetTime
        secStart = np.array([0.0])
        sections = {"startTime": 0, "endTime": 0, "label": ""}
        sections["startTime"] = np.round(sectStart,params.roundOffLen)
        sections["endTime"] = np.round(sectEnd,params.roundOffLen)
        labelStr = ("Alapana","Kriti")
        if sectEnd.size == 2:
            sections["label"] = labelStr
        else:
            sections["label"] = labelStr[1]
        TCts = np.round(TCts,params.roundOffLen)
        TCper = np.round(TCper,params.roundOffLen)
        APcurve = {TCts[t]:TCper[t] for t in range(TCts.size)}

        return {"sections": sections,
                "aksharaPeriod": np.round(mmpFromTC,params.roundOffLen),
                "aksharaTicks": np.round(aksharaTimes,params.roundOffLen),
                "APcurve": APcurve
                }
