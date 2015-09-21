# -*- coding: utf-8 -*-
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

import numpy
import matplotlib.pyplot as plt
import os
import fnmatch
import getopt
import sys
from types import *
from lxml import etree

# koma definitions
# flats
b_koma = 'quarter-flat'  # 'flat-down'
b_bakiyye = 'slash-flat'
b_kmucennep = 'flat'
b_bmucennep = 'double-slash-flat'

# sharps
d_koma = 'quarter-sharp'  #quarter-sharp    SWAP 1ST AND 3RD SHARPS
d_bakiyye = 'sharp'
d_kmucennep = 'slash-quarter-sharp'                #slash-quarter-sharp
d_bmucennep = 'slash-sharp'

altervalues = {'quarter-flat' : "-0.5", 'slash-flat': None, 'flat' : '-1', 'double-slash-flat' : None,
             'quarter-sharp' : '+0.5', 'slash-sharp' : None, 'sharp' : "+1", 'double-slash-sharp' : None}

#section list
sectionList = [u"1. HANE", u"2. HANE", u"3. HANE", u"4. HANE", u"TESLİM", u"TESLİM ", u"MÜLÂZİME", u"SERHÂNE", u"HÂNE-İ SÂNİ", u"HÂNE-İ SÂLİS", u"SERHANE", u"ORTA HANE", u"SON HANE", u"1. HANEYE", u"2. HANEYE", u"3. HANEYE", u"4. HANEYE", u"KARAR", u"1. HANE VE MÜLÂZİME", u"2. HANE VE MÜLÂZİME", u"3. HANE VE MÜLÂZİME", u"4. HANE VE MÜLÂZİME", u"1. HANE VE TESLİM", u"2. HANE VE TESLİM", u"3. HANE VE TESLİM", u"4. HANE VE TESLİM", u"ARANAĞME", u"ZEMİN", u"NAKARAT", u"MEYAN", u"SESLERLE NİNNİ", u"OYUN KISMI", u"ZEYBEK KISMI", u"GİRİŞ SAZI", u"GİRİŞ VE ARA SAZI", u"GİRİŞ", u"FİNAL", u"SAZ", u"ARA SAZI", u"SUSTA", u"KODA", u"DAVUL", u"RİTM", u"BANDO", u"MÜZİK", u"SERBEST", u"ARA TAKSİM", u"GEÇİŞ TAKSİMİ", u"KÜŞAT", u"1. SELAM", u"2. SELAM", u"3. SELAM", u"4. SELAM", u"TERENNÜM"]

tuplet = 0

errLog = open('errLog.txt', 'w')
missingUsuls = []

def getNoteType(note, type, pay, payda, sira):
    global tuplet

    ## NEW PART FOR DOTTED NOTES
    temp_payPayda = float(pay) / int(payda)

    if temp_payPayda >= 1.0:
        type.text = 'whole'
        temp_undotted = 1.0
    elif 1.0 > temp_payPayda >= 1.0 / 2:
        type.text = 'half'
        temp_undotted = 1.0 / 2
    elif 1.0/2 > temp_payPayda >= 1.0 / 4:
        type.text = 'quarter'
        temp_undotted = 1.0 / 4
    elif 1.0/4 > temp_payPayda >= 1.0 / 8:
        type.text = 'eighth'
        temp_undotted = 1.0 / 8
    elif 1.0/8 > temp_payPayda >= 1.0 / 16:
        type.text = '16th'
        temp_undotted = 1.0 / 16
    elif 1.0/16 > temp_payPayda >= 1.0 / 32:
        type.text = '32nd'
        temp_undotted = 1.0 / 32
    elif 1.0/32 > temp_payPayda >= 1.0 / 64:
        type.text = '64th'
        temp_undotted = 1.0 / 64

    #check for tuplets
    if temp_payPayda == 1.0 / 12:
        type.text = 'eighth'
        temp_undotted = 1.0 / 12
        tuplet += 1
    elif temp_payPayda == 1.0 / 24:
        type.text = '16th'
        temp_undotted = 1.0 / 24
        tuplet += 1
    #end of tuplets

    #not tuplet, normal or dotted
    #print(tuplet)

    #print(temp_payPayda)

    nofdots = 0
    timemodflag = 0
    if tuplet == 0:
        #print(sira, temp_payPayda, temp_undotted)
        temp_remainder = temp_payPayda - temp_undotted

        dotVal = temp_undotted / 2.0
        while temp_remainder > 0:
            type = etree.SubElement(note, 'dot')
            nofdots += 1
            temp_remainder = temp_payPayda - temp_undotted - dotVal
            dotVal += dotVal / 2
            break
        #print(sira, temp_payPayda, temp_undotted, dotVal, temp_remainder)

    ##END OF NEW PART FOR DOTTED NOTES
    else:
        timemodflag = 1

    return timemodflag

        #print(sira, temp_payPayda, '------------------')

