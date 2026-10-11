"""DRAFT source-only attribution of saved complete current finite failures, no rerun/waiver.
Literal exact source plane/winding is geometry, not foundation intent or architecture.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import json,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,cross,sub
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-mongkok-stadium-complete-original-far-extent-body-attribution-v1-20261011';FINITE=B/'government-xl-mongkok-stadium240332-complete-current-finite-ground-diagnostic-v1-20261011';DOC=B/'government-xl-mongkok-stadium240332-buried-original-body-plane-attribution-v1-20261011';CAP=B/'government-xl-mongkok-stadium240332-complete-current-ground-capture-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def profile(i,t,body):
 a,b,c=rational_face(t);n=cross(sub(b,a),sub(c,a));kind='zero'if not any(n)else'vertical'if n[1]==0 else'horizontal-up'if n[0]==n[2]==0 and n[1]>0 else'horizontal-down'if n[0]==n[2]==0 else'inclined-up'if n[1]>0 else'inclined-down'
 return dict(originalFace=i,genuineOriginalBody=body,exactNormal=[str(v)for v in n],literalPlaneClass=kind,minimumY=float(t[:,1].min()),maximumY=float(t[:,1].max()),originalTriangle=t.tolist(),architecturalFunctionUnqualified=True,foundationIntentUnqualified=True)
def main():
 assert not DOC.exists();refs=[]
 for folder in [OLD,FINITE,CAP]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
  refs.append(ref(folder/'result.json'))
 o=read(OLD/'diagnostic.json.gz');d=read(FINITE/'diagnostic.json.gz');asset=ROOT/o['source']['path'];assert ref(asset)==o['source'];world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(15456,3,3)and digest(world.tobytes())==o['completeOriginalWorldSHA256'];bodies=o['completeOriginalNonzeroBodyCensus']['sharedEdgeConnectedComponents'];labels={i:k for k,fs in enumerate(bodies)for i in fs};zeros=set(o['completeOriginalNonzeroBodyCensus']['exactNonrenderingOriginalFaces']);assert len(bodies)==14 and len(zeros)==15 and set(labels)|zeros==set(range(15456));profiles=[profile(i,t,labels.get(i))for i,t in enumerate(world)];far={r['originalFace']for r in o['all62OriginalFarFaceAttributions']};assert len(far)==62
 bindings=d['allFourStreamBindings'];assert set(bindings)=={'original','literal','explicitLeftF32','explicitBalancedF32'} and all(x['completeFaces']==15456 and x['proofTupleSHA256']in d['allDistinctWholeSourceFiniteProofs']for x in bindings.values());streams=[]
 for name,bind in bindings.items():
  proof=d['allDistinctWholeSourceFiniteProofs'][bind['proofTupleSHA256']];assert proof['completeFacetsAccounted']==15456;rows=proof['allWholeOriginalFacetProofs'];assert [r['face']for r in rows]==list(range(15456));failed=proof['ordinaryFailingSourceFaces'];assert failed==[r['face']for r in rows if not r['ordinaryFiniteProved']];groups=[]
  for k,fs in enumerate(bodies):
   ids=[i for i in fs if i in set(failed)];counts=Counter(profiles[i]['literalPlaneClass']for i in ids);groups.append(dict(originalBody=k,completeOriginalBodyFaces=fs,wholeBodyYRange=[float(world[fs,:,1].min()),float(world[fs,:,1].max())],ordinaryFailingOriginalFaces=ids,originalLiteralPlaneCounts=dict(counts),failedOriginalYRange=[min(profiles[i]['minimumY']for i in ids),max(profiles[i]['maximumY']for i in ids)]if ids else None,farOriginalFailingFaces=sorted(far&set(ids)),ordinaryFailingSavedProofs=[dict(originalFace=i,exactLowerM=rows[i]['exactLowerM'],completeProjectionCovered=rows[i]['completeProjectionCovered'],originalGeometryPlaneProfile=profiles[i])for i in ids],originalPlaneClassificationNotF32Reclassification=True))
  streams.append(dict(stream=name,completeBinding=bind,completeBodyGroups=groups,ordinaryFailures=len(failed),coverageFailures=len(proof['coverageFailingSourceFaces']),zeroFailingFaces=sorted(zeros&set(failed))))
 refs.extend(ref(p)for p in [Path(__file__),asset,OLD/'diagnostic.json.gz',FINITE/'diagnostic.json.gz',CAP/'capture-scope.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py']);assert all(ref(ROOT/r['path'])==r for r in refs)
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/240332:0',source=o['source'],completeOriginalWorldSHA256=o['completeOriginalWorldSHA256'],completeOriginalFaces=15456,genuineOriginalBodies=14,zeroOriginalFaces=sorted(zeros),all15456OriginalLiteralPlaneProfiles=profiles,allFourSavedFiniteFailureBodyAttributions=streams,currentFiniteProofRecomputed=False,geometryChanges=0,sourceOnly=True,currentAcceptance=False,installationApproved=False,foundationIntentInferred=False,gradeRootProved=False,clearanceFailuresWaived=False,qualification='Exact original planes/winding/Y/body attribution of saved full four-stream finite failures only. Tiny source plane tilts remain literal inclined; horizontal/upward winding alone does not prove visible surface, load function or intended foundations. Original plane classes are explicitly not reclassified F32 normals. Saved finite clearance failures and ordinary -.5 threshold remain unchanged. Genuine exposed grade interfaces/whole exposed source edges/strict clear caps and source-specific architectural roles require separate complete proofs; no body or failed face is accepted.',evidenceRefs=refs));print(json.dumps(dict(streams=[dict(stream=r['stream'],failures=r['ordinaryFailures'],bodyFailures={g['originalBody']:len(g['ordinaryFailingOriginalFaces'])for g in r['completeBodyGroups']if g['ordinaryFailingOriginalFaces']})for r in streams],currentAcceptance=False)))
if __name__=='__main__':main()
