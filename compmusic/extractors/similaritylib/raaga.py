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

from __future__ import print_function
from __future__ import division
from os.path import basename
import numpy as np
import pickle
import pypeaks
from glob import glob
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter


class Raaga:
    def __init__(self, name, path_to_raaga_profiles):
        self.name = name
        self.average_hist = None
        self.average_profile = None
        self.path_to_raaga_profiles = path_to_raaga_profiles

    @staticmethod
    def kldiv(x, y):
        """
        Calculates the KL divergence D(A||B) between the
        normalized distributions A and B.

        Usage: d = kldiv(A,B)
        """
        eps = np.finfo(float).eps*2*len(x)
        x = np.array(x)+eps
        y = np.array(y)+eps
        #eps = 0.01
        #if max(sum(A), sum(B)) > 1+eps:
        #   print(max(sum(A), sum(B)))
        #   print("Probabilities do not sum to 1.")
        #   return np.NaN
        if x.size != y.size:
            print("Arguments are of different length.")
            return np.NaN
        return (np.dot(x, np.log2(x)-np.log2(y))+np.dot(y, np.log2(y)-np.log2(x)))/2.0

    def load_average_hist(self):
        self.average_hist = pickle.load(open(self.path_to_raaga_profiles.rstrip("/") + "/" + self.name + ".pickle"))

    def compute_average_hist(self, paths_to_pitch_files, tonics, octave_folded=True, bins=1200):
        pitches = []
        for i in xrange(len(paths_to_pitch_files)):
            filepath = paths_to_pitch_files[i]
            data = np.loadtxt(filepath)

            if data is None:
                raise Exception("Pitch data not received.")
            pitches.append(data)

        compute_average_hist_data(pitches, tonics, octave_folded, bins)


    def compute_average_hist_data(self, pitches, tonics, octave_folded=True, bins=1200):
        """
        Computes average histogram for a list of given pitches.
        Pitch data should be a numpy array. `tonics` are the tonics for each
        pitch array.
        The pitch values are expected to be in hertz.
        """
        all_cents = []
        for data, tonic in zip(pitches, tonics):
            #Histogram
            valid_pitch = data[:, 1]
            valid_pitch = [1200*np.log2(i/tonic) for i in valid_pitch if i > 0]
            if octave_folded:
                valid_pitch = map(lambda x: int(x % 1200), valid_pitch)

            all_cents.extend(valid_pitch)
        if not bins:
            bins = max(all_cents)-min(all_cents)

        n, bin_edges = np.histogram(all_cents, bins, normed=True)
        bin_centers = 0.5*(bin_edges[1:]+bin_edges[:-1])
        n = n.reshape(len(n), 1)
        bin_centers = bin_centers.reshape(len(bin_centers), 1)
        self.average_hist = np.append(n, bin_centers, axis=1)

    @staticmethod
    def find_nearest_index(arr, value):
        """
        For a given value, the function finds the nearest value
        in the array and returns its index.
        :param arr: An array of numbers
        :param value: value to be looked up
        """
        arr = np.array(arr)
        index = (np.abs(arr-value)).argmin()
        return index

    def serialize_average_hist(self):
        pickle.dump(self.average_hist, file(self.path_to_raaga_profiles + "/" + self.name + ".pickle", "w"))

    def generate_image(self, filepath, smoothness=7, size=400):
        x = self.average_hist[:, 1]
        y = self.average_hist[:, 0]
        x -= 50
        y = np.concatenate((y[-50:], y[:-50]))

        #The following is for plotting xticks at proper peak locations
        locs = np.arange(0, 1200, 100)
        labels = ["Sa", "Ri1", "Ri2\nGa1", "Ri3\nGa2", "Ga3", "Ma1", "Ma2", "Pa", "Da1", "Da2\nNi1", "Da3\nNi2", "Ni3"]
        label_map = {}
        for i in xrange(len(locs)):
            label_map[locs[i]] = labels[i]

        dobj = pypeaks.Data(x, y, smoothness=7)
        dobj.get_peaks(peak_amp_thresh=6e-04)
        actual_locs = np.sort(dobj.peaks["peaks"][0])
        for i in xrange(len(actual_locs)):
            actual_locs[i] = locs[self.find_nearest_index(locs, actual_locs[i])]
        actual_labels = [label_map[i] for i in actual_locs]

        y = gaussian_filter(y, smoothness)
        plt.ioff()
        fig = plt.figure()
        fig.set_size_inches(5, 4.5)
        fig.set_dpi(300)

        plt.plot(x, y, "k-")
        plt.xlim(-50, 1150)

        plt.xticks(actual_locs, actual_labels, fontsize=10)
        plt.yticks([])

        plt.savefig(filepath, bbox_inches="tight")
        plt.close(fig)

    def similar_raagas(self, n=5):
        all_paths = glob(self.path_to_raaga_profiles + "/*.pickle")
        source_path = self.path_to_raaga_profiles.rstrip("/") + "/" + self.name + ".pickle"
        all_paths.remove(source_path)

        distances = []
        if self.average_hist is None:
            self.average_hist = pickle.load(source_path)

        for p in all_paths:
            data = pickle.load(file(p))
            distance = self.kldiv(self.average_hist[:, 0], data[:, 0])
            distances.append([basename(p)[:-7], distance])

        distances = sorted(distances, key=lambda x: x[1])
        distances = np.array(distances)

        #print(self.name, distances[:n])
        return distances[:n]

