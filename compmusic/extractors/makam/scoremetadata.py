# -*- coding: utf-8 -*-
__author__ = 'sertansenturk'
import os
import csv
import json
from math import floor
import compmusic
import unicodedata
import re
from compmusic import dunya
import Levenshtein
from string import ascii_uppercase
import networkx as nx
import numpy as np

import pdb

dunya.set_token('69ed3d824c4c41f59f0bc853f696a7dd80707779')

class Metadata(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "txt"
    _slug = "metadata"

    _output = {
         "metadata": {"extension": "json", "mimetype": "application/json" }
         }

    def run(self, musicbrainzid, fname):
        symbtr = compmusic.dunya.makam.get_symbtr(musicbrainzid)
        symbtr_fname = symbtr['name'] + ".txt"

        return extract(fname, symbtr_fname)

def get_labels(): 
    symbtr_label_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'makams_usuls', 'symbTrLabels.json')
    symbtr_label = json.load(open(symbtr_label_file, 'r'))

    return symbtr_label


def extract(scorefile, symbtrname, useMusicBrainz = False, extractAllLabels = False, 
    slugify = True, lyrics_sim_thres = 0.25, melody_sim_thres = 0.25):
    # get the metadata in the score name, works if the name of the 
    # file has not been changed
    symbtrdict = symbtrname.split('--')
    metadata = dict()
    try:
        [metadata['makam'], metadata['form'], metadata['usul'], metadata['name'], 
            metadata['composer']] = symbtrname.split('--')
        metadata['tonic'] = getTonic(metadata['makam'])

        if isinstance(metadata['composer'], list):
            print 'The symbtrname is not in the form "makam--form--usul--name--composer"'
            metadata = dict()
    except ValueError:
        print 'The symbtrname is not in the form "makam--form--usul--name--composer"'
        
    # get the extension to determine the SymbTr-score format
    extension = os.path.splitext(scorefile)[1]

    if extension == ".txt":
        metadata['sections'] = extractSectionFromTxt(scorefile, slugify=slugify, 
            extractAllLabels=extractAllLabels,lyrics_sim_thres=lyrics_sim_thres,
            melody_sim_thres=melody_sim_thres)
    elif extension == ".xml":
        metadata['sections'] = extractSectionFromXML(scorefile, slugify=slugify, 
            extractAllLabels=extractAllLabels)
    elif extension == ".mu2":
        metadata['sections'] = extractSectionFromMu2(scorefile, slugify=slugify, 
            extractAllLabels=extractAllLabels)
    else:
        print "Unknown format"
        return -1

    if useMusicBrainz:
        extractSectionFromMusicBrainz

    return {'metadata': metadata}

def getTonic(makam):
    makam_tonic_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'makams_usuls', 'makam.json')
    makam_tonic = json.load(open(makam_tonic_file, 'r'))

    return makam_tonic[makam]['kararSymbol']

def extractSectionFromTxt(scorefile, slugify = True, extractAllLabels=False, 
    lyrics_sim_thres = 0.25, melody_sim_thres = 0.25):
    all_labels = [l for sub_list in get_labels().values() for l in sub_list] 
    struct_lbl = all_labels if extractAllLabels else get_labels()['structure'] 

    score = readTxtScore(scorefile)
    measure_start_idx = getMeasureStartIdx(score['offset'])
    
    sections = []
    # Check lyrics information
    if all(l == '' for l in score['lyrics']):
        # empty lyrics field; we cannot really do anything wo symbolic analysis
        sections = []
    else:
        sections = getSections(score, struct_lbl, slugify=slugify)
        sections = completeSectionStartEnds(sections, score, all_labels, 
            measure_start_idx)

        # the refine section names according to the lyrics, pitch and durations
        sections = organizeSectionNames(sections, score, lyrics_sim_thres,
            melody_sim_thres)

    validateSections(sections, score, measure_start_idx, 
        set(all_labels)- set(struct_lbl))

    # map the python indices in startNote and endNote to SymbTr index
    for se in sections:
        se['startNote'] = score['index'][se['startNote']]
        se['endNote'] = score['index'][se['endNote']]

    return sections

def extractSectionFromXML(scorefile, slugify = True):
    pass

