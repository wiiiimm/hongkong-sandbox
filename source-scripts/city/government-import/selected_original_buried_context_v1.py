"""Freeze exact remaining buried faces from a current private runtime capture."""
import argparse,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate,face_diagnostics
from primrose_compound_foundation_v2_20261015 import module
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--batch',required=True);ap.add_argument('--runtime',required=True);a=ap.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
 base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists();prior=base/a.runtime;r,pins=authenticate(prior);gp=HERE/'local'/a.runtime/'runtime-geometry.json.gz';assert digest(gp.read_bytes())==pins[str(gp.relative_to(ROOT))];data=read(gp);final=module('selected_buried_foundation',HERE/'xl-final-script-pass.py');rows=[]
 for g in data['rows']:
  tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);detail=face_diagnostics(final,tri,ground);old=next(v for v in r['rows']if v['uid']==g['uid']);assert len(detail['buriedFaces'])==old['fullyBuriedTriangles'];assert len(tri)-len(detail['uncoveredFaceIndices'])==old['completeTerrainTriangles'];row=dict(uid=g['uid'],sourceSHA256=g['sourceSHA256'],**detail,installationApproved=False);save(doc/(g['uid'].split('/')[1]+'.json'),row);rows.append(dict(uid=g['uid'],buriedFaces=len(detail['buriedFaces']),upwardBuriedFaces=sum(f['upward']for f in detail['buriedFaces']),faceIndices=[f['faceIndex']for f in detail['buriedFaces']]))
 result=dict(uids=r['uids'],rows=rows,installationApproved=False,sourceGeometryChanges=0,newlyInstalled=0);save(doc/'summary.json',result);refs=[Path(__file__),prior/'result.json',gp,HERE/'china_ferry_current_foundations_v1_20261020.py',HERE/'xl-final-script-pass.py'];module('selected_buried_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'current-private-original-buried-context',refs,result);print(rows)
if __name__=='__main__':main()
