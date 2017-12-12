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


import logging
import re

logging.basicConfig(level=logging.INFO)

reraaga = re.compile(r"\braa?gam?\b")
retaala = re.compile(r"\btaa?lam?\b")


def has_raaga(tag):
    return re.search(reraaga, tag)


def has_taala(tag):
    return re.search(retaala, tag)


def parse_raaga(raaga):
    raaga = raaga.strip()
    number = re.search(r"([0-9]+)", raaga)
    if number:
        position = int(number.group(0))
    else:
        position = 0
    raaga = re.sub(r" ?: ?", " ", raaga)
    raaga = re.sub(r" ?raa?gam?[0-9]* ?", "", raaga)
    return (position, raaga)


def parse_taala(taala):
    taala = taala.strip()
    number = re.search(r"([0-9]+)", taala)
    if number:
        position = int(number.group(0))
    else:
        position = 0
    taala = re.sub(r" ?: ?", " ", taala)
    taala = re.sub(r" ?taa?lam?[0-9]* ?", "", taala)
    return (position, taala)
