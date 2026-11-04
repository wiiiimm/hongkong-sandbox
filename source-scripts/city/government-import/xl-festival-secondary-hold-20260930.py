"""Save resumable exact-source support diagnostics without granting installation credit."""
from shapely.geometry import MultiPoint, Polygon
from run import ROOT, read, save, digest
BASE=ROOT/'docs/astra-city/government-import/government-xl-remaining-20260923'
DOC=BASE/'festival-secondary-terrain-diagnostic-20260930'
def run():
    probe=read(DOC/'support-probe-raw.json')['rows'][0]
    selected=read(DOC/'selection.json.gz')['rows'][0]
    assert selected['candidate']['entry']['sha256']==probe['sourceSHA256']
    masked=read(BASE/'festival-secondary-mask-eval-20260930.json')['rows'][0]
    foundation=read(BASE/'festival-secondary-mask-foundation-20260930.json')['rows'][0]
    assert not masked['remainingBlockedUids'] and foundation['strictFoundationAccepted']
    form=selected['source']['building']; polygon=Polygon(form['rings'][0],form['rings'][1:])
    hull=MultiPoint([(x,z) for x,y,z in probe['contactPositions']]).convex_hull
    coverage=hull.intersection(polygon).area/polygon.area
    support=next(m for r in read(BASE/'complex-mask-foundations-20260929.json')['rows'] for m in r['models'] if m['uid']==probe['supportUid'])
    assert not support['strictFoundationAccepted']
    paths=[DOC/'selection.json.gz',DOC/'identity-resolution.json',DOC/'validation.json',DOC/'support-probe-raw.json',BASE/'festival-secondary-mask-eval-20260930.json',BASE/'festival-secondary-mask-foundation-20260930.json',BASE/'complex-mask-foundations-20260929.json',BASE/'festival-support-terrain-options-20260930.json',*[BASE/'festival-pair-rescue-diagnostic-20260930'/name for name in ('result.json','identity-resolution.json','validation.json','neighbour-checks.json','native-neighbour-checks.json')]]
    result={'uid':probe['uid'],'humanStatus':'held-unknown','primaryHold':'terrain-contact',
        'detailedHold':'candidate-support-terrain-rescue-awaiting-pair-acceptance',
        'nextWork':'A 3.183 m2 parent-terrain preservation diagnostic clears all seven buried support faces. Support identity and terrain coverage/overlap pass. The only neighbor flagged is secondary source landsd/104302:0, so the pair needs joint acceptance. Complete runtime-warning resolution, full pair foundation/contact and staged/live browser gates before publication. The pair remains uninstalled; do not move or remodel either source.',
        'needsHumanDecision':False,'needsAIModeling':False,'nextActionType':'compute-investigation',
        'neighborFormsPassed':91,'fullyBuriedFaces':0,'supportUid':probe['supportUid'],
        'supportInstalled':False,'terrainRescue':read(BASE/'festival-support-terrain-options-20260930.json')['diagnosticParentRescue'],'supportContactSamples':probe['samples'],'supportContactWithin05':probe['within05'],
        'contactHullTargetCoverage':coverage,'supportFoundation':support['foundation'],
        'sourceSHA256':probe['sourceSHA256'],'supportSHA256':probe['supportSHA256'],
        'evidence':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in paths],
        'aiCalls':0,'modelGeometryChanges':0,'publication':False}
    save(DOC/'held.json',result)
    print({k:result[k] for k in ('uid','supportContactSamples','supportContactWithin05','contactHullTargetCoverage','nextActionType')})
if __name__=='__main__':run()
