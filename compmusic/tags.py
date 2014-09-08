#!/usr/bin/env python
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


import sys
import os
import re
import logging
logging.basicConfig(level=logging.INFO)

reraaga = r"\braa?gam?[0-9]*\b"
retaala = r"\btaa?lam?[0-9]*\b"
retaal = r"\btaa?la?[0-9]*\b"
reraag = r"\braa?ga?[0-9]*\b"
resection = r"\bsection[0-9]*\b"
rehindustaniform = r"\bform([0-9])?:? ?(.*)\b"
relaya = r"\blaya([0-9])?:? ?(.*)\b"


def has_raaga(tag):
    """ Carnatic raaga tag """
    return re.search(reraaga, tag) is not None

def has_taala(tag):
    """ Carnatic taala tag """
    return re.search(retaala, tag) is not None

def has_raag(tag):
    """ Hindustani raag tag """
    return re.search(reraag, tag) is not None

def has_taal(tag):
    """ Hindustani taal tag """
    return re.search(retaal, tag) is not None

def has_laya(tag):
    """ Hindustani laya tag """
    return re.search(relaya, tag) is not None

def has_section(tag):
    """ Hindustani section tag """
    return re.search(resection, tag) is not None

def has_makam(tag):
    """ Makam tag """
    remakam = r"\bmakam([0-9]|\b)"
    return re.search(remakam, tag) is not None

def has_usul(tag):
    """ Makam usul tag """
    reusul = r"\busul([0-9]|\b)"
    return re.search(reusul, tag) is not None

def has_makam_form(tag):
    """ Makam form """
    reform = r"\bform([0-9]|\b)"
    return re.search(reform, tag) is not None

def has_hindustani_form(tag):
    """ Hindustani form """
    return re.search(rehindustaniform, tag) is not None

def parse_raaga(raaga):
    raaga = raaga.strip()
    raaga = re.sub(r" ?: ?", " ", raaga)
    raaga = re.sub(reraaga, "", raaga)
    return raaga.strip()

def parse_taala(taala):
    taala = taala.strip()
    taala = re.sub(r" ?: ?", " ", taala)
    taala = re.sub(retaala, "", taala)
    return taala.strip()


def parse_makam(makam):
    makam = makam.strip()
    remakam = r"\bmakam ?([0-9])? ?:? ?(.*)\b"
    return _parse_num_and_value(remakam, makam)

def _parse_num_and_value(expression, target):

    # use re.U flag to make \b match unicode char classess too
    match = re.search(expression, target, re.U)
    if match:
        number = match.group(1)
        if number:
            number = int(number)
        else:
            number = 0
        val = match.group(2)
        return (number, val)
    else:
        return (None, None)

def parse_usul(usul):
    usul = usul.strip()
    reusul = r"\busul ?([0-9])? ?:? ?(.*)\b"
    return _parse_num_and_value(reusul, usul)

def parse_makam_form(form):
    form = form.strip()
    reform = r"\bform ?([0-9])? ?:? ?(.*)\b"
    return _parse_num_and_value(reform, form)


def parse_raag(raag):
    raag = raag.strip()
    reraag = r"\braa?ga?([0-9])?:? ?(.*)\b"
    return _parse_num_and_value(reraag, raag)

def parse_taal(taal):
    retaal = r"\btaa?la?([0-9])?:? ?(.*)\b"
    taal = taal.strip()
    return _parse_num_and_value(retaal, taal)

def parse_hindustani_form(form):
    form = form.strip()
    return _parse_num_and_value(rehindustaniform, form)

def parse_laya(laya):
    laya = laya.strip()
    return _parse_num_and_value(relaya, laya)

def group_makam_tags(makams, forms, usuls):
    makams.sort(key=lambda i: i[0])
    forms.sort(key=lambda i: i[0])
    usuls.sort(key=lambda i: i[0])
    max_size = max(makams[-1][0] if makams else 0,
            forms[-1][0] if forms else 0,
            usuls[-1][0] if usuls else 0)

    ret = []
    for i in range(max_size+1):
        m = makams[0] if makams else (None, None)
        f = forms[0] if forms else (None, None)
        u = usuls[0] if usuls else (None, None)
        thisr = {}
        if m[0] == i:
            thisr["makam"] = m[1]
            makams = makams[1:]
        if f[0] == i:
            thisr["form"] = f[1]
            forms = forms[1:]
        if u[0] == i:
            thisr["usul"] = u[1]
            usuls = usuls[1:]

        ret.append(thisr)
    return ret