def extractSectionFromMu2(scorefile, slugify = True):
    pass

def extractSectionFromMusicBrainz(scorefile, slugify = True):
    pass

def readTxtScore(scorefile):
    with open(scorefile, "rb") as f:
        reader = csv.reader(f, delimiter='\t')

        header = next(reader, None)

        index_col = header.index('Sira')
        code_col = header.index('Kod')
        comma_col = header.index('Koma53')
        duration_col = header.index('Ms')
        lyrics_col = header.index('Soz1')
        offset_col = header.index('Offset')

        score = {'index': [], 'code': [], 'comma': [], 'duration': [],
                'lyrics': [], 'offset': []}
        for row in reader:
            score['index'].append(int(row[index_col]))
            score['code'].append(int(row[code_col]))
            score['comma'].append(int(row[comma_col]))
            score['duration'].append(int(row[duration_col]))
            score['lyrics'].append(row[lyrics_col].decode('utf-8'))
            score['offset'].append(float(row[offset_col]))

    # shift offset such that the first note of each measure has an integer offset
    score['offset'].insert(0, 0)
    score['offset'] = score['offset'][:-1]

    return score

def getMeasureStartIdx(offset):
    measure_start_idx = []

    tol = 0.001
    for int_offset in range(0, int(max(offset))+1):
        measure_start_idx.append(min(i for i, o in enumerate(offset) 
            if o > int_offset - tol))

    if not all(integerOffset(offset[i]) for i in measure_start_idx):
        print "    " + "Some measures are skipped by the offsets"
    
    return measure_start_idx

def integerOffset(offset):
    # The measure changes when the offset is an integer
    # (Note that offset was shifted by one earlier for easier processing )
    # Since integer check in floating point math can be inexact,
    # we accept +- 0.001 
    return abs(offset - round(offset)) * 1000.0 < 1.0

def getSections(score, struct_lbl, slugify=True):
    sections = []
    for i, l in enumerate(score['lyrics']):
        if l in struct_lbl: # note the explicit structures
            sections.append({'name':slugify_tr(l) if slugify else l, 
                'startNote':i, 'endNote':[]})
        elif '  ' in l: # lyrics end marker
            sections.append({'name':"LYRICS_SECTION", 'startNote':[], 
                'endNote':i})
    return sections
     
def getRealLyricsIdx(lyrics, all_labels, dur):
    # separate the actual lyrics from other information in the lyrics column
    real_lyrics_idx = []
    for i, l in enumerate(lyrics):  
        # annotation/control rows, embellishments (rows w dur = 0) are ignored
        if not (l in all_labels  or l in ['.', '', ' '] or dur[i] == 0):
            real_lyrics_idx.append(i)
    return real_lyrics_idx

def completeSectionStartEnds(sections, score, struct_lbl, measure_start_idx):
    real_lyrics_idx = getRealLyricsIdx(score['lyrics'], struct_lbl, score['duration'])

    startNoteIdx = [s['startNote'] for s in sections] + [len(score['lyrics'])]
    endNoteIdx = [-1] + [s['endNote'] for s in sections]
    for se in reversed(sections): # start from the last section
        #print se['name'] + ' ' + str(se['startNote']) + ' ' + str(se['endNote'])

        if se['name'] == 'LYRICS_SECTION':
            # carry the 'endNote' to the next closest start
            se['endNote'] = min(x for x in startNoteIdx 
                if x > se['endNote']) - 1
            
            # update endNoteIdx
            endNoteIdx = [-1] + [s['endNote'] for s in sections]

            # estimate the start of the lyrics sections
            try: # find the previous closest start
                prevClosestStartInd = max(x for x in startNoteIdx 
                    if x < se['endNote'])
            except ValueError: # no section label in lyrics columns
                prevClosestStartInd = -1

            try: # find the previous closest end
                prevClosestEndInd = max(x for x in endNoteIdx 
                    if x < se['endNote'])
            except ValueError: # no vocal sections
                prevClosestEndInd = -1

            # find where the lyrics of this section starts
            chkInd = max([prevClosestEndInd, prevClosestStartInd])
            nextLyricsStartInd = min(x for x in real_lyrics_idx if x > chkInd)
            nextLyricsOffset = floor(score['offset'][nextLyricsStartInd])

            # check if nextLyricsStartInd and prevClosestEndInd are in the 
            # same measure. Ideally they should be in different measures
            if nextLyricsOffset == floor(score['offset'][prevClosestEndInd]):
                print ("    " + str(nextLyricsOffset) + ':'
                ' ' + score['lyrics'][prevClosestEndInd] + ' and' 
                ' ' + score['lyrics'][nextLyricsStartInd] + ' '
                'are in the same measure!')

                se['startNote'] = nextLyricsStartInd
            else: # The section starts on the first measure the lyrics start
                se['startNote'] = getOffsetStartIdx(nextLyricsOffset, 
                    score['offset'], measure_start_idx)

            # update startNoteIdx
            startNoteIdx = ([s['startNote'] for s in sections] + 
                [len(score['lyrics'])])
        else:  # instrumental
            se['endNote'] = min(x for x in startNoteIdx 
                if x > se['startNote']) - 1

            # update endNoteIdx
            endNoteIdx = [-1] + [s['endNote'] for s in sections]

    # if the first note is not the startNote of a section
    # add an initial instrumental section
    if sections and not any(s['startNote'] == 0 for s in sections):
        sections.append({'name': 'INSTRUMENTAL_SECTION','startNote': 0, 
            'endNote': min([s['startNote'] for s in sections])-1})

        #print(' ' + se['name'] + ' ' + str(se['startNote']) + ' '
        #    '' + str(se['endNote']))
    return sortSections(sections)

