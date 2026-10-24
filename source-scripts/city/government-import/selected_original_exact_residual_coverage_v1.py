"""Resolve floating residuals with exact rational coverage of the same drawn facets."""
import argparse,numpy as np,shapely
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_projection_coverage_v2_20261010 import exact_coverage
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','runtime','context']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch;base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists();rp=base/a.runtime;cp=base/a.context;r,rpins=authenticate(rp);_,cpins=authenticate(cp);gp=HERE/'local'/a.runtime/'runtime-geometry.json.gz';assert digest(gp.read_bytes())==rpins[str(gp.relative_to(ROOT))];refs=[Path(__file__),rp/'result.json',cp/'result.json',gp];rows=[]
 for g in read(gp)['rows']:
  contextpath=cp/(g['uid'].split('/')[1]+'.json.gz');assert digest(contextpath.read_bytes())==cpins[str(contextpath.relative_to(ROOT))];context=read(contextpath);refs.append(contextpath);tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3);polys=shapely.polygons(ground[:,:,[0,2]]);ground=ground[shapely.area(polys)>1e-10];assert digest(tri.tobytes())==context['sourceBinding']['decodedWorldTrianglesSHA256']and digest(ground.tobytes())==context['sourceBinding']['drawnGroundSHA256'];proofs=[]
  for c in context['faces']:
   if c['groundProjectionCovered']:continue
   i=c['sourceFace'];p=exact_coverage(tri[i],ground);proofs.append(dict(sourceFace=i,rawFloatingCoverageFalseRetained=True,**p));print(dict(uid=g['uid'],face=i,exactCovered=p['exactProjectionCovered']),flush=True)
  row=dict(uid=g['uid'],rawFloatingUncovered=len(proofs),exactCovered=sum(p['exactProjectionCovered']for p in proofs),stillUncoveredFaces=[p['sourceFace']for p in proofs if not p['exactProjectionCovered']],sourceSHA256=g['sourceSHA256'],sourceBinding=context['sourceBinding'],proofs=proofs,installationApproved=False);save(doc/(g['uid'].split('/')[1]+'.json.gz'),row);rows.append({k:v for k,v in row.items()if k not in ['proofs','sourceBinding']})
 summary=dict(uids=r['uids'],rows=rows,sourceGeometryChanges=0,installationApproved=False,newlyInstalled=0);save(doc/'summary.json',summary);refs.append(HERE/'exact_original_projection_coverage_v2_20261010.py');module('selected_exact_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-same-drawn-ground-residual-coverage',refs,summary)
if __name__=='__main__':main()