def getUsul(usul, file):
    fpath = 'makams_usuls/usuls_v3_ANSI.txt'

    usulID = []
    usulName = []
    nofBeats = []
    beatType = []
    accents = []

    f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), fpath))

    while 1:
        temp_line = f.readline()

        if len(temp_line) == 0:
            break
        else:
            temp_line = temp_line.split('\t')
            temp_line.reverse()
            #print(temp_line)

            try:
                usulID.append(temp_line.pop())
            except:
                usulID.append('')

            try:
                usulName.append(temp_line.pop())
            except:
                usulName.append('')

            try:
                nofBeats.append(temp_line.pop())
            except:
                nofBeats.append('')

            try:
                beatType.append(temp_line.pop())
            except:
                beatType.append('')

            try:
                accents.append(temp_line.pop())
            except:
                accents.append('')

    f.close
    #eof file read
    '''
    print(usulID[usulID.index(usul)])
    print(usulName)
    print(nofBeats[usulID.index(usul)])
    print(beatType[usulID.index(usul)])
    print(accents)
    print(len(usulID),len(usulName),len(nofBeats),len(beatType),len(accents))
    '''
    try:
        #print( nofBeats[usulID.index(usul)], 2**int(beatType[usulID.index(usul)]) )
        return int(nofBeats[usulID.index(usul)]), int(
            beatType[usulID.index(usul)])  #second paramater, usul_v1 2**int(beatType[usulID.index(usul)]
    except:
        #print('Usul: ', usul, ' not in list')
        #errLog.write('Usul: ' + usul + ' not in list.\n')
        missingUsuls.append(usul + '\t' + file)
        #return 4, 4


def getAccName(alter):
    #print('Alter: ',alter)
    if alter == '+1' or alter == '+2':
        accName = d_koma
    elif alter == '+4' or alter == '+3':
        accName = d_bakiyye
    elif alter == '+5' or alter == '+6':
        accName = d_kmucennep
    elif alter == '+8' or alter == '+7':
        accName = d_bmucennep
    elif alter == '-1' or alter == '-2':
        accName = b_koma
    elif alter == '-4' or alter == '-3':
        accName = b_bakiyye
    elif alter == '-5' or alter == '-6':
        accName = b_kmucennep
    elif alter == '-8' or alter == '-7':
        accName = b_bmucennep

    return accName


def getKeySig(piecemakam, keysig):


    makamTree = etree.parse(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'makams_usuls/Makamlar.xml'))
    xpression = '//dataroot/Makamlar[makam_adi= $makam]/'
    makam_ = piecemakam

    makamName = makamTree.xpath(xpression + 'Makam_x0020_Adi', makam=makam_)
    #print(makamName)

    donanim = []
    trToWestern = {'La': 'A', 'Si': 'B', 'Do': 'C', 'Re': 'D', 'Mi': 'E', 'Fa': 'F', 'Sol': 'G'}

    for i in range(1, 10):
        try:
            donanim.append((makamTree.xpath(xpression + 'Donanim-' + str(i), makam=makam_))[0].text)
            donanim[-1] = trToWestern[donanim[-1][:2]] + donanim[-1][2:]
            print(donanim[-1])
        except:
            break

    #print(makamName[0].text)
    #print(donanim)

    while len(donanim) > 0:
        temp_key = donanim.pop()
        #print(temp_key)
        if type(temp_key) != type(None):
            temp_key = temp_key.replace('#', '+')
            temp_key = temp_key.replace('b', '-')

            keystep = etree.SubElement(keysig, 'key-step')
            keystep.text = temp_key[0]
            #''' alteration is not working for microtones
            keyalter = etree.SubElement(keysig, 'key-alter')
            keyalter.text = temp_key[-2:]
            #'''
            keyaccidental = etree.SubElement(keysig, 'key-accidental')
            keyaccidental.text = getAccName(temp_key[-2:])


