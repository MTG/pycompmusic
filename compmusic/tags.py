#!/usr/bin/env python

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

reraaga = re.compile(r"\braa?gam?\b")
retaala = re.compile(r"\btaa?lam?\b")
remakam = re.compile(r"\bmakam\b")
reusul = re.compile(r"\busul\b")
reform = re.compile(r"\bform\b")

def has_raaga(tag):
    return re.search(reraaga, tag) is not None

def has_taala(tag):
    return re.search(retaala, tag) is not None

def has_makam(tag):
    return re.search(remakam, tag) is not None

def has_usul(tag):
    return re.search(reusul, tag) is not None

def has_form(tag):
    return re.search(reform, tag) is not None

def parse_raaga(raaga):
    raaga = raaga.strip()
    raaga = re.sub(r" ?: ?", " ", raaga)
    raaga = re.sub(r" ?raa?gam?[0-9]* ?", "", raaga)
    return raaga

def parse_taala(taala):
    taala = taala.strip()
    taala = re.sub(r" ?: ?", " ", taala)
    taala = re.sub(r" ?taa?lam?[0-9]* ?", "", taala)
    return taala

def parse_makam(makam):
    makam = makam.strip()
    makam = re.sub(r" ?: ?", " ", makam)
    makam = re.sub(r" ?makam ?", "", makam)
    return makam

def parse_usul(usul):
    usul = usul.strip()
    usul = re.sub(r" ?: ?", " ", usul)
    usul = re.sub(r" ?usul ?", "", usul)
    return usul

def parse_form(form):
    form = form.strip()
    form = re.sub(r" ?: ?", " ", form)
    form = re.sub(r" ?form ?", "", form)
    return form

def main():
    tags = open(sys.argv[1]).readlines()
    r = []
    t = []
    for tg in tags:
        if re.search(reraaga, tg):
            r.append(parse_raaga(tg))
        if re.search(retaala, tg):
            t.append(parse_taala(tg))
    rfp = open("raaga_list", "w")
    tfp = open("taala_list", "w")
    for ra in sorted(list(set(r))):
        try:
            Raaga.objects.fuzzy(ra)
        except Raaga.DoesNotExist:
            rfp.write("%s\n" % ra)
    for ta in sorted(list(set(t))):
        try:
            Taala.objects.fuzzy(ta)
        except Taala.DoesNotExist:
            tfp.write("%s\n" % ta)
    rfp.close()
    tfp.close()


if __name__ == "__main__":
    main()
