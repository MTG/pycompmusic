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

#sys.path.insert(0, os.path.join(
#        os.path.dirname(os.path.abspath(__file__)), ".."))
#from dunya import settings
#from django.core.management import setup_environ
#setup_environ(settings)

#from carnatic.models import Raaga, Taala

reraaga = re.compile(r"\braa?gam?[0-9]*\b")
retaala = re.compile(r"\btaa?lam?[0-9]*\b")
retaal = re.compile(r"\btaa?la?[0-9]*\b")
reraag = re.compile(r"\braa?ga?[0-9]*\b")
resection = re.compile(r"\bsection[0-9]*\b")
remakam = re.compile(r"\bmakam\b")
reusul = re.compile(r"\busul\b")
reform = re.compile(r"\bform[0-9]*\b")
rehindustaniform = re.compile(r"\bform([0-9])?:? ?(.*)\b")
relaya = re.compile(r"\blaya([0-9])?:? ?(.*)\b")


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
    return re.search(remakam, tag) is not None

def has_usul(tag):
    """ Makam usul tag """
    return re.search(reusul, tag) is not None

def has_makam_form(tag):
    """ Makam form """
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
    makam = re.sub(r" ?: ?", " ", makam)
    makam = re.sub(remakam, "", makam)
    return makam.strip()

def parse_usul(usul):
    usul = usul.strip()
    usul = re.sub(r" ?: ?", " ", usul)
    usul = re.sub(reusul, "", usul)
    return usul.strip()

def parse_makam_form(form):
    form = form.strip()
    form = re.sub(r" ?: ?", " ", form)
    form = re.sub(reform, "", form)
    return form.strip()


def parse_raag(raag):
    raag = raag.strip()
    reraag = re.compile(r"\braa?ga?([0-9])?:? ?(.*)\b")
    match = re.search(reraag, raag)
    if match:
        number = match.group(1)
        if number:
            number = int(number)
        mraag = match.group(2)
        return (number, mraag)
    else:
        return (None, None)

def parse_taal(taal):
    retaal = re.compile(r"\btaa?la?([0-9])?:? ?(.*)\b")
    taal = taal.strip()
    match = re.search(retaal, taal)
    if match:
        number = match.group(1)
        if number:
            number = int(number)
        mtaal = match.group(2)
        return (number, mtaal)
    else:
        return (None, None)

def parse_hindustani_form(form):
    form = form.strip()
    match = re.search(rehindustaniform, form)
    if match:
        number = match.group(1)
        if number:
            number = int(number)
        form = match.group(2)
        return (number, form)
    else:
        return (None, None)

def parse_laya(laya):
    laya = laya.strip()
    match = re.search(relaya, laya)
    if match:
        number = match.group(1)
        if number:
            number = int(number)
        laya = match.group(2)
        return (number, laya)
    else:
        return (None, None)
