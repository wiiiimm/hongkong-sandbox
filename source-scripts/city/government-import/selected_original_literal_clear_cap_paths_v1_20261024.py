"""Replay existing strict-clear cap paths on complete current literal source context.

Shared exact original edges only. No invented cross-component contacts, no source
edits and no implication that literal evidence proves other coordinate streams.
"""
import argparse,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_strict_clear_cap_wall_paths_20261009 import verify


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','continuous','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    source=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid)
    g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    ctx=take(a.continuous,base/a.continuous/(a.uid.split('/')[1]+'.json.gz'))
    assert source['sourceSHA256']==g['sourceSHA256']==ctx['sourceSHA256'];asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset)
    tri=np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
    assert digest(tri.tobytes())==ctx['sourceBinding']['decodedWorldTrianglesSHA256']
    assert digest(ground.tobytes())==ctx['sourceBinding']['drawnGroundSHA256'],'Context must bind complete drawn ground; filtered ground needs separate treatment'
    canonical=lambda x:digest(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
    binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeCurrentFacetContextsSHA256=canonical(ctx['faces']),exactOriginalContactListSHA256=canonical([]),currentDrawnGroundSHA256=digest(ground.tobytes()))
    proof=verify(tri,ctx['faces'],[],expected_binding=binding,current_binding=binding)
    result=dict(uids=[a.uid],sourceSHA256=source['sourceSHA256'],coordinateRepresentation='actual-literal-only',binding=binding,proof=proof,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,qualification='Existing exact shared-edge clear-cap path kernel replayed on every complete current literal source context and complete drawn ground. No extra contacts supplied. Source-role, exact residual numerical/coverage obligations, other coordinate representations, actual support/foreign/browser and publication remain independent. Failure does not imply corruption.')
    save(out/'summary.json',result);refs.extend([HERE/'original_strict_clear_cap_wall_paths_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py'])
    module('selected_literal_cap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'actual-literal-original-shared-edge-strict-clear-cap-paths',refs,result)
    print(dict(allAffectedHavePaths=proof['allAffectedHavePaths'],affected=len(proof['affectedOriginalWallFaces']),rawExposureFailures=proof['rawExposureFailures']),flush=True)

if __name__=='__main__':main()
