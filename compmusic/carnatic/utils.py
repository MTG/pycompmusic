#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
import yaml
import numpy as np
import DAO as dao
import stringDuplicates as sd
import intonationLib as iL

homeDir = "/media/CompMusic/audio/users/gkoduri/"
annotationDir = homeDir+"data/Features/annotations/"
pitchDir = homeDir+"data/Features/pitch/"

db = dao.DAO()


#Functions to update raagaClusters

def getTag(mbid, tag="raaga"):
    res = db.getRecordingInfo("mbid", mbid)
    newterm = ""
    if res != "empty" and "tags" in res.keys():
        if tag == "raaga":
            #raaga can be labelled as raaga or unknown!
            for tagInfo in res["tags"]:
                if tagInfo["category"] == "unknown":
                    newterm = tagInfo["tag"]
                    if "raagam " in tagInfo["tag"]:
                        newterm = newterm.replace("raagam ", "").strip()
                    elif " raagam" in tagInfo["tag"]:
                        newterm = newterm.replace(" raagam", "").strip()
                    elif "raaga " in tagInfo["tag"]:
                        newterm = newterm.replace("raaga ", "").strip()
                    elif " raaga" in tagInfo["tag"]:
                        newterm = newterm.replace(" raaga", "").strip()
                    elif "ragam " in tagInfo["tag"]:
                        newterm = newterm.replace("ragam ", "").strip()
                    elif " ragam" in tagInfo["tag"]:
                        newterm = newterm.replace("ragam", "").strip()
                    elif "raga " in tagInfo["tag"]:
                        newterm = newterm.replace("raga ", "").strip()
                    elif " raga" in tagInfo["tag"]:
                        newterm = newterm.replace(" raga", "").strip()
                    else:
                        newterm = ""
                elif tagInfo["category"] == "raaga":
                    newterm = tagInfo["tag"]
                elif tagInfo["category"] == "raga":
                    newterm = tagInfo["tag"]
        elif tag == "taala":
            #raaga can be labelled as raaga or unknown!
            for tagInfo in res["tags"]:
                if tagInfo["category"] == "unknown":
                    newterm = tagInfo["tag"]
                    if "taalam " in tagInfo["tag"]:
                        newterm = newterm.replace("taalam ", "").strip()
                    elif " taalam" in tagInfo["tag"]:
                        newterm = newterm.replace(" taalam", "").strip()
                    elif "taala " in tagInfo["tag"]:
                        newterm = newterm.replace("taala ", "").strip()
                    elif " taala" in tagInfo["tag"]:
                        newterm = newterm.replace(" taala", "").strip()
                    elif "talam " in tagInfo["tag"]:
                        newterm = newterm.replace("talam ", "").strip()
                    elif " talam" in tagInfo["tag"]:
                        newterm = newterm.replace("talam", "").strip()
                    elif "tala " in tagInfo["tag"]:
                        newterm = newterm.replace("tala ", "").strip()
                    elif " tala" in tagInfo["tag"]:
                        newterm = newterm.replace(" tala", "").strip()
                    else:
                        newterm = ""
                elif tagInfo["category"] == "taala":
                    newterm = tagInfo["tag"]
                elif tagInfo["category"] == "tala":
                    newterm = tagInfo["tag"]
        return newterm

def dictToUnicode(cluster):
    """
    Sometimes yaml complains about datatypes. Converting to unicode may help.
    This function converts a dictionary of type key:[value1, value2] to unicode.
    """
    uCluster = {}
    for key in cluster.keys():
        ukey = unicode(key).encode("utf-8")
        uvalues = []
        uCluster[ukey] = []
        for value in cluster[key]:
            uValue = unicode(value).encode("utf-8")
            uCluster[ukey].append(uValue)
    return uCluster

def mergeClusters(allClusters, updatedClusters):
    for key, values in updatedClusters.items():
        allClusters[key] = values
    return allClusters

