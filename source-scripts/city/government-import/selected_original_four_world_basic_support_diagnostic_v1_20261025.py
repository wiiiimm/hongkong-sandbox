"""Record finite clearance and canonical BASIC support in four worlds, including failures; never approve."""
import argparse
from pathlib import Path
import numpy as np
import subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from finite_height_clearance_bound_v1_20261023 import verify as finite_bound


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','basic-contacts','continuous']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selected=take(a.runtime,base/a.runtime/'selection.json.gz');geometry={r['uid']:r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']};attributes={r['uid']:r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']};basic={r['uid']:r for r in take(a.basic_contacts,base/a.basic_contacts/'checks.json.gz')['rows']};modes=[];bounds=[];rawflags=[]
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifestpath.read_bytes())==selected['manifestSHA256'];refs.append(manifestpath)
    native=set();suppressed=set()
    for url in read(manifestpath)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;refs.append(path)
        for m in read(path)['models']:native.add(m['uid']);suppressed.update(m.get('suppressesBuildingUids',[]))
    for row in selected['rows']:
        uid=row['uid'];g=geometry[uid];attr=attributes[uid];support=basic[uid];assert support['basicIsCurrentFinalSupport']and support['supportUid']not in native|suppressed
        assert row['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256']==support['sourceSHA256']
        ctx=take(a.continuous,base/a.continuous/(uid.split('/')[1]+'.json.gz'));ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3);index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);literal=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1,3)
        assert np.array_equal(literal[index],np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)])
        asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(raw);original=literal.copy();original[index.ravel()]=tri.reshape(-1,3);assert np.array_equal(original[index],tri)
        positions={'original':original,'literal':literal,'leftF32':np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3),'balancedF32':np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3)};payload=[]
        for mode,pos in positions.items():
            proof=finite_bound(pos,ground);bounds.append(dict(uid=uid,mode=mode,sourceSHA256=row['sourceSHA256'],sourceWorldTrianglesSHA256=digest(pos[index].astype('<f8').tobytes()),completeGroundSHA256=digest(ground.astype('<f8').tobytes()),**proof));payload.append(dict(mode=mode,geometry=dict(position=pos.reshape(-1).tolist(),index=index.reshape(-1).tolist())))
        rawflags.append(dict(uid=uid,rawContinuousAffectedFaces=ctx['continuousAffectedFaces'],rawUncoveredProjectionFaces=ctx['wholeSourceUncoveredFaces'],rawMinimums=[ctx['faces'][i]['minimum']['minimumGapM']for i in ctx['continuousAffectedFaces']],rawRejectionsUnchanged=True))
        modes.append(dict(uid=uid,supportUid=support['supportUid'],sourceSHA256=row['sourceSHA256'],supportGeometry=support['supportGeometry'],modes=payload))
    save(out/'mode-inputs.json.gz',dict(rows=modes,evidenceRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in dict.fromkeys(refs)]));save(out/'finite-clearance.json',bounds);save(out/'raw-continuous-flags.json',rawflags)
    tool=HERE/'original_four_world_current_basic_support_v1_20261023.mjs'
    with(out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(out.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    report=read(out/'mode-checks.json.gz');assert len(report['rows'])==4*len(selected['rows'])
    for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    result=dict(rawCanonicalContactPassed={uid:r['canonicalContactPassed']for uid,r in basic.items()},uids=[r['uid']for r in selected['rows']],sources=len(selected['rows']),coordinateModes=4,wholeSourceFiniteClearancePassed=all(r['ordinaryClearanceBoundProved']for r in bounds),allCanonicalBasicSupportModesPassed=all(r['proof']['passed']for r in report['rows']),rawContinuousFlagsRetained=rawflags,sourceGeometryChanges=0,installationApproved=False,publication=False,status='four-world-current-basic-support-and-finite-clearance-diagnostics',qualification='All original finite source/ground vertices give exact rational global clearance lower bounds; no XZ/source-plane inversion or -.5m threshold change. Original/literal/twoFloat32 source representations separately pass or fail canonical contact against unchanged current basic support geometry. Raw floating continuous negatives are retained, never silently rewritten. No identity/collision/source-suppression/future-dependency/browser/publication approval.')
    save(out/'summary.json',result);refs.extend([tool,HERE/'finite_height_clearance_bound_v1_20261023.py',HERE/'exact_packed_world_geometry_20261009.py']);module('four_world_basic_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-basic-support-and-complete-finite-clearance',list(dict.fromkeys(refs)),result);print({k:result[k]for k in ['sources','wholeSourceFiniteClearancePassed','allCanonicalBasicSupportModesPassed']},flush=True)

if __name__=='__main__':main()
