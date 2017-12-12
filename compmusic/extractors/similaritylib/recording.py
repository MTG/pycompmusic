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
import numpy as np

ji_intervals = np.array([-2400, -2289, -2197, -2085, -2014, -1902, -1791,
                         -1699, -1587, -1516, -1404, -1312, -1200, -1089,
                         -997, -885, -814, -702, -591, -499, -387, -316,
                         -204, -112, 0, 111, 203, 315, 386, 498, 609, 701,
                         813, 884, 996, 1088, 1200, 1311, 1403, 1515,
                         1586, 1698, 1809, 1901, 2013, 2084, 2196, 2288,
                         2400, 2511, 2603, 2715, 2786, 2898, 3009, 3101,
                         3213, 3284, 3396, 3488, 3600, 3711, 3803, 3915,
                         3986, 4098, 4209, 4301, 4413, 4484, 4596, 4688,
                         4800])

def pad(profile, _min=-2400, _max=4800):
    #Fill zeros for features from intervals absent in the profile
    for interval in ji_intervals:
        if interval not in profile.keys():
            profile[interval] = {"position": 0,
                                 "mean": 0,
                                 "amplitude": 0,
                                 "variance": 0,
                                 "skew1": 0,
                                 "skew2": 0,
                                 "kurtosis": 0}

    #Remove intervals beyond the desirable range
    for interval in profile.keys():
        if _max < int(interval) < _min:
            profile.pop(interval)

    return profile

def distance(profile1, profile2):
    profile1 = pad(profile1)
    profile2 = pad(profile2)

    keys = profile1.keys()
    try:
        keys.pop("skew1")
    except KeyError:
        pass
    v1 = [profile1[k] for k in keys]
    v2 = [profile2[k] for k in keys]
    return np.linalg.norm(v1-v2)

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
        print("Arguments are of different length.")
        return np.NaN
    return (np.dot(x, np.log2(x)-np.log2(y))+np.dot(y, np.log2(y)-np.log2(x)))/2.0