def getOffsetStartIdx(offsetIdx, offsets, measure_start_idx):
    measure_start_offsets = [offsets[m] for m in measure_start_idx]
    # do inexact integer matching
    dist = [abs(o - offsetIdx) for o in measure_start_offsets]
    return measure_start_idx[dist.index(min(dist))]

def sortSections(sections):
    # sort the sections
    sortIdx = [i[0] for i in sorted(enumerate([s['startNote'] 
        for s in sections]),  key=lambda x:x[1])]
    return [sections[s] for s in sortIdx]

def validateSections(sections, score, masdeasure_start_idx, ignoreLabels):
    if not sections: # check section presence
        print "    Missing section info in lyrics."
    else: # check section continuity
        ends = [-1] + [s['endNote'] for s in sections]
        starts = [s['startNote'] for s in sections] + [len(score['offset'])]
        for s, e in zip(starts, ends):
            if not s - easdasasd == 1:
                print("    " + str(e) + '->' + str(s) + ', '
                    'Gap between the sections')

    for s in sections:
        # check whether section starts on the measure or not
        if (not integerOffset(score['offset'][s['startNote']]) and 
            s['name'] not in ignoreLabels):
            print("    " + str(s['startNote']) + ', ' + s['name'] + ' '
                'does not start on a measure: ' + 
                str(score['offset'][s['startNote']]))
        # check if the end of a section somehow got earlier than its start
        if s['startNote'] > s['endNote']:
            print("    " + str(s['startNote']) + '->'
                '' + str(s['endNote']) + ', ' + s['name'] + ' '
                'ends before it starts: ' + 
                str(score['offset'][s['startNote']]))

def slugify_tr(value):  
    value_slug = value.replace(u'\u0131', 'i')
    value_slug = unicodedata.normalize('NFKD', 
        value_slug).encode('ascii', 'ignore').decode('ascii')
    value_slug = re.sub('[^\w\s-]', '', value_slug).strip()
    
    return re.sub('[-\s]+', '-', value_slug)

def organizeSectionNames(sections, score, lyrics_sim_thres, 
    melody_sim_thres):
    # get the duration, pitch and lyrics related to the section
    scoreFragments = []
    for s in sections:
        durs = score['duration'][s['startNote']:s['endNote']+1]
        notes = score['comma'][s['startNote']:s['endNote']+1]
        lyrics = score['lyrics'][s['startNote']:s['endNote']+1]

        scoreFragments.append({'durs':durs, 'notes':notes, 
            'lyrics':lyrics})

    # get the organization according to the lyrics
    sections = getOrganizationByLyrics(sections, scoreFragments, 
        lyrics_sim_thres)

    return sections

