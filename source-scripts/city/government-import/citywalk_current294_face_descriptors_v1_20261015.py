"""Exact source-face descriptors for all294 original sampler failures; no approval."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from upton_wall_band_functional_context_v1_20261014 import face_descriptor
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citywalk-current294-face-descriptors-v1-20261015';DOC=BASE/BATCH
SRC=BASE/'government-xl-citywalk-current294-incident-faces-v2-20261015';PRIOR=BASE/'government-xl-citywalk-saved294-source-layer-attribution-v1-20261014'
def main():
 assert not DOC.exists();packet=read(SRC/'incident-faces.json.gz');paths=[Path(__file__),SRC/'incident-faces.json.gz',HERE/'upton_wall_band_functional_context_v1_20261014.py',PRIOR/'result.json'];receipt=read(PRIOR/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 source=PRIOR/'complete-saved294-source-layer-attribution.json.gz';assert dict(path=str(source.relative_to(ROOT)),sha256=digest(source.read_bytes()))in receipt['evidenceRefs']
 for p,h in packet['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;paths.append(ROOT/p)
 census=read(BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v5-20261015/input.json.gz')
 for p,h in census['currentNativeViewerTileHashes'].items():assert digest((ROOT/p).read_bytes())==h;paths.append(ROOT/p)
 rows=[]
 for r in packet['rows']:
  assert not r['unmatchedPoints']and r['allPointsExactSamplerAttributed'];descriptors=[]
  for f in r['incidentFaces']:
   d=face_descriptor(f['faceIndex'],f['vertices']);v=np.asarray(f['vertices']);n=np.cross(v[1]-v[0],v[2]-v[0]);length=np.linalg.norm(n);d.update(normalY=float(n[1]/length)if length else None,sourceVertices=f['vertices'],heightSpan=float(v[:,1].max()-v[:,1].min()));descriptors.append(d)
  horizontal=[f['originalFaceID']for f in descriptors if f['heightSpan']==0];vertical=[f['originalFaceID']for f in descriptors if f['exactNormalYIsZero']and f['nondegenerate']];other=[f['originalFaceID']for f in descriptors if f['originalFaceID']not in set(horizontal+vertical)]
  rows.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],savedPoints=len(r['points']),completePointAttribution=r['points'],faces=descriptors,exactHorizontalFaceIDs=horizontal,exactVerticalFaceIDs=vertical,otherFaceIDs=other,sourceRoleApproved=False))
 assert sum(r['savedPoints']for r in rows)==294;DOC.mkdir();save(DOC/'descriptors.json.gz',dict(rows=rows,sourceGeometryChanges=0,all294ExactSamplerMembership=True,functionalInterpretationPending=True))
 summary=[dict(uid=r['uid'],points=r['savedPoints'],incidentFaces=len(r['faces']),horizontal=len(r['exactHorizontalFaceIDs']),vertical=len(r['exactVerticalFaceIDs']),other=len(r['otherFaceIDs']))for r in rows];save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False,nextStep='Review all461 exact source faces and their actual podium junctions; no blanket vertical-wall disposition. Preserve horizontal/other faces and original failed interface.'))
 module('citywalk294_descriptor_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current294-source-sampler-face-descriptors-v1',paths,dict(uids=['landsd/134332:0'],towerUIDs=[r['uid']for r in rows],summary=summary,fullAcceptance=False));print(summary,flush=True)
if __name__=='__main__':main()
