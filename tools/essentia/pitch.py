import essentia.standard as es
import sys
import numpy as np
from os.path import exists

#usage: python pitch.py pitchDir wavFiles

pitchDir = sys.argv[1].rstrip("/")
wavFiles = sys.argv[2:]
print pitchDir

for f in wavFiles:
    if ".wav" not in f.lower(): continue
    
    mbid = f.split("/")[-1][:-4]
    if exists(pitchDir+"/"+mbid+".txt"): continue

    print mbid
    loader = es.EasyLoader(filename=f, sampleRate=44100)
    equalLoudness = es.EqualLoudness(sampleRate=44100)
    audio = loader()
    audioDL = equalLoudness(audio)
    pitch = es.PitchPolyphonic(binResolution=1)
    res = pitch(audioDL)
    t = np.linspace(0, len(res[0])*128.0/44100, len(res[0]))
    data = zip(t, res[0], res[1])
    data = np.array(data)
    np.savetxt(pitchDir+"/"+mbid+".txt", data, delimiter="\t")
