"""Bind all four unchanged current roof bodies to standalone v3 opening guards."""
import json
import numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from complete_original_lower_opening_mounts_v3_20261011 import verify,binding
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-block6-current-four-opening-guards-v3-20261011';DOC=B/BATCH
P=B/'government-xl-parkview-block6-fresh-current-physical-capture-v1-20261011';G=B/'government-xl-parkview-block6-complete-original-support-paths-v1-20261011';V2=B/'government-xl-parkview-block6-current-four-stream-source-proofs-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();r=read(P/'selection.json.gz')['rows'][0];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];a=read(P/'actual-render-geometry.json.gz')['row'];index=np.asarray(a['completeOriginalIndex']).reshape(-1,3);graph=read(G/'diagnostic.json.gz');bodies=graph['completeSourceEdgeBodyFaces'];parents={int(k):v for k,v in graph['completeConditionalParents'].items()};hosts=sorted(f for i in parents for f in bodies[i]);assert len(hosts)==10953;assert graph['unreachedBodies']==[78,79,80,83]
 worlds=[decode_original_world_triangles(asset.read_bytes())]+[np.asarray(a[k]).reshape(-1,3)[index]for k in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']];names=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'];old=read(V2/'diagnostic.json.gz');rows=[]
 for name,t in zip(names,worlds):
  pin=digest(t.tobytes());previous=next(x for x in old['rows']if x['mode']==name);assert pin==previous['completeWorldSHA256'];same=next((x for x in rows if x['completeWorldSHA256']==pin),None)
  if same:rows.append({**same,'mode':name,'identicalImmutableSourceBodyHostProofsReusedFrom':same['mode']});continue
  proofs=[]
  for i in graph['unreachedBodies']:
   v=verify(t,bodies[i],hosts,expected_binding=binding(t,bodies[i],hosts));prior=next(x['proof']for x in previous['completeFourOpeningProofs']if x['originalBody']==i);assert json.loads(json.dumps(v['priorV2MountProofVerbatim']))==prior;assert v['completeLowerOpeningAssociated'];proofs.append(dict(originalBody=i,proof=v))
  rows.append(dict(mode=name,completeWorldSHA256=pin,completeFourOpeningProofs=proofs,allFourStandaloneV3GuardsPassed=True))
 refs=[ref(p)for p in [Path(__file__),asset,P/'actual-render-geometry.json.gz',P/'selection.json.gz',G/'diagnostic.json.gz',V2/'diagnostic.json.gz',HERE/'complete_original_lower_opening_mounts_v3_20261011.py',HERE/'test_complete_original_lower_opening_mounts_v3_20261011.py',HERE/'complete_original_lower_opening_mounts_v2_20261011.py',HERE/'test_complete_original_lower_opening_mounts_v2_20261011.py']]
 save(DOC/'diagnostic.json.gz',dict(uids=['landsd/255438:0'],rows=rows,completeOriginalFaces=11041,completeHostOriginalFaces=10953,allFourStreamsPass=True,priorV2ProofsUnchanged=True,exactIntersectionAbsencePreserved=True,structuralRootCredit=False,structuralBridgeCredit=False,closedSolidCertified=False,architecturalFunctionInferred=False,currentAcceptance=False,installationApproved=False,newlyInstalled=0,evidenceRefs=refs))
 print('Four original opening bodies pass standalone v3 in all four bound streams; v2 proofs preserved.')
if __name__=='__main__':main()
