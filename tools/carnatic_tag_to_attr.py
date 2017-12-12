from __future__ import print_function

import carnatic

import compmusic


def rt_for_recording(recording):
    raaga = None
    taala = None
    for t in recording.get("tag-list", []):
        n = t["name"]
        r = get_raaga(n)
        if r:
            raaga = r
        t = get_taala(n)
        if t:
            taala = t
    return raaga, taala


def get_taala(name):
    taala = None
    if compmusic.tags.has_taala(name):
        ttag = compmusic.tags.parse_taala(name)
        try:
            taala = carnatic.models.Taala.objects.fuzzy(ttag)
        except carnatic.models.Taala.DoesNotExist:
            taala = None
    return taala


def get_raaga(name):
    raaga = None
    if compmusic.tags.has_raaga(name):
        rtag = compmusic.tags.parse_raaga(name)
        try:
            raaga = carnatic.models.Raaga.objects.fuzzy(rtag)
        except carnatic.models.Raaga.DoesNotExist:
            raaga = None
    return raaga


recordingtags = {}
In[39]: for r in recordings:
    rid = r["id"]
    if rid not in recordingtags:
        rg, ta = rt_for_recording(r)
        recordingtags[rid] = {"raaga": rg.name.encode("utf-8") if rg else None,
                              "taala": ta.name.encode("utf-8") if ta else None}

json.dump(recordingtags, open("carnatic-recording-to-tag.json", "w"))

releases = compmusic.get_releases_in_collection(compmusic.CARNATIC_COLLECTION)

In[19]: for w in wattr:
    raaga = None
    taala = None
    for a in w["attribute-list"]:
        if a["type"] == u'T\u0101la (Carnatic)':
            taala = a["attribute"]
        elif a["type"] == u'R\u0101ga (Carnatic)':
            raaga = a["attribute"]
    wid = w["id"]
    if wid not in workmap:
        workmap[wid] = {"raaga": raaga, "taala": taala}

In[19]: for rel in releases:
    recs = compmusic.get_recordings_from_release(rel)
    for rec in recs:
        recordings.append(compmusic.mb.get_recording_by_id(rec, includes=["tags"])["recording"])
        for w in compmusic.get_works_from_recording(rec):
            works.append(compmusic.mb.get_work_by_id(w["target"]))
    print(rel)

json.dump(works, open("carnatic-work-list-unedited.json", "w"))
json.dump(recordings, open("carnatic-recording-list-unedited.json", "w"))
for rel in releases:
    recs = compmusic.get_recordings_from_release(rel)
    for rec in recs:
        recordings.append(compmusic.mb.get_recording_by_id(rec, includes=["tags", "work-rels"])["recording"])
    print(rel)
json.dump(recordings, open("carnatic-recording-and-work-list-unedited.json", "w"))

wattr = [w["work"] for w in works if "attribute-list" in w["work"]]

json.dump(wattr, open("carnatic-works-with-attributes.json", "w"))
workmap = {}

In[19]: for w in wattr:
    raaga = None
    taala = None
    for a in w["attribute-list"]:
        if a["type"] == u'T\u0101la (Carnatic)':
            taala = a["attribute"]
        elif a["type"] == u'R\u0101ga (Carnatic)':
            raaga = a["attribute"]
    wid = w["id"]
    if wid not in workmap:
        workmap[wid] = {"raaga": raaga.encode("utf-8") if raaga else None,
                        "taala": taala.encode("utf-8") if taala else None}
json.dump(workmap, open("carnatic-works-to-attribute.json", "w"))

worktorec = collections.defaultdict(list)
rectowork = collections.defaultdict(list)

for r in recordings:
    rid = r["id"]
    for w in r.get("work-relation-list", []):
        wid = w["target"]
        worktorec[wid].append(rid)
        rectowork[rid].append(wid)
newworktorec = {}
newrectowork = {}
for k, v in worktorec.items():
    newworktorec[k] = list(set(v))
for k, v in rectowork.items():
    newrectowork[k] = list(set(v))
json.dump(newworktorec, open("carnatic-work-to-recordings.json", "w"))
json.dump(newrectowork, open("carnatic-recording-to-works.json", "w"))

rectags = {}
for r in rlist:
    data = {}
    for t in r.get("tag-list", []):
        n = t["name"]
        if compmusic.tags.has_raaga(n):
            data["raaga"] = n
        elif compmusic.tags.has_taala(n):
            data["taala"] = n
    id = r["id"]
    if data and id not in rectags:
        rectags[id] = data

json.dump(rectags, open("carnatic-recording-to-mb-tags.json", "w"))

worknoattr = []
In[19]: for w in allworks:
    if "attribute-list" not in w["work"]:
        worknoattr.append(w["work"])
json.dump(worknoattr, open("carnatic-works-no-attributes.json", "w"))
