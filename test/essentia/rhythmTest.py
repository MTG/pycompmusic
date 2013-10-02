#!/usr/bin/env python
import rhythm
re = rhythm.RhythmExtract()
# fname = '/media/Data/Data/CompMusicDB/Carnatic/audio/Aneesh_Vidyashankar/Pure_Expressions/7_Jagadoddharana.mp3'
fname = '/media/Code/UPFWork/PhD/Data/CMCMDa/mp3/adi/10014_1313_Bhagyadalakshmi.mp3'
results = re.run(fname)
print("All done")