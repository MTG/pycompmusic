# coding=utf-8
__author__ = 'burakuyar', 'hsercanatli'
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import json
import xml.etree.ElementTree as ET
import sqlite3
import codecs

class ScoreConverter(object):
    def __init__(self, name):
        # io information
        self.file = name
        self.ly_stream = []

        # setting the xml tree
        self.tree = ET.parse(self.file)
        self.root = self.tree.getroot()

        # koma definitions
        # flats
        self.b_koma = 'quarter-flat'
        self.b_bakiyye = 'slash-flat'
        self.b_kmucennep = 'flat'
        self.b_bmucennep = 'double-slash-flat'

        # sharps
        self.d_koma = 'quarter-sharp'
        self.d_bakiyye = 'sharp'
        self.d_kmucennep = 'slash-quarter-sharp'
        self.d_bmucennep = 'slash-sharp'

        # list of accidentals
        self.list_accidentals = {self.b_koma: "-1", self.b_bakiyye: "-4", self.b_kmucennep: "-5", self.b_bmucennep: "-8",
                                 self.d_koma: "+1", self.d_bakiyye: "+4", self.d_kmucennep: "+5", self.d_bmucennep: "+8"}

        # octaves and accidentals dictionary
        self.octaves = {"2": ",", "3": "", "4": "\'", "5": "\'\'", "6": "\'\'\'", "7": "\'\'\'\'", "r": ""}
        self.accidentals = {"-1": "fc", "-4": "fb", "-5": "fk", "-8": "fbm",
                            "1": "c", "4": "b", "5": "k", "8": "bm", "0": ""}

        # notes and accidentals dictionary lilypond
        self.notes_western2lily = {"g": "4", "a": "5", "b": "6", "c": "7", "d": "8", "e": "9", "f": "10"}

        self.notes_keyaccidentals = {"-8": "(- BUYUKMUCENNEP)", "-5": "(- KUCUK)", "-4": "(- BAKIYE)", "-1": "(- KOMA)",
                                     "+8": "BUYUKMUCENNEP", "+5": "KUCUK", "+4": "BAKIYE", "+1": "KOMA"}

        self.mapping = []
        # tempo
        self.bpm = None
        self.divisions = None

        # makam and usul
        self.information = None
        self.makam = None
        self.usul = None

        # accidentals
        self.keysig_accs = []
        self.keysig_keys = []

        # list of info of an individual note fetched from xml file
        self.measure = []

    def read_musicxml(self):
        global step, oct

        # getting beats and beat type
        self.beats = self.bpm = self.root.find('part/measure/attributes/time/beats').text
        self.beat_type = self.bpm = self.root.find('part/measure/attributes/time/beat-type').text

        # getting key signatures
        for e in self.root.findall('part/measure/attributes/key/key-step'): self.keysig_keys.append(e.text.lower())
        for e in self.root.findall('part/measure/attributes/key/key-accidental'):
            self.keysig_accs.append(self.list_accidentals[e.text])

        # makam and usul information
        try:
            self.information = self.root.find('part/measure/direction/direction-type/words').text
            self.makam = self.information.split(",")[0].split(": ")[1].lower()
            self.usul = self.information.split(",")[1].split(": ")[1].lower()
            print self.usul, self.makam
        except: pass

        # getting bpm
        self.bpm = float(self.root.find('part/measure/direction/sound').attrib['tempo'])
        self.divs = float(self.root.find('part/measure/attributes/divisions').text)
        self.qnotelen = 60000 / self.bpm

        print("rook OK")
        # measure
        for measure in self.root.findall('part/measure'):
            temp_measure = []

            # all notes in selected measure
            for note in measure.findall('note'):
                if note.find('duration'):
                    extra = None
                    dur = note.find('duration').text
                    # note inf
                    try:
                        step = note.find('pitch/step').text.lower()
                        oct = note.find('pitch/octave').text
                        rest = 0
                        extra = int(note.find('extra').text)
                        print extra
                    except:
                        try:
                            rest = note.find('rest')
                            if type(rest) == type(None): rest = 0
                            else:
                                rest = 1
                                step = "r"
                                oct = "r"
                        except: rest = 0

                    # accident inf
                    try:
                        acc = note.find('accidental').text
                        if type(acc) == type(None): acc = 0
                        elif acc == self.b_koma: acc = -1
                        elif acc == self.b_bakiyye: acc = -4
                        elif acc == self.b_kmucennep: acc = -5
                        elif acc == self.b_bmucennep: acc = -8

                        elif acc == self.d_koma: acc = +1
                        elif acc == self.d_bakiyye: acc = +4
                        elif acc == self.d_kmucennep: acc = +5
                        elif acc == self.d_bmucennep: acc = +8
                    except: acc = 0

                    # dotted or not
                    try:
                        dot = note.find('dot')
                        if type(dot) == type(None): dot = 0
                        else: dot = 1
                    except: dot = 0

                    # tuplet or not
                    try:
                        tuplet = note.find('time-modification')
                        if type(tuplet) == type(None): tuplet = 0
                        else: tuplet = 1
                    except: tuplet = 0

                    # lyrics
                    try:
                        lyric = note.find('lyric/text').text
                        if type(lyric) == type(None): lyric = ""
                        else: lyric = lyric
                    except: lyric = ""

                    # appending attributes to the temp note
                    normal_dur = int(self.qnotelen * float(dur) / self.divs) / self.qnotelen
                    temp_note = [step, oct, acc, dot, tuplet, rest, normal_dur, extra, lyric]
                    temp_measure.append(temp_note)

            # adding temp measure to the measure
            self.measure.append(temp_measure)

    def ly_writer(self):
        curr_path = os.path.dirname(os.path.abspath(__file__))
        # connecting database, trying to get information for beams in lilypond
        conn = sqlite3.connect(os.path.join(curr_path, "makam_db"))
        c = conn.cursor()

        # getting the components for the given makam
        c.execute('SELECT * FROM usul WHERE NAME="{0}"'.format(self.usul.title()))
        data = c.fetchone()
        # if beam information is exist
        if data is not None:
            if data[-1] is not None:
                strokes = data[-1].replace("+", " ")
                self.ly_stream.append('''\n\t\\set Staff.beatStructure = #\'({0})\n'''.format(strokes))

        if data is None:
            c.execute('SELECT * FROM usul WHERE NAMEENG="{0}"'.format(self.usul.lower()))
            data = c.fetchone()
            if data is not None:
                if data[-1] is not None:
                    strokes = data[-1].replace("+", " ")
                    self.ly_stream.append('''\n\t\\set Staff.beatStructure = #\'({0})\n'''.format(strokes))

        self.ly_stream.append("\n\t\\time")

        # time signature
        try: self.ly_stream.append(self.beats + "/" + self.beat_type)
        except: print("No time signature!!!")

        self.ly_stream.append("\n\t\\clef treble \n\t\\set Staff.keySignature = #`(")

        accidentals_check = []
        temp_keysig = ""
        for i in range(0, len(self.keysig_keys)):
            accidentals_check.append(self.keysig_keys[i] + self.accidentals[self.keysig_accs[i].replace("+", "")])
            temp_keysig += "("
            temp_keysig += "( 0 . " + str(self.notes_western2lily[self.keysig_keys[i]]) + "). , " + str(self.notes_keyaccidentals[self.keysig_accs[i]])
            temp_keysig += ")"

            self.ly_stream.append(temp_keysig)
            temp_keysig = ""

        self.ly_stream.append(")")
        print accidentals_check
        
        line = len(self.ly_stream) + 5
        for xx, measure in enumerate(self.measure):
            self.ly_stream.append("\n\t")
            self.ly_stream.append("{")
            tuplet = 0

            pos = 0
            for note in measure:
                temp_note = ""
                temp_dur = 4 / note[6]                                              # normal duration

                # dotted
                if note[3] == 1:                                                    # dot flag
                    temp_note += str(note[0])                                       # step
                    temp_note += self.accidentals[str(note[2])]                     # accidental
                    temp_note += self.octaves[str(note[1])]                         # octave

                    temp_dur = 1 / (2 / temp_dur / 3)
                    temp_note += str(int(temp_dur))
                    temp_note += "."

                # tuplet
                elif note[4] == 1:                                                  # tuplet flag
                    if tuplet == 0:
                        tuplet = 4
                        temp_note += "\\tuplet 3/2 {"
                    temp_note += str(note[0])                                       # step
                    temp_note += self.accidentals[str(note[2])]                     # accidental
                    temp_note += self.octaves[str(note[1])]                         # octave

                    temp_dur = temp_dur * 2 / 3
                    temp_note += str(int(temp_dur))

                    tuplet -= 1
                    if tuplet == 1:
                        temp_note += " }"
                        tuplet = 0

                # nor
                else:
                    temp_note += str(note[0])
                    temp_note += self.accidentals[str(note[2])]
                    temp_note += self.octaves[str(note[1])]
                    temp_note += str(int(temp_dur))

                if note[7]:
                    self.mapping.append((note[7], pos + 4, line))
                
                # lyrics
                if note[-1] is not "":
                    if len(note[-1]) > 1:
                        if note[-1][1].isupper(): temp_note += '''^\\markup { \\left-align {\\bold \\translate #'(1 . 0) \"''' + u''.join(note[-1]).encode('utf-8').strip() + '''\"}}'''
                        else: temp_note += '''_\\markup { \\center-align {\\smaller \\translate #'(0 . -2.5) \"''' + u''.join(note[-1]).encode('utf-8').strip() + '''\"}}'''
                    else: temp_note += '''_\\markup { \\center-align {\\smaller \\translate #'(0 . -2.5) \"''' + u''.join(note[-1]).encode('utf-8').strip() + '''\"}}'''

                pos += len(temp_note) +1
                self.ly_stream.append(temp_note)
            line += 1
            self.ly_stream.append("} %measure " + str(xx + 1))
        self.ly_stream.append('''\n\t\\bar \"|.\"''')

    def run(self):
        ly_initial = """
\\include "makam.ly"
{
  %\\override Score.SpacingSpanner.strict-note-spacing = ##t
  %\\set Score.proportionalNotationDuration = #(ly:make-moment 1/8)
             """
        self.read_musicxml()
        self.ly_writer()
        ly_string = " ".join(self.ly_stream)

        fname = self.file.split(".")[0]
        outfile = codecs.open(fname + ".ly", 'w')
        outfile.write(ly_initial + ly_string + "\n}")
        outfile.close()

        outfile = codecs.open(fname + ".json", 'w')
        json.dump(self.mapping, outfile)
        outfile.close()
