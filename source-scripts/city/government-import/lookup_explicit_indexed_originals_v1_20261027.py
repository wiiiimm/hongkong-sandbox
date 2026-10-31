"""Nominate exact cached companions across source sheets, never source acceptance."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','capture','discovery']:parser.add_argument('--'+k,required=True)
    parser.add_argument('--uid',action='append',required=True)
    a=parser.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    assert len(set(a.uid))==len(a.uid)and 0<len(a.uid)<=8
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    _,pins=authenticate(base/a.capture);selection=base/a.capture/'selection.json.gz'
    assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))]
    sources=read(selection)['rows'];assert sources
    discovery_folder=base/a.discovery;_,discovery_pins=authenticate(discovery_folder)
    discovery_path=discovery_folder/'complete-cached-records.json.gz'
    assert digest(discovery_path.read_bytes())==discovery_pins[str(discovery_path.relative_to(ROOT))]
    indexed=read(discovery_path);assert indexed['nativeRun']==NATIVE_RUN
    refs=[Path(__file__),base/a.capture/'result.json',selection,discovery_folder/'result.json',discovery_path]
    forms={}
    for tile in sorted({r['source']['tile']for r in sources}):
        p=ROOT/'3d-viewer'/tile;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
        for form in read(p)['buildings']:forms[form['uid']]=form
    assert set(a.uid)<=forms.keys()
    chosen=[]
    for uid in a.uid:
        form=forms[uid]
        matches=[r for r in indexed['rows'] if any(v['uid']==uid and v.get('buildingCSUID')==form['buildingCSUID'] and v.get('objectId')==form['objectId'] for v in r['model'].get('matching',{}).get('viewerMatches',[]))]
        assert len(matches)==1,'Exact UID/CSUID/ObjectID source lookup is missing or ambiguous'
        chosen.append(matches[0])
    keys={(r['cacheKey'],r['nativeResultSHA256']) for r in chosen};assert len(keys)==1,'Select each source sheet separately'
    key,sha=next(iter(keys))
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT 1 FROM astra_modelling.native_stage_members WHERE run_id=%s AND cache_key=%s',(NATIVE_RUN,key)).fetchone()
        actual,native=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert actual==sha
        for r in chosen:assert next(m for m in native['models'] if m['modelId']==r['model']['modelId'])==r['model']
    rows=[]
    for uid in a.uid:
        form=forms[uid]
        models=[m for m in native['models']if any(v['uid']==uid and v.get('buildingCSUID')==form['buildingCSUID']and v.get('objectId')==form['objectId']for v in m.get('matching',{}).get('viewerMatches',[]))]
        assert len(models)==1,'Ambiguous source lookup requires explicit investigation'
        rows.append(dict(uid=uid,currentForm=form,matchedOriginalModels=models,matchCount=1,identityAccepted=False))
    result=dict(uids=sorted(r['uid']for r in sources),relatedUIDs=a.uid,nativeCacheKey=key,nativeResultSHA256=sha,rows=rows,sourceGeometryChanges=0,installationApproved=False,qualification='Exact current tile/UID/CSUID/objectId and immutable cached model nomination only. No source identity, physical support, permit grouping or publication approval.')
    save(out/'lookup.json',result)
    module('explicit_adjacent_lookup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-explicit-cross-sheet-original-source-lookup',refs,result)
    print([dict(uid=r['uid'],modelId=r['matchedOriginalModels'][0]['modelId'],faces=r['matchedOriginalModels'][0]['triangles'])for r in rows],flush=True)


if __name__=='__main__':main()
