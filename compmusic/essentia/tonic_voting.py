#!/usr/bin/env python

import yaml
import DAO as dao
import numpy as np
import sys
from os import listdir
from os.path import basename

db = dao.DAO()

#sys.argv[1] is path to annotations directory

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

def tonics_by_artist(annotations_path=""):
    files = listdir(annotations_path)
    artist_tonics = {}
    for f in files:
        print f
        mbid = basename(f)[:-5]
        annotations = yaml.load(file(annotations_path+"/"+f, "r"))
        if "tonic" not in annotations.keys():
            print "No tonic for", mbid
            continue
        tonic = annotations["tonic"]["computedValue"]
        rec_info = db.getRecordingInfo("uuid", mbid)
        if rec_info == "empty":
            print "No rec info:", mbid
            continue
        if rec_info["artist"]["uuid"] in artist_tonics.keys():
            artist_tonics[rec_info["artist"]["uuid"]].append([mbid, tonic])
        else:
            artist_tonics[rec_info["artist"]["uuid"]] = [[mbid, tonic]]

        #yaml.dump(artist_tonics, file("tonicsByArtist.yaml", "w"), default_flow_style=False)
    return artist_tonics

def vote(artist_tonics):
    #artist_tonics = yaml.load(file("tonicsByArtist.yaml"))
    count = 0
    for artist in artist_tonics.keys():
        data = np.array(artist_tonics[artist])
        data = data[:, 1].astype("float")
        [n, bins] = np.histogram(data)
        max_index = np.argmax(n)
        _median = data[findNearestIndex(data, bins[max_index])]
        for rec in artist_tonics[artist]:
            cents_diff = abs(1200*np.log2(rec[1]/_median))
            if cents_diff > 350:
                rec[1] = float(_median)
                count+=1
    return artist_tonics


if __name__ == "__main__":
    annotations_path = sys.argv[1]
    artist_tonics = tonics_by_artist(annotations_path)
    artist_tonic_voted = vote(artist_tonics)
    yaml.dump(artist_tonics, file("votedTonicsByArtist.yaml", "w"), default_flow_style=False)

