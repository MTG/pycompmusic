from __future__ import division
from os.path import basename
import numpy as np
import pickle
from glob import glob


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
        #   print max(sum(A), sum(B))
        #   print "Probabilities do not sum to 1."
        #   return np.NaN
        if x.size != y.size:
            print "Arguments are of different length."
            return np.NaN
        return (np.dot(x, np.log2(x)-np.log2(y))+np.dot(y, np.log2(y)-np.log2(x)))/2.0

    def compute_average_hist(self, paths_to_pitch_files, tonics, octave_folded=True, bins=1200):
        """
        Computes average histogram for a list of given pitch files.
        The pitch values are expected to be in hertz.
        """
        all_cents = []
        for i in xrange(len(paths_to_pitch_files)):
            filepath = paths_to_pitch_files[i]
            data = np.loadtxt(filepath)

            if data is None:
                raise Exception("Pitch data not received.")

            #Histogram
            valid_pitch = data[:, 1]
            tonic = tonics[i]
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

    def serialize_average_hist(self):
        pickle.dump(self.average_hist, file(self.path_to_raaga_profiles + "/" + self.name + ".pickle", "w"))

    def generate_image(self, x, y):
        pass

    def similar_raagas(self, n=5):
        all_paths = glob(self.path_to_raaga_profiles + "/*.pickle")
        source_path = self.path_to_raaga_profiles + "/" + self.name + ".pickle"
        all_paths.remove(source_path)

        distances = []
        if self.average_hist is None:
            self.average_hist = pickle.load(source_path)

        for p in all_paths:
            data = pickle.load(p)
            distance = self.kldiv(self.average_hist[:, 1], data[:, 1])
            distances.append([basename[p][:-7], distance])

        distances = sorted(distances, key=lambda x: x[1])
        distances = np.array(distances)
        return distances[:n, 0]

if __name__ == "__main__":
    import yaml
    import sys
    sys.path.append("/media/CompMusic/audio/users/gkoduri/workspace/PhD/scripts")
    import utils as u

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
    #    print mbid, raaga
    #    if raaga in raaga_mbids.keys():
    #        raaga_mbids[raaga].append([mbid, tonics[i]])
    #    else:
    #        raaga_mbids[raaga] = [[mbid, tonics[i]]]
    #
    #import pickle
    #pickle.dump(raaga_mbids, file("/home/gopal/data/raagaMBIDs.pickle", "w"))

    import pickle
    from os.path import exists
    raaga_mbids = pickle.load(file("/home/gopal/data/raagaMBIDs.pickle"))
    for r in raaga_mbids.keys():
        if exists("/home/gopal/data/features/raagaProfiles/" + r + ".pickle"):
            continue
        print r, len(raaga_mbids[r])
        raaga = Raaga(r, "/home/gopal/data/features/raagaProfiles/")
        pitch_files = ["/home/gopal/data/features/pitch/" + str(i[0]) + ".txt"
                       for i in raaga_mbids[r]]
        tonics = [i[1] for i in raaga_mbids[r]]
        raaga.compute_average_hist(pitch_files, tonics)
        raaga.serialize_average_hist()
