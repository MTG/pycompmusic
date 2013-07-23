#!/usr/bin/env python

import sys
import os
import re
import logging
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

