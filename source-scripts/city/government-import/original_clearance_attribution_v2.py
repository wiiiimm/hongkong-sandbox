"""Attribute exact captured clearance failures to immutable source faces and ground.
Diagnostic only. Does not approve installation or change acceptance thresholds.
"""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','samples','runtime','ground','uid']:p.add_argument('--'+key,required=True)
 a=p.parse_args();out=BASE/a.batch;assert not out.exists();refs=[Path(__file__)];cached={}
 def take(batch,path):
  if batch not in cached:
   cached[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==cached[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 samples=take(a.samples,BASE/a.samples/'samples.json')
 runtime=take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')
 g=next(r for r in runtime['rows']if r['uid']==a.uid);assert g['sourceSHA256']==samples['sourceSHA256']
 groundpath=HERE/'local'/a.ground/'original-terrain.json.gz'
 if groundpath.exists():
  ground=np.asarray(take(a.ground,groundpath)['triangles'])
 else:
  summary=take(a.ground,BASE/a.ground/'summary.json')
  record=next(r for r in summary['rows']if r['uid']==a.uid)
  assert record['status']=='original-terrain-checked'and record['sourceSHA256']==g['sourceSHA256']
  decoder=module('attribution_original_terrain',HERE/'xl-second-pass.py');parts=[]
  for name in record['sourceTerrainPaths']:
   path=ROOT/name;metadata=take(a.ground,path)
   for buffer in metadata.get('buffers',[]):
    member=path.parent/buffer['uri'];assert digest(member.read_bytes())==cached[a.ground][str(member.relative_to(ROOT))];refs.append(member)
   parts.append(decoder.terrain_triangles(path))
  ground=np.concatenate(parts);refs.append(HERE/'xl-second-pass.py')
 polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;ground=ground[valid]
 points=np.asarray([r['position']for r in samples['rows']]);assert len(points)>0
 helper=module('clearance_attribution_sampler',HERE/'xl-final-script-pass.py')
 heights=helper.s.context.shared.samples(points[:,[0,2]],ground,shapely.STRtree(polygons[valid]));assert np.isfinite(heights).all()
 triangles=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 faces=[]
 for i in sorted({r['faceIndex']for r in samples['rows']}):
  f=triangles[i];normal=np.cross(f[1]-f[0],f[2]-f[0]);size=float(np.linalg.norm(normal))
  faces.append(dict(faceIndex=i,vertices=f.tolist(),normal=normal.tolist(),normalisedVertical=float(normal[1]/size)if size else None,samples=sum(r['faceIndex']==i for r in samples['rows'])))
 records=[dict(**r,originalTerrainHeight=float(h),originalTerrainGapM=float(r['position'][1]-h),renderedMinusOriginalGroundM=float(r['ground']-h))for r,h in zip(samples['rows'],heights)]
 summary=dict(uids=[a.uid],sourceSHA256=g['sourceSHA256'],checks=samples['checks'],failedSamples=len(records),failedFaces=len(faces),failedCentroids=sum(r['kind']=='centroid'for r in records),maximumAbsoluteRenderedOriginalGroundDeltaM=max(abs(r['renderedMinusOriginalGroundM'])for r in records),originalGroundGapRangeM=[min(r['originalTerrainGapM']for r in records),max(r['originalTerrainGapM']for r in records)],upwardFailedFaceCount=sum(r['normalisedVertical']is not None and r['normalisedVertical']>.25 for r in faces),installationApproved=False,physicalInterpretationAccepted=False,sourceGeometryChanges=0,rawFailuresPreserved=True)
 save(out/'context.json',dict(**summary,faces=faces,samples=records));refs.append(HERE/'xl-final-script-pass.py')
 module('original_clearance_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'original-source-clearance-attribution',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()
