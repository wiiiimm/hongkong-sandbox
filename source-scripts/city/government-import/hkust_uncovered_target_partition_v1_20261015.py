"""Partition HKUST's unresolved provider target; original-source diagnostic only."""
from pathlib import Path
import hashlib, json
import numpy as np
from shapely.geometry import Polygon, mapping
from shapely import union_all
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
PACKET=BASE/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014'
PRIOR=BASE/'government-xl-hkust-two-original-source-context-receipt-v1-20261014/result.json'
BATCH='government-xl-hkust-uncovered-target-partition-v1-20261015';DOC=BASE/BATCH

def main():
 assert not DOC.exists()
 old=read(PRIOR)
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(old['jobId'],)).fetchone()==('complete',old)
 # Historical receipt remains historical; only exact source arrays and unchanged target tile are reused.
 reportp=PACKET/'two-original-scope-interface-output-v1/result.json';report=read(reportp)
 assert digest(reportp.read_bytes())==old['completedContextResultSHA256']
 formsdoc=read(PACKET/'current-six-forms-verbatim.json');tile=ROOT/formsdoc['currentTilePath'];assert digest(tile.read_bytes())==formsdoc['currentTileSHA256']
 paths=[Path(__file__),PRIOR,reportp,tile,PACKET/'current-six-forms-verbatim.json'];shapes=[]
 for ref in report['arrayRefs']:
  p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];a=read(p);s=a['sourceTuple'];asset=ROOT/s['originalAssetPath'];assert digest(asset.read_bytes())==s['sourceSHA256'];tri=np.asarray(a['completeOrderedOriginalTriangles'],dtype='<f8');assert hashlib.sha256(tri.tobytes()).hexdigest()==a['originalWorldSHA256'];assert len(tri)==s['originalFaces']
  polygons=[Polygon(t[:,[0,2]]) for t in tri];shapes.append(union_all([p for p in polygons if p.area>0]));paths += [p,asset]
 scope=report['completeCurrentTileRawRingNomination'];forms=[x['form'] for x in scope['nominated']+scope['strictDisjointExclusions']];assert len(forms)==scope['completeTileForms']==1383
 byuid={f['uid']:f for f in forms};uids=report['uids'];poly=lambda f:Polygon(f['rings'][0],f['rings'][1:])
 target=union_all([poly(byuid[u]) for u in uids]);source=union_all(shapes);missing=target.difference(source)
 prior=next(x for x in report['projectionScope'] if x['label']=='two-originals-against-expanded-target');assert abs(source.intersection(target).area/target.area-prior['targetCoverage'])<1e-12
 rows=[];pieces=[]
 for f in forms:
  if f['uid'] in uids:continue
  intersection=missing.intersection(poly(f))
  if intersection.area>0:
   rows.append({'uid':f['uid'],'CSUID':f.get('buildingCSUID'),'kind':f.get('kind'),'structureType':f.get('structureType'),'name':f.get('name'),'missingTargetOverlapM2':intersection.area,'originalForm':f});pieces.append(intersection)
 covered=union_all(pieces);residual=missing.difference(covered)
 DOC.mkdir();out={'uids':uids,'targetAreaM2':target.area,'uncoveredTargetAreaM2':missing.area,'overlaps':sorted(rows,key=lambda x:-x['missingTargetOverlapM2']),'distinctOtherFormCoveredM2':covered.area,'unassignedMissingAreaM2':residual.area,'allTileFormsExamined':len(forms),'sourceGeometryChanges':0,'identityAccepted':False,'physicalAccepted':False,'qualification':'Spatial attribution only. Other-form overlap is not permission to suppress, merge identities, or waive support. All historical negatives remain applicable.'}
 save(DOC/'partition.json',out);save(DOC/'regions.geojson',{'type':'FeatureCollection','features':[{'type':'Feature','properties':{'role':name},'geometry':mapping(g)} for name,g in [('target',target),('originals',source),('missing',missing),('unassigned',residual)]]})
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,ax=plt.subplots(figsize=(10,12))
 def draw(g,color,label):
  polys=[g] if g.geom_type=='Polygon' else list(getattr(g,'geoms',[]));first=True
  for p in polys:
   if p.geom_type!='Polygon':continue
   x,z=p.exterior.xy;ax.plot(x,z,color=color,lw=1,label=label if first else None);first=False
 draw(target,'black','Provider target');draw(source,'#238b45','Two unchanged originals');draw(missing,'#d7301f','Uncovered target')
 for row in rows:
  p=poly(row['originalForm']);draw(p,'#756bb1',None);c=p.representative_point();ax.text(c.x,c.y,row['uid'].split('/')[1],fontsize=7)
 ax.set_aspect('equal');ax.invert_yaxis();ax.legend();ax.set_title('HKUST complete target gap partition — diagnostic only');ax.set_xlabel('Viewer X (m)');ax.set_ylabel('Viewer Z (m)');fig.tight_layout();fig.savefig(DOC/'partition.png',dpi=160);plt.close(fig)
 freezer=module('hkust_partition_receipt',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
 freezer.freeze(BATCH,'hkust-complete-provider-gap-partition-v1',paths,{**out,'historicalReceiptJobId':old['jobId'],'currentHeldReason':'paired-source-target-gap-and-original-support-unresolved','nextStep':'Inspect unassigned target region and provider height/part records for missing original components; no blanket tower/podium identity union or support waiver.'})
 print(json.dumps({k:v for k,v in out.items() if k!='overlaps'}),flush=True)
if __name__=='__main__':main()