def updateRaagaClusters(raagaClusters, newterms = [], mbids = [], simThresh=0.6):
    """
    newterms: the new raaga terms which need to be synced with raagaClusters, if
    these point to empty list, the function expects a valid mbids list.
    mbids: Those mbids which do not already have a key at raagaMBIDs.yaml
    raagaClusters: The clusters discovered using string matching function, and
    manually corrected. It is a dictionary with keys as actual raaga names and
    values as all the possible spelling variations (including the key!).

    returns just the updated raagaClusters. Check them and sync with the
    raagaClusters already stored on filesystem.

    Once you get updatedClusters, write them to yaml file, make corrections,
    reload it to a dictionary, and call mergeClusters(updatedClusters,
    allClusters)
    """
    if newterms == []:
        if mbids == []:
            print "Either newterms or mbids must be a valid non-empty list!"
            return
        for mbid in mbids:
            newterm = getTag(mbid, tag="raaga")
            if newterm:
                newterms.append(newterm)

        newterms = [i.strip("0123456789()[]-") for i in newterms]
        newterms = np.unique(newterms)
    #return newterms

    oldterms = np.concatenate(raagaClusters.values())
    updatedClusters = []
    for newterm in newterms:
        if newterm in oldterms:
            print newterm, "exists in our cluster\n"
            continue

        similarities = [] #of a new raaga term to each of existing cluster
        for key, values in raagaClusters.items():
            s = 0
            for term in values:
                s += sd.similarity(term, newterm)
            s = s/len(values)
            similarities.append([key, s])
        similarities = np.array(similarities)

        tmp = similarities[:, 1].astype("float")
        maxIndex = np.argmax(tmp)
        if tmp[maxIndex] < simThresh:
            raaga = similarities[maxIndex][0]
            print "Added new cluster for", newterm, "(Nearest cluster was",\
            raaga, ") \n"
            raagaClusters[newterm] = [newterm]
            updatedClusters.append(newterm)
        else:
            raaga = similarities[maxIndex][0]
            raagaClusters[raaga].append(newterm)
            print newterm, "is now part of", raaga, "cluster with",\
            tmp[maxIndex], "confidence\n"
            updatedClusters.append(raaga)

    updatedClusters = np.unique(updatedClusters)
    for key in raagaClusters.keys():
        if key not in updatedClusters:
            raagaClusters.pop(key)

    return raagaClusters


# Functions to set/get raagaMBIDs based on raagaClusters

#so that it loads once when imported!
raagaMBIDs = yaml.load(file(homeDir+"data/raagaMBIDs.yaml"))
def updateRaagaMBIDs(raagaClusters, mbids):
    global raagaMBIDs
    if not raagaMBIDs:
        raagaMBIDs = {}
    oldMBIDs = np.concatenate(raagaMBIDs.values())
    for mbid in mbids:
        if mbid in oldMBIDs:
            continue
        newterm = getTag(mbid, tag="raaga")
        for key, values in raagaClusters.items():
            if newterm in values:
                if key in raagaMBIDs.keys():
                    raagaMBIDs[key].append(mbid)
                else:
                    raagaMBIDs[key] = [mbid]
    yaml.dump(raagaMBIDs, file(homeDir+"data/raagaMBIDs.yaml", "w"))

def raaga(mbid):
    for r in raagaMBIDs.keys():
        if mbid in raagaMBIDs[r]:
            return r

#Other functions which are regularly used in workspace

def pitch(mbid, returnScale="cents", tonic=None, vocal=False):
    """
    Return pitch either in hertz or cent scale. if vocal is set to True, it
    returns pitch corresponding to vocal regions only.

    """
    filepath = pitchDir+mbid+".txt"

    try:
            data = np.loadtxt(filepath, delimiter="\t", dtype="float")
    except:
        raise Exception("Pitch filepath is incorrect")

    if returnScale=="cents":
        if not tonic:
            try:
                annotationFile = annotationDir+mbid+".yaml"
                manualAnnotations = yaml.load(file(annotationFile))
            except:
                raise Exception("The annotations file is missing, or the path is wrong.")
            try:
                tonic = manualAnnotations['tonic']['votedValue']
            except:
                print mbid
                raise Exception("Missing tonic information")

        dataLen = len(data)
        cents = [-10000]*dataLen
        for i in xrange(dataLen):
            if data[i, 1] > 0:
                cents[i] = 1200*np.log2(1.0*data[i,1]/tonic)
            else:
                cents[i] = -10000
        data = zip(data[:, 0], cents)
        return np.array(data)
    else:
        return data[:, :2]

