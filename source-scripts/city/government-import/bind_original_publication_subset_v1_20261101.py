"""Bind an exact publication subset to completed full model-only scope/contacts.

Copies complete proofs byte-for-byte. No new measurements, source edits,
approvals, missing-neighbour exemptions or publication are introduced.
"""
import argparse,shutil
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','selection','scope','contacts']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';assert all(n.startswith('government-xl-')and'/'not in n for n in vars(a).values());refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        f=base/batch/name;assert digest(f.read_bytes())==pins[batch][str(f.relative_to(ROOT))];refs.append(f);return read(f)
    selection=take(a.selection,'selection.json.gz');scope=take(a.scope,'summary.json');contacts=take(a.contacts,'summary.json')
    scope_path=base/a.scope/'summary.json';assert pins[a.contacts][str(scope_path.relative_to(ROOT))]==digest(scope_path.read_bytes())
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==scope['currentManifestSHA256'];refs.append(manifest)
    sources={r['uid']:r for r in selection['rows']};assert sources and len(sources)==len(selection['rows'])
    old={r['uid']:r for r in scope['rows']};assert len(old)==len(scope['rows'])and set(sources)<=set(old)
    rows=[]
    for uid,source in sources.items():
        assert source['sourceSHA256']==old[uid]['sourceSHA256'];asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset);rows.append(old[uid])
    scope_batch=a.batch+'-scope';out=base/scope_batch;assert not out.exists()
    for uid in sources:
        name=uid.split('/')[1]+'-forms.json.gz';take(a.scope,name);out.mkdir(exist_ok=True);shutil.copyfile(base/a.scope/name,out/name);assert digest((out/name).read_bytes())==pins[a.scope][str((base/a.scope/name).relative_to(ROOT))]
    subset={**scope,'uids':sorted(sources),'rows':rows,'qualification':scope['qualification']+' Exact selected publication subset; every selected source retains its complete original actor/form scope. No approval.'};save(out/'summary.json',subset)
    module('publication_subset_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(scope_batch,'exact-complete-publication-subset-scope-binding',list(dict.fromkeys(refs)),subset)
    native_batch=a.batch+'-native';out=base/native_batch;assert not out.exists();out.mkdir()
    selected=[r for r in contacts['rows']if r['uid']in sources];separated=[r for r in contacts.get('strictlySeparatedNativePairs',[])if r['uid']in sources]
    expected={(r['uid'],n['uid'])for r in rows for n in r['nearbyNativeActors']};measured={(r['uid'],r['nativeUid'])for r in selected};away={(r['uid'],r['nativeUid'])for r in separated};assert not measured&away and measured|away==expected
    for r in selected:
        assert r['sourceSHA256']==sources[r['uid']]['sourceSHA256']and len(r['modes'])==4 and{m['mode']for m in r['modes']}=={'original','literal','leftF32','balancedF32'}
        for m in r['modes']:
            assert m['sourceFaces']==sources[r['uid']]['triangles'];name=r['uid'].split('/')[1]+'--'+r['nativeUid'].split('/')[1]+'--'+m['mode']+'.json.gz';proof=take(a.contacts,name);assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0 and len(proof['contacts'])==m['finiteContactPairs'];shutil.copyfile(base/a.contacts/name,out/name);assert digest((out/name).read_bytes())==pins[a.contacts][str((base/a.contacts/name).relative_to(ROOT))]
    for name in ['native-input.json.gz','native-attributes.json.gz']:
        take(a.contacts,name);shutil.copyfile(base/a.contacts/name,out/name);assert digest((out/name).read_bytes())==pins[a.contacts][str((base/a.contacts/name).relative_to(ROOT))]
    refs.extend([base/scope_batch/'result.json',base/scope_batch/'summary.json'])
    result={**contacts,'uids':sorted(sources),'rows':selected,'strictlySeparatedNativePairs':separated,'qualification':contacts['qualification']+' Exact publication subset of existing complete proofs; all selected actors/neighbours and raw verdicts retained. Native arrays/proofs copied byte-for-byte; unselected source rows grant no acceptance.'};save(out/'summary.json',result)
    module('publication_subset_native_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(native_batch,'exact-complete-publication-subset-native-contact-binding',list(dict.fromkeys(refs)),result)
    print(dict(sources=len(sources),completeNativePairs=len(expected),newMeasurements=0,publication=False),flush=True)

if __name__=='__main__':main()