class symbtrscore(object):
    def __init__(self, fpath, makam, form, usul, name, composer=None):
        self.fpath = fpath
        #piece attributes
        self.makam = makam 
        self.form = form
        self.usul = usul
        self.name = name
        self.composer = "N/A"
        if composer: 
            self.composer = composer

        #symbtr lines
        self.l_sira = []
        self.l_kod = []
        self.l_nota53 = []
        self.l_notaAE = []
        self.l_koma53 = []
        self.l_komaAE = []
        self.l_pay = []
        self.l_payda = []
        self.l_ms = []
        self.l_LNS = []
        self.l_velOn = []
        self.l_soz1 = []
        self.l_offset = []
        self.nof_divs = 0

        #cumulative time array
        self.l_time = [0]

        #split note information for xml use
        self.l_nota = []
        self.l_oct = []
        self.l_acc = []

        self.tuplet = 0

        self.score = None
        self.sections = []

    def readsymbtrlines(self):
        f = open(self.fpath)
        i = 0
        sumlinelength = 0

        #read operation
        while 1:
            temp_line = f.readline()
            #print(temp_line)
            if len(temp_line) == 0:
                break
            elif len(temp_line.split('\t')) == 1:
                l_soz1[-1] += temp_line
            else:
                temp_line = temp_line.split('\t')
                temp_line.reverse()
                #print(temp_line)
                #print(len(temp_line))
                #sumlinelength += len(temp_line)

                self.l_sira.append(temp_line.pop())
                self.l_kod.append(temp_line.pop())
                self.l_nota53.append(temp_line.pop())
                self.l_notaAE.append(temp_line.pop())
                self.l_koma53.append(temp_line.pop())
                self.l_komaAE.append(temp_line.pop())
                self.l_pay.append(temp_line.pop())
                self.l_payda.append(temp_line.pop())
                self.l_ms.append(temp_line.pop())
                self.l_LNS.append(temp_line.pop())
                self.l_velOn.append(temp_line.pop())
                try:
                    self.l_soz1.append(temp_line.pop().decode('utf-8'))
                except:
                    self.l_soz1.append('')
                try:
                    self.l_offset.append(temp_line.pop())
                    self.l_offset[-1] = l_offset[-1][:-1]
                except:
                    self.l_offset.append('')
                i += 1
        f.close
        #eof file read
        #print ('sumlinelength:')
        #print(sumlinelength)
        #print(l_soz1)

         #cumulative time array

        l_temp = list(self.l_ms)
        l_temp.reverse()
        l_temp.pop()

        while len(l_temp) != 0:
            self.l_time.append(self.l_time[-1] + int(l_temp.pop()))
        #eof time array

        l_temp = list(self.l_notaAE)
        l_temp.reverse()
        #l_temp.pop()

        while len(l_temp) != 0:
            temp_note = l_temp.pop()
            if len(temp_note) > 0 and temp_note not in ['Sus', 'Es']:
                self.l_nota.append(temp_note[0])
                self.l_oct.append(temp_note[1])

                if len(temp_note) == 2:
                    self.l_acc.append('')
                else:
                    if temp_note[2] == '#':
                        try:
                            self.l_acc.append('+' + temp_note[3])
                        except:
                            print(temp_note)
                    else:
                        try:
                            self.l_acc.append('-' + temp_note[3])
                        except:
                            print(temp_note)
            else:
                self.l_nota.append('r')
                self.l_oct.append('r')
                self.l_acc.append('r')

    def symbtrtempo(self, pay1, ms1, payda1, pay2, ms2, payda2):
        try:
            return 60000 * 4 * int(pay1) / (int(ms1) * int(payda1))
        except:
            return 60000 * 4 * int(pay2) / (int(ms2) * int(payda2))

    def addwordinfo(self, lyric, templyric, word, endlineflag):
        #endlineflag = 0
        spacechars = 0
        #lyrics word information
        if len(templyric) > 0 and templyric != "." and templyric not in sectionList:
            spacechars = templyric.count(" ")
            #print(spacechars)
            syllabic = etree.SubElement(lyric, 'syllabic')
            if spacechars == 2:
                #print("word end", cnt)
                #SEGMENT END
                endlineflag = 1
                syllabic.text = "end"
                word = 0
                #sentence = 1
            elif spacechars >= 1:
                syllabic.text = "end"
                word = 0
                #print("word end", cnt)
            else:
                if word == 0:
                    syllabic.text = "begin"
                    word = 1
                    #print("word start", cnt)
                elif word == 1:
                    syllabic.text = "middle"
                    #print("word middle", cnt)
        #print(templyric, endlineflag, word, spacechars)
        return word, endlineflag

    def addduration(self, duration, pay, payda):
        temp_duration = int(self.nof_divs * 4 * int(pay) / int(payda))
        duration.text = str(temp_duration)
        return temp_duration   #duration calculation    UNIVERSAL

    def addaccidental(self, note, acc, pitch):
        xmlaccidental = {'+1': d_koma, '+4': d_bakiyye, '+5': d_kmucennep, '+8': d_bmucennep,
                                     '-1': b_koma, '-4': b_bakiyye, '-5': b_kmucennep, '-8': b_bmucennep}
        if acc not in ['', 'r']:
            accidental = etree.SubElement(note, 'accidental')  #accidental XML create
            accidental.text = xmlaccidental[acc]
            '''
            alter = etree.SubElement(pitch, 'alter')
            if int(acc) > 0:
                alter.text = '1'
            else:
                alter.text = '-1'
            '''
            self.addalter(pitch, xmlaccidental[acc])

    def addalter(self, pitch, acc):
        if altervalues[acc] != None:
            alter = etree.SubElement(pitch, 'alter')
            alter.text = altervalues[acc]

    def addtimemodification(self, note):
        global tuplet
        time_mod = etree.SubElement(note, 'time-modification')
        act_note = etree.SubElement(time_mod, 'actual-notes')
        act_note.text = '3'
        norm_note = etree.SubElement(time_mod, 'normal-notes')
        norm_note.text = '2'

        if tuplet == 1:
            notat = etree.SubElement(note, 'notations')
            tupl = etree.SubElement(notat, 'tuplet')
            tupl.set('type', 'start')
            tupl.set('bracket', 'yes')
        elif tuplet == 3:
            notat = etree.SubElement(note, 'notations')
            tupl = etree.SubElement(notat, 'tuplet')
            tupl.set('type', 'stop')
            #tupl.set('bracket', 'yes')
            tuplet = 0

    def usulchange(self, measure, tempatts, temppay, temppayda, nof_divs, templyric):
        nof_beats = int(temppay)
        beat_type = int(temppayda)
        measureLength = nof_beats * nof_divs * (4 / float(beat_type))
        #print(nof_beats, beat_type)
        #print(measureSum)
        time = etree.SubElement(tempatts, 'time')
        beats = etree.SubElement(time, 'beats')
        beatType = etree.SubElement(time, 'beat-type')
        beats.text = str(nof_beats)
        beatType.text = str(beat_type)

        #1st measure direction: usul and makam info
        #                                               tempo(metronome)
        direction = etree.SubElement(measure, 'direction')
        direction.set('placement', 'above')
        directionType = etree.SubElement(direction, 'direction-type')

        #usul info
        words = etree.SubElement(directionType, 'words')
        words.set('default-y', '35')
        if  templyric:
            words.text = 'Usul: ' + templyric.title()

        return  measureLength

    def setsection(self, tempmeasurehead, lyric, templyric):
        if templyric != "SAZ":
            tempheadsection = tempmeasurehead.find(".//lyric")
        else:
            tempheadsection = lyric
        tempheadsection.set('name', templyric)

    def xmlconverter(self):
        ###CREATE MUSIC XML
        #init
        self.score = etree.Element("score-partwise")  #score-partwise
        self.score.set('version', '3.0')

        #work-title
        work = etree.SubElement(self.score, 'work')
        workTitle = etree.SubElement(work, 'work-title')
        workTitle.text = self.name.title()

        identification = etree.SubElement(self.score, 'identification')
        enc = etree.SubElement(identification, 'encoding')
        sup = etree.SubElement(enc, 'supports')
        sup.set('element', 'print')
        sup.set('attribute', 'new-system')
        sup.set('type', 'yes')
        sup.set('value', 'yes')


        #part-list
        partList = etree.SubElement(self.score, 'part-list')
        scorePart = etree.SubElement(partList, 'score-part')
        scorePart.set('id', 'P1')
        partName = etree.SubElement(scorePart, 'part-name')
        partName.text = 'Music'

        #part1
        P1 = etree.SubElement(self.score, 'part')
        P1.set('id', 'P1')

        #measures array
        measure = []
        i = 1
        measureSum = 0

        #part1 measure1
        measure.append(etree.SubElement(P1, 'measure'))
        measure[-1].set('number', str(i))

        #1st measure direction: usul and makam info
        #                                               tempo(metronome)
        direction = etree.SubElement(measure[-1], 'direction')
        direction.set('placement', 'above')
        directionType = etree.SubElement(direction, 'direction-type')

        #usul and makam info
        words = etree.SubElement(directionType, 'words')
        words.set('default-y', '35')
        words.text = 'Makam: ' + self.makam.title() + ', Usul: ' + self.usul.title()

        #tempo info
        tempo = self.symbtrtempo(self.l_pay[1], self.l_ms[1], self.l_payda[1],
                                 self.l_pay[2], self.l_ms[2], self.l_payda[2])

        sound = etree.SubElement(direction, 'sound')
        sound.set('tempo', str(tempo))
        #print('tempo '+ str(tempo))

        nof_divs = 96
        self.nof_divs = nof_divs
        nof_beats = 4  #4
        beat_type = 4  #4
        if self.usul not in ['serbest', 'belirsiz']:
            nof_beats, beat_type = getUsul(self.usul, self.fpath)
            measureLength = nof_beats * nof_divs * (4 / float(beat_type))
        else:
            nof_beats = ''
            beat_type = ''
            measureLength = 1000

        #print(usul, measureLength)

        #ATTRIBUTES
        atts1 = etree.SubElement(measure[-1], 'attributes')
        divs1 = etree.SubElement(atts1, 'divisions')
        divs1.text = str(nof_divs)

        #key signature
        keysig = etree.SubElement(atts1, 'key')
        getKeySig(self.makam, keysig)
        #print(makam)

        time = etree.SubElement(atts1, 'time')
        beats = etree.SubElement(time, 'beats')
        beatType = etree.SubElement(time, 'beat-type')
        beats.text = str(nof_beats)
        beatType.text = str(beat_type)

        #print(l_acc)

        ###LOOP FOR NOTES
        #notes
        word = 0
        sentence = 0
        tempsection = 0
        endlineflag = 1
        tempatts = ""
        tempmeasurehead = measure[-1]

        for cnt in range(1, len(self.l_nota)):

            tempkod = self.l_kod[cnt]
            tempsira = self.l_sira[cnt]
            temppay = self.l_pay[cnt]
            temppayda = self.l_payda[cnt]
            tempnota = self.l_nota[cnt]
            tempacc = self.l_acc[cnt]
            tempoct = self.l_oct[cnt]
            templyric = self.l_soz1[cnt]

            if tempkod not in ['0', '8', '35', '51', '53', '54', '55']:
                note = etree.SubElement(measure[-1], 'note')  #note     UNIVERSAL

                if tempnota != 'r':
                    pitch = etree.SubElement(note, 'pitch')  #note pitch XML create
                else:
                    rest = etree.SubElement(note, 'rest')  #note rest XML create        REST

                duration = etree.SubElement(note, 'duration')  #note duration XML create        UNIVERSAL
                type = etree.SubElement(note, 'type')  #note type XML create    UNIVERSAL
                #print(l_kod[cnt+1], l_nota[cnt] , l_payda[cnt+1])
                #print(l_payda[cnt+1])
                #BAŞLA
                if int(temppayda) == 0:
                    print(tempsira + '\t' + tempkod + '\t' + self.fpath)
                    continue
                temp_duration = self.addduration(duration, temppay, temppayda)  #duration calculation   UNIVERSAL

                timemodflag = getNoteType(note, type, temppay, temppayda, tempsira)

                if tempnota != 'r':
                    step = etree.SubElement(pitch, 'step')   #note pitch step XML create
                    step.text = tempnota                  #step val #XML assign

                    #setting accidentals
                    self.addaccidental(note, tempacc, pitch)

                    octave = etree.SubElement(pitch, 'octave')  #note pitch octave XML create
                    octave.text = tempoct  #octave val XML assign

                    if timemodflag == 1:
                        self.addtimemodification(note)

                    #LYRICS PART
                    lyric = etree.SubElement(note, 'lyric')

                    word, endlineflag = self.addwordinfo(lyric, templyric, word, endlineflag)    #word keeps the status of current syllable
                    #current lyric text
                    text = etree.SubElement(lyric, 'text')
                    text.text = templyric

                    if endlineflag == 1:
                        endline = etree.SubElement(lyric, 'end-line')

                    print(cnt, endlineflag, measureSum)

                    #section information
                    if templyric in sectionList:        #instrumental pieces and pieces with section keywords
                        #lyric.set('name', templyric)
                        self.setsection(tempmeasurehead, lyric, templyric)
                        self.sections.append(templyric)
                        #section = templyric
                    elif (endlineflag == 1 and measureSum == 0) or \
                            (endlineflag == 0 and measureSum == 0 and self.sections[-1] == "SAZ"):  #line endings
                        tempsectionid = "Section" + str(tempsection)
                        self.setsection(tempmeasurehead, lyric, tempsectionid)
                        self.sections.append(tempsectionid)
                        tempsection += 1
                        endlineflag = 0
                    else:
                        #tempsection += 1
                        lyric.set('name', "")

                measureSum += temp_duration
                #print(temp_duration, ' ', measureSum, ' ' , measureLength,' ',i)

                #NEW MEASURE
                if measureSum >= measureLength:
                    i += 1
                    numb = etree.SubElement(P1, 'measure')
                    measure.append(numb)
                    measure[-1].set('number', str(i))
                    if i % 2 !=0:
                        eprint = etree.SubElement(measure[-1], 'print')
                        eprint.set('new-system', 'yes')

                    tempatts = etree.SubElement(numb, 'attributes')
                    measureSum = 0
                    tempmeasurehead = numb
                    #eof notes
            elif tempkod == '51':
                #print('XX')
                try:
                    measureLength = self.usulchange(measure[-1], tempatts, temppay, temppayda, nof_divs, templyric)
                except:
                    print('Kod', tempkod, 'but no time information.')

    def writexml(self, out_file):
        #printing xml file
        f = open(out_file, 'wb')
        f.write(etree.tostring(self.score, pretty_print=True, xml_declaration=True, encoding="UTF-8", standalone=False ,
                               doctype='<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">'))
        f.close

    def convertsymbtr2xml(self, out_file):
        self.readsymbtrlines()
        self.xmlconverter()
        self.writexml(out_file)

def multipleFiles():
    errorFiles = []
    totalFiles = 0
    cnvFiles = 0
    errFiles = 0

    for file in os.listdir('.'):
        if fnmatch.fnmatch(file, '*.txt') and file != 'errLog.txt' and file != 'errorFiles.txt':
            print(file)
            #txtToMusicXML(file)
            totalFiles += 1
            '''
            try:
                txtToMusicXML(file)
                cnvFiles += 1
            except:
                errorFiles.append(file)
                errFiles += 1
            '''
    f = open('errorFiles.txt', 'w')
    for item in errorFiles:
        f.write(item + '\n')
    f.close
    print('Total files: ', totalFiles)
    print('Converted: ', cnvFiles)
    print('Failed: ', errFiles)
    print('Usul Conflict: ', len(set(missingUsuls)))