def vocalFilter(data, mbid):
    annotationFile = annotationDir+mbid+".yaml"
    try:
        manualAnnotations = yaml.load(file(annotationFile))
    except:
        print "The annotations file is missing, or the path is wrong. Please override the default argument value if needed. Quitting."
        return
    dataLen = len(data)
    vocalPitch = [min(data[:, 1])]*dataLen
    try:
        vocalSegments = manualAnnotations['vocal']
        for segment in vocalSegments['segments']:
            start = iL.findNearestIndex(data[:,0], segment['start'])
            end = iL.findNearestIndex(data[:,0], segment['end'])
            if end > dataLen:
                end = dataLen
            for i in xrange(start, end):
                    vocalPitch[i] = data[i, 1]
    except:
        vocalPitch = data[:,1]
        print "No annotated information of vocal segments found, returning the pitch unfiltered for", mbid
    data = zip(data[:, 0], vocalPitch) #assigning won't change the original array (passed to function)
    return np.array(data)

# Functions to update taalaClusters

def updateTaalaClusters(taalaClusters, newterms = [], mbids = [], simThresh=0.6):
    """
    newterms: the new taala terms which need to be synced with taalaClusters, if
    these point to empty list, the function expects a valid mbids list.
    mbids: Those mbids which do not already have a key at taalaMBIDs.yaml
    taalaClusters: The clusters discovered using string matching function, and
    manually corrected. It is a dictionary with keys as actual taala names and
    values as all the possible spelling variations (including the key!).

    returns just the updated taalaClusters. Check them and sync with the
    taalaClusters already stored on filesystem.

    Once you get updatedClusters, write them to yaml file, make corrections,
    reload it to a dictionary, and call mergeClusters(updatedClusters,
    allClusters)
    """

    unwantedChars = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "(",\
                    ")", "[", "]", ".", "-", " "]
    if newterms == []:
        if mbids == []:
            print "Either newterms or mbids must be a valid non-empty list!"
            return
        for mbid in mbids:
            newterm = getTag(mbid, tag="taala")
            if newterm:
                newterms.append(newterm)
    newterms = np.unique(newterms)
    #return newterms

    oldterms = np.concatenate(taalaClusters.values())
    updatedClusters = []
    for newterm in newterms:
        if newterm in oldterms:
            print newterm, "exists in our cluster\n"
            continue

        similarities = [] #of a new taala term to each of the existing cluster
        for key, values in taalaClusters.items():
            s = []
            for term in values:
                s.append(sd.similarity(sd.stripChars(term, unwantedChars),\
                                   sd.stripChars(newterm, unwantedChars)))
            #s = s/len(values)
            s = max(s)
            similarities.append([key, s])
        similarities = np.array(similarities)

        tmp = similarities[:, 1].astype("float")
        maxIndex = np.argmax(tmp)
        if tmp[maxIndex] < simThresh:
            taala = similarities[maxIndex][0]
            print "Added new cluster for", newterm, "(Nearest cluster was",\
            taala, " with", tmp[maxIndex], "confidence)\n"
            taalaClusters[newterm] = [newterm]
            updatedClusters.append(newterm)
        else:
            taala = similarities[maxIndex][0]
            taalaClusters[taala].append(newterm)
            print newterm, "is now part of", taala, "cluster with",\
            tmp[maxIndex], "confidence\n"
            updatedClusters.append(taala)

    updatedClusters = np.unique(updatedClusters)
    for key in taalaClusters.keys():
        if key not in updatedClusters:
            taalaClusters.pop(key)

    return taalaClusters

import sys
if __name__=="__main__":
    taalas = yaml.load(file(sys.argv[1]))
    taalaClusters = yaml.load(file(sys.argv[2]))
    res = updateTaalaClusters(taalaClusters, taalas)
    print res
