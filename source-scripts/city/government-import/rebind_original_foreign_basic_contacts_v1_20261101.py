"""Reuse complete source/BASIC contact proofs only for byte-identical current inputs.

No terrain, support, native, physical or publication approval transfers.
"""
import argparse
import json
import subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def identical_array(old,new,dtype):
    a=np.asarray(old,dtype=dtype);b=np.asarray(new,dtype=dtype)
    assert a.shape==b.shape and a.tobytes()==b.tobytes(), 'Complete represented arrays differ'
    return digest(b.tobytes())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','uid','prior','prior-runtime','prior-attributes','runtime','attributes','scope','lease']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.prior,a.prior_runtime,a.prior_attributes,a.runtime,a.attributes,a.scope])and not out.exists()
    lease=read(Path(a.lease));assert reservations.owns(lease)
    pins={};refs=[Path(__file__)];receipts={}
    def take(n,filename):
        if n not in pins:receipts[n],pins[n]=authenticate(base/n);refs.append(base/n/'result.json')
        path=base/n/filename;assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selected=take(a.runtime,'selection.json.gz');current=next(r for r in selected['rows']if r['uid']==a.uid)
    prior=next(r for r in take(a.prior_runtime,'selection.json.gz')['rows']if r['uid']==a.uid)
    report=take(a.prior,'summary.json');assert report['uids']==[a.uid]and report['foreignPairs']==len(report['rows'])
    oldbasic=take(a.prior,'basic.json');assert oldbasic['startAndEndInputHashesVerified']and oldbasic['completeRecursiveProductionModuleClosure']
    scope=take(a.scope,'summary.json');sr=next(r for r in scope['rows']if r['uid']==a.uid)
    forms=take(a.scope,a.uid.split('/')[1]+'-forms.json.gz');native={n['uid']for n in sr['nearbyNativeActors']}
    obligations={f['building']['uid']for f in forms}-{a.uid}-native
    assert obligations=={r['foreignUid']for r in report['rows']}, 'Current foreign pair scope differs'
    resources={'building:'+f['building']['uid']for f in forms}|{'building:'+u for u in native}
    assert resources<=set(lease['resources'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']==scope['currentManifestSHA256'];refs.append(manifest)
    assert current['sourceSHA256']==prior['sourceSHA256']==sr['sourceSHA256']
    for row in [prior,current]:
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
        assert row['candidate']['entry']['rootTranslation']==[-834500,0,816500]and row['candidate']['entry'].get('verticalPlacementOffsetHKPD',0)==0
    decoder=HERE/'exact_packed_world_geometry_20261009.py';assert digest(decoder.read_bytes())==pins[a.prior][str(decoder.relative_to(ROOT))];refs.append(decoder)
    source_hashes={'original':digest(decode_original_world_triangles((ROOT/current['candidate']['path']).read_bytes()).astype('<f8').tobytes())}
    oldattr=next(r for r in take(a.prior_attributes,'attributes.json.gz')['rows']if r['uid']==a.uid);newattr=next(r for r in take(a.attributes,'attributes.json.gz')['rows']if r['uid']==a.uid)
    assert oldattr['sourceSHA256']==newattr['sourceSHA256']==current['sourceSHA256']
    identical_array(oldattr['completeOriginalIndex'],newattr['completeOriginalIndex'],'<i8')
    ix=np.asarray(newattr['completeOriginalIndex']).reshape(-1,3)
    for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
        identical_array(oldattr[field],newattr[field],'<f8')
        source_hashes[mode]=digest(np.asarray(newattr[field],dtype='<f8').reshape(-1,3)[ix].tobytes())
    for f in forms:
        path=ROOT/'3d-viewer'/f['tile'];assert digest(path.read_bytes())==f['tileSHA256'];assert next(b for b in read(path)['buildings']if b['uid']==f['building']['uid'])==f['building'];refs.append(path)
    save(out/'basic-inputs.json',dict(manifestSHA256=scope['currentManifestSHA256'],currentInputHashes=scope['currentFormTileHashes'],rows=[dict(building=f['building'],tile='3d-viewer/'+f['tile'])for f in forms]))
    tool=HERE/'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs';assert digest(tool.read_bytes())==pins[a.prior][str(tool.relative_to(ROOT))];refs.append(tool)
    with(out/'capture.log').open('w')as log:subprocess.run(['node',str(tool),str((out/'basic-inputs.json').relative_to(ROOT)),str((out/'basic.json').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    fresh=read(out/'basic.json');assert fresh['startAndEndInputHashesVerified']and fresh['completeRecursiveProductionModuleClosure']
    oldby={r['uid']:r for r in oldbasic['rows']};newby={r['uid']:r for r in fresh['rows']};assert set(oldby)==set(newby)=={f['building']['uid']for f in forms}
    geometry=[]
    for uid,row in sorted(newby.items()):
        old=oldby[uid];assert old['currentBuilding']==row['currentBuilding']
        position=identical_array(old['position'],row['position'],'<f8');index=identical_array(old['index'],row['index'],'<i8')
        geometry.append(dict(uid=uid,completePositionSHA256=position,completeIndexSHA256=index))
    # Any code involved in the old BASIC geometry remains unchanged too.
    for name,sha in oldbasic['inputHashes'].items():
        if name.endswith(('.js','.mjs')):assert digest((ROOT/name).read_bytes())==sha;refs.append(ROOT/name)
    proofs=[]
    for row in report['rows']:
        assert row['uid']==a.uid
        for m in row['modes']:
            name=a.uid.split('/')[1]+'--'+row['foreignUid'].split('/')[1]+'--'+m['mode']+'.json.gz';raw=take(a.prior,name)
            assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0 and len(raw['contacts'])==m['allFiniteContactPairs']
            proofs.append(dict(path=str((base/a.prior/name).relative_to(ROOT)),sha256=digest((base/a.prior/name).read_bytes()),uid=a.uid,foreignUid=row['foreignUid'],mode=m['mode']))
    for name,sha in fresh['inputHashes'].items():assert digest((ROOT/name).read_bytes())==sha;refs.append(ROOT/name)
    assert digest(manifest.read_bytes())==selected['manifestSHA256']and reservations.owns(lease)
    coimports={r['uid']for r in selected['rows']};retained=[r for r in report['rows']if r['foreignUid']not in coimports]
    result=dict(uids=[a.uid],sourceSHA256=current['sourceSHA256'],sourceWorldSHA256ByMode=source_hashes,currentManifestSHA256=selected['manifestSHA256'],completeForeignPairs=len(obligations),completePairModeRows=len(proofs),newFinitePairComputations=0,currentBasicCompleteGeometry=geometry,rawPriorRows=report['rows'],reusedProofs=proofs,retainedForeignPairs=len(retained),retainedPositiveOriginalPairs=[r for r in retained if next(m['positiveContactPairs']for m in r['modes']if m['mode']=='original')>0],nativeUidsRequireIndependentChecks=sorted(native),sourceGeometryChanges=0,rawWarningsPreserved=True,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' Exact current form/pair set, complete recursive production BASIC inputs and every complete position/index plus literal/F32 source array match the authenticated previous computation byte-for-byte, including signed zeros/order. Original source asset and decoder unchanged. Manifest may differ only because inputs were separately recaptured and validated; no historical geometry proof or current scope is guessed, and no native/terrain/physical approval transfers.')
    save(out/'summary.json',result)
    module('source_basic_contact_rebind_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-current-input-rebinding-of-complete-source-basic-contact-diagnostics',list(dict.fromkeys(refs)),result)
    print(dict(foreignPairs=len(obligations),reusedPairModeRows=len(proofs),newFinitePairComputations=0,retainedForeignPairs=len(retained)),flush=True)

if __name__=='__main__':main()