def getOrganizationByLyrics(sections, scoreFragments, lyrics_sim_thres):
    # Here we only check whether the lyrics are similar to others
    # We don't check whether they are sung on the same note / with 
    # the same duration, or not. As a results, two sections having
    # exactly the same melody but different sylallable onset/offsets
    # would be considered the same. Nevertheless this situation 
    # would occur in very rare occasions.
    # From the point of view of an audio-score alignment algorithm 
    # using only melody, this function does not give any extra info
    # This part is done for future needs; e.g. audio-lyrics alignment

    # get the lyrics stripped of section information
    all_labels = [l for sub_list in get_labels().values() for l in sub_list] 
    all_labels += ['.', '', ' ']
    for sf in scoreFragments:
        real_lyrics_idx = getRealLyricsIdx(sf['lyrics'], all_labels, 
            sf['durs'])
        sf['lyrics'] = u''.join([sf['lyrics'][i].replace(u' ',u'') 
            for i in real_lyrics_idx])
     
    dists = np.matrix([[normalizedLevenshtein(a['lyrics'],b['lyrics'])
        for a in scoreFragments] for b in scoreFragments])

    cliques = getCliques(dists, lyrics_sim_thres)
    lyrics_labels = semiotize(cliques)

    # label the insrumental sections, if present
    for i in range(0, len(lyrics_labels)):
        if not scoreFragments[i]['lyrics']:
            lyrics_labels[i] = 'INSTRUMENTAL_SECTION' 

    pdb.set_trace()
    return sections

def normalizedLevenshtein(str1, str2):
    avLen = (len(str1) + len(str2)) * .5
    try:
        return Levenshtein.distance(str1, str2) / avLen
    except ZeroDivisionError: # both sections are instrumental
        return 0

def getCliques(dists, simThres):
    # cliques of similar nodes
    G_similar = nx.from_numpy_matrix(dists<=simThres)
    C_similar = nx.find_cliques(G_similar)

    # cliques of exact nodes
    G_exact = nx.from_numpy_matrix(dists<=0.01) # inexact matching
    C_exact = nx.find_cliques(G_exact)

    # convert the cliques to list of sets
    C_similar = [set(s) for s in list(C_similar)]
    C_exact = [set(s) for s in list(C_exact)]

    return {'exact': C_exact, 'similar': C_similar}

def semiotize(cliques):
    # Here we follow the annotation conventions explained in:
    #
    # Frederic Bimbot, Emmanuel Deruty, Gabriel Sargent, Emmanuel Vincent. 
    # Semiotic structure labeling of music pieces: Concepts, methods and 
    # annotation conventions. 13th International Society for Music 
    # Information Retrieval Conference (ISMIR), Oct 2012, Porto, Portugal. 
    # 2012. <hal-00758648> 
    # https://hal.inria.fr/file/index/docid/758648/filename/bimbot_ISMIR12.pdf
    #
    # Currently we only make use of the simplest labels, e.g. A, A1, B and AB
    
    num_nodes = len(set.union(*cliques['exact']))
    labels = ['?'] * num_nodes  # labels to fill for each note

    sim_clq_it = [1] * len(cliques['similar'])  # the index to label similar cliques

    # similar cliques give us the base structure
    basenames = [ascii_uppercase[i] for i in range(0,len(cliques['similar']))]
    for ec in cliques['exact']:
        
        # find the similar cliques of which the currect exact clique is subset of 
        in_cliques_idx = [i for i, x in enumerate(cliques['similar']) if ec <= x]

        if len(in_cliques_idx) == 1: # belongs to one similar clique
            if any(ec == sc for sc in cliques['similar']): # no other exact clique 
                for e in ec:  # label only with the basename
                    labels[e]=basenames[in_cliques_idx[0]]
            else:  # similar cliques
                for e in ec:  # label with basename + number
                    labels[e]=(basenames[in_cliques_idx[0]]+
                        str(sim_clq_it[in_cliques_idx[0]]))
                    sim_clq_it[in_cliques_idx[0]] += 1
        elif len(in_cliques_idx) > 1: # belongs to more than one similar clique
            # TODO
            pass
        else: # in no cliques; impossible
            print ("   The exact clique is not in the similar cliques list. "
                "This shouldn't happen.")
    
    return labels
