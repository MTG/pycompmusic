
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

import intonation
import numpy as np
from scipy.stats import variation, skew, kurtosis


class IntonationProfile:
    def __init__(self, pitch):
        self.ji_intervals = np.array([-2400, -2289, -2197, -2085, -2014, -1902, -1791,
                                      -1699, -1587, -1516, -1404, -1312, -1200, -1089,
                                      -997, -885, -814, -702, -591, -499, -387, -316,
                                      -204, -112, 0, 111, 203, 315, 386, 498, 609, 701,
                                      813, 884, 996, 1088, 1200, 1311, 1403, 1515,
                                      1586, 1698, 1809, 1901, 2013, 2084, 2196, 2288,
                                      2400, 2511, 2603, 2715, 2786, 2898, 3009, 3101,
                                      3213, 3284, 3396, 3488, 3600, 3711, 3803, 3915,
                                      3986, 4098, 4209, 4301, 4413, 4484, 4596, 4688,
                                      4800])
        self.pitch_obj = intonation.Pitch(pitch[:, 0], pitch[:, 1])
        self.rec = intonation.Recording(self.pitch_obj)
        self.intonation_profile = None

    def compute_profile(self):
        self.rec.label_contours(self.ji_intervals)
        distributions = {}
        for key, segments in self.rec.contour_labels.items():
            distributions[key] = []
            for indices in segments:
                distributions[key].extend(self.pitch_obj.pitch[indices[0]:indices[1]])

        parameters = {}
        for interval, distribution in distributions.items():
            distribution = np.array(distribution)
            # TODO: replace -10000 with whatever the bound is for invalid pitch values in cent scale
            distribution = distribution[distribution >= -10000]
            [n, be] = np.histogram(distribution, bins=1200)
            bc = (be[1:] + be[:-1]) / 2.0
            peak_pos = bc[np.argmax(n)]
            peak_mean = float(np.mean(distribution))
            peak_variance = float(variation(distribution))
            peak_skew = float(skew(distribution))
            peak_kurtosis = float(kurtosis(distribution))
            pearson_skew = float(3.0 * (peak_mean - peak_pos) / np.sqrt(abs(peak_variance)))
            parameters[interval] = {"position": float(peak_pos),
                                    "mean": peak_mean,
                                    "amplitude": float(max(n)),
                                    "variance": peak_variance,
                                    "skew1": peak_skew,
                                    "skew2": pearson_skew,
                                    "kurtosis": peak_kurtosis}
        all_amps = [parameters[interval]["amplitude"] for interval in parameters.keys()]
        peak_amp_sum = sum(all_amps)
        for interval in parameters.keys():
            parameters[interval]["amplitude"] = parameters[interval]["amplitude"] / peak_amp_sum

        self.intonation_profile = parameters
