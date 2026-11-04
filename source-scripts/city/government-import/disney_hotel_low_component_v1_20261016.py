"""Complete authored component context for the actual low-rim failures."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-disney-hotel-low-component-v1-20261016';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-disney-hotel-current-contacts-v1-20261016'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for ref in r['evidenceRefs']:
  p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];refs.append(p)
 path=HERE/'local/government-xl-disney-hotel-whole-neighbour-ground-v2-20261016/runtime-geometry.json.gz';g=read(path)['rows'][0];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 contact=read(PRIOR/'contacts.json.gz');bad=[f for f in contact['failures'] if f['reason']=='low-rim-gap'];ids={i for f in bad for i in f['sourceFaces']}
 helper=module('hotel_low_component',HERE/'xl-final-script-pass.py');parts=helper.connected_components(t,np.ones(len(t),dtype=bool));selected=[p for p in parts if ids.intersection(p.tolist())];assert len(selected)==1
 part=selected[0];a=t[part];projection=shapely.union_all([shapely.MultiPoint(face[:,[0,2]]).convex_hull for face in a]);inputs=BASE/'government-xl-disney-hotel-whole-neighbour-ground-v2-20261016/neighbour-inputs.json.gz';near=[]
 for row in read(inputs)['rows']:
  b=row['building'];poly=shapely.Polygon(b['rings'][0],b['rings'][1:]);distance=poly.distance(projection)
  if distance<=15:near.append(dict(uid=b['uid'],name=b.get('name'),parent=b.get('parent'),distanceM=distance,overlapM2=poly.intersection(projection).area,building=b))
 summary=dict(totalSourceFaces=len(t),componentCount=len(parts),selectedComponentFaces=len(part),sourceFaceIds=sorted(part.tolist()),bounds=[a.min(axis=(0,1)).tolist(),a.max(axis=(0,1)).tolist()],lowRimFailureSamples=len(bad),nearbyForms=[dict(uid=b['uid'],distanceM=b['distanceM'],overlapM2=b['overlapM2'])for b in near],topology='Existing connected_components uses vertices rounded to four decimal places; context only, not contact acceptance.',fullAcceptance=False)
 DOC.mkdir();save(DOC/'summary.json',summary);save(DOC/'source-context.json.gz',dict(summary=summary,triangles=a.tolist(),faceIds=part.tolist(),failures=bad,nearbyForms=near))
 refs += [path,inputs,PRIOR/'contacts.json.gz',HERE/'xl-final-script-pass.py'];result=module('hotel_component_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-hotel-low-rim-component-context-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/236354:0'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],componentFaces=len(part),nearby=summary['nearbyForms']),flush=True)
if __name__=='__main__':main()
