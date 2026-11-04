"""Bounded interpretation of the unchanged official Fu Tor Loy original assembly."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def main():
 batch='government-xl-fu-tor-loy-physical-review-v1-20261023';out=BASE/batch;assert not out.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 cap='government-xl-fu-tor-loy-five-originals-current-v1-20261023-runtime';selection=take(cap,BASE/cap/'selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};runtime=take(cap,HERE/'local'/cap/'runtime-geometry.json.gz');geometry={r['uid']:r for r in runtime['rows']}
 attrs='government-xl-fu-tor-loy-five-originals-attributes-v1-20261023';attributes=take(attrs,BASE/attrs/'attributes.json.gz');assert attributes['startEndAllInputsVerified'];attributes={r['uid']:r for r in attributes['rows']}
 n='government-xl-fu-tor-loy-assembly-identity-review-v1-20261023';identity=take(n,BASE/n/'review.json');assert identity['identityOnlyApproved'] and identity['sourceSHA256ByUid']==sources
 n='government-xl-fu-tor-loy-four-world-path-readback-v1-20261023';paths=take(n,BASE/n/'summary.json');assert paths['verifiedWitnessPaths']==1308 and len(paths['rows'])==16 and all(r['maximumResidualM']<=.001 and r['degeneratePathFaces']==0 for r in paths['rows'])
 n='government-xl-fu-tor-loy-secondary-original-contacts-v1-20261023';parts=take(n,BASE/n/'summary.json');assert len(parts['rows'])==4
 n='government-xl-fu-tor-loy-detached-context-v2-20261023';detached=take(n,BASE/n/'summary.json');assert len(detached['rows'])==2
 assert detached['rows'][0]['minimumDistanceM']<.049 and detached['rows'][1]['minimumDistanceM']==0
 images=[]
 for n,f in [('government-xl-fu-tor-loy-detached-context-v2-20261023','231442:0.png'),('government-xl-fu-tor-loy-detached-context-v2-20261023','232818:0.png'),('government-xl-fu-tor-loy-five-originals-context-plots-v3-20261023','complete-original-assembly.png')]:
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  p=BASE/n/f;assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 pre='government-xl-fu-tor-loy-prephysical-v1-20261023';receipt,_=authenticate(BASE/pre);refs.append(BASE/pre/'result.json');assert len(receipt['completed'])==7
 # Entire tower mesh is above an inclusive upper bound of every terrain facet
 # whose XZ AABB can intersect it, stronger than point-sampled clearance.
 clearances=[]
 for number in ['231442','232818','233770','233775']:
  uid='landsd/'+number+':0';n=f'government-xl-fu-tor-loy-{number}-four-world-foundations-v1-20261023';f=take(n,BASE/n/'summary.json');assert len(f['rows'])==4 and all(r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 and r['completeTerrainTriangles']==r['triangles']for r in f['rows'])
  ground=np.asarray(geometry[uid]['drawnGroundGeometry']).reshape(-1,3,3);g=attributes[uid]
  for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
   t=np.asarray(g[field],dtype='<f8').reshape(-1,3)[np.asarray(g['completeOriginalIndex']).reshape(-1,3)]
   lo,hi=t.min((0,1)),t.max((0,1));mask=np.all(ground.max(1)[:,[0,2]]>=lo[[0,2]],axis=1)&np.all(ground.min(1)[:,[0,2]]<=hi[[0,2]],axis=1);assert mask.any()
   gap=float(lo[1]-ground[mask,:,1].max());assert gap>0;clearances.append(dict(uid=uid,mode=mode,minimumSourceY=float(lo[1]),completeTerrainAABBUpperY=float(ground[mask,:,1].max()),conservativeWholeMeshClearanceM=gap))
 patch='government-xl-fu-tor-loy-five-source-terrain-v1-20261023';terrain,_=authenticate(BASE/patch);refs.append(BASE/patch/'result.json');candidate=ROOT/terrain['candidate']['path'];assert digest(candidate.read_bytes())==terrain['candidate']['sha256'];refs.append(candidate)
 n='government-xl-fu-tor-loy-five-originals-current-v1-20261023-neighbours';neighbours=take(n,BASE/n/'summary.json');assert not neighbours['basicFlags'];failed=[r for r in neighbours['nativeRows']if not r['passed']];assert len(failed)==1 and failed[0]['uid']=='landsd/177605:0'
 n='government-xl-fu-tor-loy-hoi-yu-unchanged-context-v1-20261023';unchanged,_=authenticate(BASE/n);refs.append(BASE/n/'result.json');assert unchanged['proposalTerrainNonRegressionProved'] and not unchanged['rawSupportPolicyPassed'] and not unchanged['existingNativeReaccepted']
 review=dict(uids=sorted(sources),reviewer='Codex ROOT',sourceSHA256ByUid=sources,sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,completeNeighbourInterpretationAccepted=True,exactTerrainReplacement=terrain['candidate']['replaces'],retainedNativeRegression=dict(requiredNativeUids=neighbours['requiredNativeUids'],rawNativeFailures=[r['uid']for r in failed],unchangedContextJob=unchanged['jobId']),imagesActuallyViewed=images,continuousTowerTerrainUpperBounds=clearances,rawCanonicalFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,publicationApproved=False,basis='Accept only these five exact original government meshes as the complete official K44/80 podium/four-tower visual assembly at unchanged 1x source placement. Mall root passes the seven completed original/renderer foundation, continuous coverage and strict-rim phases. Every tower strict-contact sample is accounted by unchanged strict contacts or independently verified finite original-facet paths to finite positive-dimensional podium contacts in all four coordinate modes. Raw canonical interface and synthetic highest-podium-envelope negatives remain false; those envelopes are not actual terrain. Whole tower meshes clear actual terrain. All secondary faces remain in source: the 14-face Fu Wong rooftop piece is disjoint by 0.048198068m, accepted as an original roof detail without structural attachment credit; Fu Sun 22-face roof and long thin face/Fu Tong 14-face source attachment have finite surface contacts. Fu Sun tiny single facade triangle has point contact only, not a support root. Fu Lai degenerate single face remains preserved with no area/support credit. No model component is moved, capped, repaired, removed or used as an independent new support root. This records source visual assembly applicability, not structural engineering certification. Of 48 current native neighbours, 47 pass; Hoi Yu retains its existing raw support negative but both complete four-world native/support terrain face multisets and original asset hashes are exactly unchanged, proving no proposal regression without reaccepting the legacy model. No broad coverage, support or burial thresholds change.',scope='Private staged browser readiness only. Desktop/mobile source appearance, picking/collision, joint activation, failure recovery, runtime budgets, guarded publication/live and independent full521 readback remain required.')
 save(out/'ROOT-PHYSICAL-REVIEW.json',review)
 module('fu_tor_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-unchanged-five-source-physical-interpretation',refs,dict(uids=sorted(sources),sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,completeNeighbourInterpretationAccepted=True,sourceGeometryChanges=0,installationApproved=False));print('Exact original assembly ready for private staged browser checks',flush=True)
if __name__=='__main__':main()