if __name__ == "__main__":
    import yaml
    import sys
    sys.path.append("/media/CompMusic/audio/users/gkoduri/workspace/PhD/scripts")
    import utils as u

    #BLOCK TO CREATE MAP BETWEEN RAAGA NAMES AND MBIDS
    #raaga_map = yaml.load(file("/home/gopal/data/raagaClusters.yaml"))
    #pitch_files = glob("/home/gopal/data/features/pitch/*.txt")
    #mbids = [basename(mbid)[:-4] for mbid in pitch_files]
    #
    #w = u.Workspace("/home/gopal/data/features/",
    #                "/home/gopal/data/features/annotations/",
    #                "/home/gopal/data/audio/Carnatic/metadata/Carnatic.yaml")
    #tonics = [w.tonic(mbid) for mbid in mbids]
    #
    #raaga_mbids = {}
    #for i in xrange(len(mbids)):
    #    if tonics[i] is None:
    #        continue
    #
    #    mbid = mbids[i]
    #    tag = w.get_tag("raaga", mbid)
    #    raaga = w.get_raaga(tag, raaga_map)
    #    if raaga == "":
    #        continue
    #
    #    print(mbid, raaga)
    #    if raaga in raaga_mbids.keys():
    #        raaga_mbids[raaga].append([mbid, tonics[i]])
    #    else:
    #        raaga_mbids[raaga] = [[mbid, tonics[i]]]
    #
    #import pickle
    #pickle.dump(raaga_mbids, file("/home/gopal/data/raagaMBIDs.pickle", "w"))

    #BLOCK TO COMPUTE AVERAGE HISTOGRAMS
    import pickle
    from os.path import exists
    raaga_mbids = pickle.load(file("/home/gopal/data/raagaMBIDs.pickle"))
    raaga_mbids.pop("Unknown")

    #for r in raaga_mbids.keys():
    #    if exists("/home/gopal/data/features/raagaProfiles/" + r + ".pickle"):
    #        continue
    #    print(r, len(raaga_mbids[r]))
    #    raaga = Raaga(r, "/home/gopal/data/features/raagaProfiles/")
    #    pitch_files = ["/home/gopal/data/features/pitch/" + str(i[0]) + ".txt"
    #                   for i in raaga_mbids[r]]
    #    tonics = [i[1] for i in raaga_mbids[r]]
    #    raaga.compute_average_hist(pitch_files, tonics)
    #    raaga.serialize_average_hist()

    #BLOCK TO COMPUTE SIMILARITY MAP
    data = np.loadtxt("/home/gopal/data/raagaIndices.txt", delimiter=",", dtype="str")
    raaga_indices = {}
    for row in data:
        raaga_indices[row[1]] = row[0]
    similarity_map = {}
    raagas = raaga_mbids.keys()
    for i in xrange(len(raagas)):
        if not exists("/home/gopal/data/features/raagaProfiles/" + raagas[i] + ".pickle") or raagas[i] not in raaga_indices.keys():
            continue
        similarity_map[raagas[i]] = []
        x = pickle.load(file("/home/gopal/data/features/raagaProfiles/" + raagas[i] + ".pickle"))
        raaga = Raaga(raagas[i], "/home/gopal/data/features/raagaProfiles/")
        raaga.average_hist = x
        res = raaga.similar_raagas(5)
        similarity_map[raaga.name] = res
        print(raaga.name, res)

    pickle.dump(similarity_map,
              file("/home/gopal/data/features/raagaProfiles/similarity_map.yaml", "w"))

    #BLOCK TO GET IMAGES
    smap = pickle.load(file("/home/gopal/data/features/raagaProfiles/similarity_map.pickle"))
    raagas = list(smap["huseni"][:, 0])
    raagas.append("huseni")
    for i in raagas:
        raaga = Raaga(i, "/home/gopal/data/features/raagaProfiles")
        raaga.load_average_hist()
        raaga.generate_image("/home/gopal/data/features/raagaImages/"+i+".png")
