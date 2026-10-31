"""Four-coordinate exact source face bindings, not a numeric waiver or installation."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from upton_wall_band_functional_context_v1_20261014 import face_descriptor
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-pacifica-wall-binding-v1-20261019';DOC=BASE/BATCH;ATTR=BASE/'government-xl-pacifica-actual-render-attributes-v1-20261019';REVIEW=BASE/'government-xl-pacifica-source-interpretation-v1-20261019';PAIR=BASE/'government-xl-pacifica-original-assembly-v1-20261019'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',HERE/'upton_wall_band_functional_context_v1_20261014.py']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [ATTR,REVIEW]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 decision=read(REVIEW/'ROOT-SOURCE-INTERPRETATION.json');assert all(r['sourceFunctionalInterpretationAccepted']and not r['installationApproved']for r in decision['rows']);ids={r['uid']:r['sourceFaceIds']for r in decision['rows']};sources={r['uid']:r for r in read(PAIR/'selection.json.gz')['rows']};bindings=[];descriptors=[]
 for row in read(ATTR/'attributes.json.gz')['rows']:
  uid=row['uid'];source=sources[uid];raw=(ROOT/source['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']==source['sourceSHA256'];ix=np.asarray(row['completeOriginalIndex'],dtype=np.int64).reshape(-1,3)
  worlds={'original':np.asarray(decode_original_world_triangles(raw),dtype='<f8')}
  for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(row[field],dtype='<f8').reshape(-1,3)[ix]
  assert all(len(w)==source['triangles']for w in worlds.values())
  for mode,w in worlds.items():
   assert np.isfinite(w).all();h=digest(w.astype('<f8').tobytes());bindings.append(dict(uid=uid,sourceSHA256=source['sourceSHA256'],buildingCSUID=source['candidate']['entry']['buildingCSUID'],mode=mode,wholeWorldSHA256=h,completeFaces=len(w)))
   if uid in ids:descriptors.append(dict(uid=uid,mode=mode,wholeWorldSHA256=h,faces=[face_descriptor(i,w[i].tolist())for i in ids[uid]],additionalBuriedFaceDescriptors=[face_descriptor(i,w[i].tolist())for i in ([3028,3029]if uid=='landsd/75351:0'else[])]))
 assert len(bindings)==20 and len(descriptors)==8
 save(DOC/'exact-source-face-bindings.json.gz',dict(bindings=bindings,descriptors=descriptors,ROOTSourceReview=dict(path=str((REVIEW/'ROOT-SOURCE-INTERPRETATION.json').relative_to(ROOT)),sha256=digest((REVIEW/'ROOT-SOURCE-INTERPRETATION.json').read_bytes())),allUnusedAttributesRetainedInCapture=True,raw30SupportFailuresRetained=True,sourceGeometryChanges=0,installationApproved=False))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('olympian_bindings_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-four-coordinate-reviewed-wall-face-bindings',list(dict.fromkeys(refs)),dict(uids=list(sources),sourceBindings=20,reviewedFacesPerMode=37,strictInterfacePassed=False,installationApproved=False))
if __name__=='__main__':main()
