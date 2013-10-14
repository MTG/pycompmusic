#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
import yaml
import numpy as np
import DAO as dao
import stringDuplicates as sd
import csv

db = dao.DAO()


class FuzzyMatch:
    def __init__(self, yaml_map_file, clusters_csv_file, tag="raaga", similarity_threshold=0.6, log="log.txt"):
        self.yaml_map = yaml.load(file(yaml_map_file))
        self.clusters = {}
        self.clusters_csv_file = clusters_csv_file
        self.load_clusters()

        self.all_terms = []
        self.tag = tag
        self.similarity_threshold = similarity_threshold
        self.log_file = file(log, "w")

    def load_clusters(self):
        data = np.loadtxt(self.clusters_csv_file, dtype="str", delimiter=",")
        for row in data:
            terms = list(np.unique(row))
            try:
                terms.remove('')
            except ValueError:
                pass
            self.clusters[row[0]] = terms

    def get_tag(self, mbid):
        result = db.getRecordingInfo("mbid", mbid)
        newterm = ""
        if result != "empty" and "tags" in result.keys():
            if self.tag == "raaga":
                #raaga can be labelled as raaga or unknown!
                for tagInfo in result["tags"]:
                    if tagInfo["category"] == "unknown":
                        newterm = tagInfo["tag"]
                        if "raagam " in tagInfo["tag"]:
                            newterm = newterm.replace("raagam ", "").strip()
                            break
                        elif " raagam" in tagInfo["tag"]:
                            newterm = newterm.replace(" raagam", "").strip()
                            break
                        elif "raaga " in tagInfo["tag"]:
                            newterm = newterm.replace("raaga ", "").strip()
                            break
                        elif " raaga" in tagInfo["tag"]:
                            newterm = newterm.replace(" raaga", "").strip()
                            break
                        elif "ragam " in tagInfo["tag"]:
                            newterm = newterm.replace("ragam ", "").strip()
                            break
                        elif " ragam" in tagInfo["tag"]:
                            newterm = newterm.replace("ragam", "").strip()
                            break
                        elif "raga " in tagInfo["tag"]:
                            newterm = newterm.replace("raga ", "").strip()
                            break
                        elif " raga" in tagInfo["tag"]:
                            newterm = newterm.replace(" raga", "").strip()
                            break
                        else:
                            newterm = ""
                    elif tagInfo["category"] == "raaga":
                        newterm = tagInfo["tag"]
                        break
                    elif tagInfo["category"] == "raga":
                        newterm = tagInfo["tag"]
                        break
            elif self.tag == "taala":
                #taala can be labelled as taala or unknown!
                for tagInfo in result["tags"]:
                    if tagInfo["category"] == "unknown":
                        newterm = tagInfo["tag"]
                        if "taalam " in tagInfo["tag"]:
                            newterm = newterm.replace("taalam ", "").strip()
                            break
                        elif " taalam" in tagInfo["tag"]:
                            newterm = newterm.replace(" taalam", "").strip()
                            break
                        elif "taala " in tagInfo["tag"]:
                            newterm = newterm.replace("taala ", "").strip()
                            break
                        elif " taala" in tagInfo["tag"]:
                            newterm = newterm.replace(" taala", "").strip()
                            break
                        elif "talam " in tagInfo["tag"]:
                            newterm = newterm.replace("talam ", "").strip()
                            break
                        elif " talam" in tagInfo["tag"]:
                            newterm = newterm.replace("talam", "").strip()
                            break
                        elif "tala " in tagInfo["tag"]:
                            newterm = newterm.replace("tala ", "").strip()
                            break
                        elif " tala" in tagInfo["tag"]:
                            newterm = newterm.replace(" tala", "").strip()
                            break
                        else:
                            newterm = ""
                    elif tagInfo["category"] == "taala":
                        newterm = tagInfo["tag"]
                        break
                    elif tagInfo["category"] == "tala":
                        newterm = tagInfo["tag"]
                        break
            return newterm.lower()

    def get_terms(self):
        for mbid in self.yaml_map.keys():
            self.all_terms.append(self.get_tag(mbid))

        self.all_terms = list(np.unique(self.all_terms))
        try:
            self.all_terms.remove(None)
        except ValueError:
            pass
        try:
            self.all_terms.remove('')
        except ValueError:
            pass


    @staticmethod
    def dict_to_unicode(cluster):
        """
        Sometimes yaml complains about datatypes. Converting to unicode may help.
        This function converts a dictionary of type key:[value1, value2] to unicode.
        """
        unicode_cluster = {}
        for key in cluster.keys():
            ukey = unicode(key).encode("utf-8")
            unicode_cluster[ukey] = []
            for value in cluster[key]:
                unicode_value = unicode(value).encode("utf-8")
                unicode_cluster[ukey].append(unicode_value)
        return unicode_cluster

    def serialize_clusters(self, path):
        csv_clusters = []
        for cluster_name, values in self.clusters.items():
            try:
                values.remove(cluster_name)
            except ValueError:
                pass
            row = [cluster_name]
            row.extend(values)
            csv_clusters.append(row)
        fileobj = file(path, "w")
        csv_writer = csv.writer(fileobj)
        csv_writer.writerows(csv_clusters)
        fileobj.flush()

    def update_clusters(self):
        """
        """
        if len(self.all_terms) == 0:
            print "Calling get_terms function to find all the terms."
            self.get_terms()

        existing_terms = np.concatenate(self.clusters.values())
        updated_clusters = []
        for term in self.all_terms:
            if term in existing_terms:
                print term, " exists in our catalogue\n"
                self.log_file.write(term+" exists in our catalogue\n")
                continue

            #find similarities of a new term to each of the existing clusters
            similarities = []
            for key, values in self.clusters.items():
                s = 0
                for existing_term in values:
                    s += sd.similarity(term, existing_term)
                s /= len(values)
                similarities.append([key, s])
            similarities = np.array(similarities)

            tmp = similarities[:, 1].astype("float")
            max_index = np.argmax(tmp)
            if tmp[max_index] < self.similarity_threshold:
                cluster_name = similarities[max_index][0]
                print "Added new cluster for", term, "(Nearest cluster was ", cluster_name, ") \n"
                self.log_file.write("Added new cluster for " + term +
                                    " (Nearest cluster was " + cluster_name + ") \n")
                self.clusters[term] = [term]
                updated_clusters.append(term)
            else:
                cluster_name = similarities[max_index][0]
                self.clusters[cluster_name].append(term)
                print term, "is now part of ", cluster_name, "cluster with", str(tmp[max_index]), "confidence\n"
                self.log_file.write(term + " is now part of " + cluster_name +
                                    " cluster with " + str(tmp[max_index]) + " confidence\n")
                updated_clusters.append(cluster_name)

        updated_clusters = np.unique(updated_clusters)
        self.log_file.write("The following are the updated clusters:\n")
        for i in updated_clusters:
            self.log_file.write(i + "\n")


import sys
if __name__ == "__main__":
    yaml_map_file = sys.argv[1]
    clusters_csv_file = sys.argv[2]
    fuzzymatch = FuzzyMatch(yaml_map_file, clusters_csv_file,
                            tag="raaga", similarity_threshold=0.6)
    fuzzymatch.get_terms()
    fuzzymatch.update_clusters()
    fuzzymatch.serialize_clusters(sys.argv[3])