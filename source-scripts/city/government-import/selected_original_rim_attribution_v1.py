"""Attribute raw terrain contact warnings to exact original incident faces."""
import argparse,numpy as np,shapely
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from original_wall_rim_accounting_20261009 import original_samples
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--batch',required=True);ap.add_argument('--runtime',required=True);a=ap.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch;base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists();prior=base/a.runtime;r,pins=authenticate(prior);gp=HERE/'local'/a.runtime/'runtime-geometry.json.gz';mp=prior/'metrics.json'
 for p in [gp,mp]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 final=module('rim_attribution_ground',HERE/'xl-final-script-pass.py');rows=[]
 for g in read(gp)['rows']:
  position=np.asarray(g['position']).reshape(-1,3);index=np.asarray(g['index']).reshape(-1,3);bottom=float(position.min(0)[1]);records=original_samples(position,index,bottom);metric=next(m for m in read(mp)['rows']if m['uid']==g['uid']);assert len(records)==metric['checks'];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;points=np.asarray([v['point']for v in records]);heights=final.s.context.shared.samples(points[:,[0,2]],ground[valid],shapely.STRtree(polygons[valid]));gaps=points[:,1]-heights;assert np.isfinite(gaps).all();low=points[:,1]<=bottom+.35
  assert int(low.sum())==metric['lowRimChecks'];assert max(abs(float(gaps.min())-metric['minSurfaceGap']),abs(float(gaps[low].min())-metric['minLowGap']),abs(float(gaps[low].max())-metric['maxLowGap']))<1e-9
  selected=[]
  for i in np.flatnonzero(low&((gaps<-.5)|(gaps>1))):selected.append(dict(sampleIndex=int(i),**records[i],ground=float(heights[i]),gap=float(gaps[i]),reason='raised-rim'if gaps[i]>1 else'below-grade-rim'))
  tri=position[index];normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);ratio=np.divide(normal[:,1],length,out=np.zeros(len(tri)),where=length>0);ids=sorted({f for p in selected for f in p['originalIncidentFaces']});result=dict(uid=g['uid'],sourceSHA256=g['sourceSHA256'],wholeOriginalSamples=len(records),lowRimSamples=int(low.sum()),raisedRimSamples=sum(p['reason']=='raised-rim'for p in selected),belowGradeRimSamples=sum(p['reason']=='below-grade-rim'for p in selected),warnings=selected,incidentFaces=[dict(face=i,normalYRatio=float(ratio[i]),vertices=tri[i].tolist())for i in ids],installationApproved=False);save(doc/(g['uid'].split('/')[1]+'.json.gz'),result);rows.append({k:v for k,v in result.items()if k not in ['warnings','incidentFaces']});print(rows[-1],flush=True)
 summary=dict(uids=r['uids'],rows=rows,installationApproved=False,sourceGeometryChanges=0,newlyInstalled=0);save(doc/'summary.json',summary);refs=[Path(__file__),prior/'result.json',gp,mp,HERE/'original_wall_rim_accounting_20261009.py',HERE/'xl-final-script-pass.py'];module('original_rim_attribution_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'original-complete-runtime-contact-warning-attribution',refs,summary)
if __name__=='__main__':main()
