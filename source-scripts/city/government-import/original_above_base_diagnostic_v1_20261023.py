"""Diagnostic original-facet partition and source-terrain sampling; no acceptance."""
from pathlib import Path
import json
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_grade_partition_v1 import partition_triangle
BASE=ROOT/'docs/astra-city/government-import';N='government-xl-basement-burial-context-v1-20261023';T='government-xl-all-200-original-terrain-batch-v2-20261022';M='government-xl-remaining-official-structure-context-v1-20261022';B='government-xl-original-above-base-diagnostic-v1-20261023';D=BASE/B;LOCAL=HERE/'local'/B
assert not D.exists()and not LOCAL.exists();refs=[Path(__file__),HERE/'original_grade_partition_v1.py',HERE/'exact_packed_world_geometry_20261009.py'];pins={}
for n in [N,T,M]:
 _,pins[n]=authenticate(BASE/n);refs.append(BASE/n/'result.json')
def take(n,p):
 assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
context=take(N,BASE/N/'summary.json');forms={r['uid']:r['currentForm']for r in take(M,BASE/M/'summary.json')['rows']if r.get('uid')};assets={sha:ROOT/p for p,sha in pins[T].items()if p.endswith('.glb.gz')}
world=module('above_base_source_terrain',HERE/'xl-second-pass.py');world.LOCAL=LOCAL
final=module('above_base_foundation',HERE/'xl-final-script-pass.py');reports=[]
for r in context['rows']:
 oldContext=r['originalTINBurialContext']
 if not oldContext or not oldContext['allOriginalTINBurialComponentsBelowRecordedBase']:continue
 uid=r['uid'];base=r['officialBaseHeightHKPD'];asset=assets[r['sourceSHA256']];blob=asset.read_bytes();assert digest(blob)==r['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(blob);assert digest(tri.astype('<f8').tobytes())==r['sourceWorldSHA256']
 above=[];below=[];partitions=[]
 for face_id,face in enumerate(tri):
  high,low=partition_triangle(face,base);above.extend(high);below.extend(low)
  if len(high)!=1 or low:partitions.append(dict(originalFace=face_id,abovePieces=[[[str(v)for v in p]for p in t]for t in high],belowPieces=[[[str(v)for v in p]for p in t]for t in low]))
 high=np.asarray(above,dtype='<f8');low=np.asarray(below,dtype='<f8');assert len(high)and len(low)
 save(LOCAL/(uid.split('/')[1]+'-analysis-partitions.json.gz'),dict(sourceSHA256=r['sourceSHA256'],sourceWorldSHA256=r['sourceWorldSHA256'],recordedBaseHeight=base,modifiedAnalysisFacetsOnly=partitions,sourceGeometryChanged=False,qualification='Exact rational original-facet portions for analysis only; source asset and runtime geometry remain untouched. No grade-plane cap is generated. Every original facet conserves its exact oriented area vector.'))
 parts=[];lo=tri.min((0,1));hi=tri.max((0,1))
 for name in oldContext['sourceTerrainPaths']:
  p=ROOT/name;data=take(T,p)
  for buffer in data.get('buffers',[]):
   uri=buffer.get('uri')
   if uri and not uri.startswith('data:'):
    q=p.parent/uri;assert digest(q.read_bytes())==pins[T][str(q.relative_to(ROOT))];refs.append(q)
  g=world.terrain_triangles(p);parts.append(g[(g[:,:,0].max(1)>=lo[0]-10)&(g[:,:,0].min(1)<=hi[0]+10)&(g[:,:,2].max(1)>=lo[2]-10)&(g[:,:,2].min(1)<=hi[2]+10)])
 ground=np.concatenate(parts);form=forms[uid];assert form['baseHeightHKPD']==base;poly=Polygon(form['rings'][0],form['rings'][1:]);raw=final.foundation_context(tri,ground,poly);old=take(T,BASE/T/(uid.split('/')[1]+'.json'))['originalTerrainFoundation']
 for k in ['triangles','completeTerrainTriangles','fullyBuriedTriangles','fullyBuriedUpwardTriangles']:assert raw[k]==old[k]
 report=dict(uid=uid,sourceSHA256=r['sourceSHA256'],sourceWorldSHA256=r['sourceWorldSHA256'],recordedBaseHeight=base,originalSourceFaces=len(tri),aboveGradeAnalysisPieces=len(high),belowGradeAnalysisPieces=len(low),rawWholeOriginalFoundation=raw,aboveBaseSampledFoundation=final.foundation_context(high,ground,poly),belowBaseSampledFoundation=final.foundation_context(low,ground,poly),sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False)
 reports.append(report);save(D/(uid.split('/')[1]+'.json'),report);print(dict(uid=uid,aboveBaseBuried=report['aboveBaseSampledFoundation']['fullyBuriedTriangles'],aboveBaseMinimumGap=report['aboveBaseSampledFoundation']['minimumGapM'],rawBuried=raw['fullyBuriedTriangles']),flush=True)
summary=dict(uids=[r['uid']for r in reports],rows=reports,sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,newlyInstalled=0,qualification='Diagnostic separation of exact immutable original facets at fresh official recorded base. Above-base foundation_context uses its existing four samples per derived analysis triangle; this is NOT a continuous, current-scene, support or four-world acceptance proof. Original raw failures retained verbatim; no original geometry edits, renderer filtering, basement role inference or acceptance exemption. All existing gates remain required.')
save(D/'summary.json',summary);refs.extend([HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',*[p for p in LOCAL.rglob('*')if p.is_file()]])
module('above_base_diagnostic_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'original-source-above-base-diagnostic',refs,summary)
