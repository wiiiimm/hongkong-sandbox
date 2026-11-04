"""Bounded original podium/ground interface review, preserving all raw crossings."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-verdant-podium-review-v1-20261018';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-wave-verdant-podium-tin-comparison-v1-20261018'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 rows=read(PRIOR/'summary.json')['rows'];assert len(rows)==8
 for x in rows:assert x['comparedFaces']==x['originalTinNegative']and x['missingOriginalCoverage']==0 and x['largestAbsoluteMinimumChangeM']<.001
 raw=read(BASE/'government-xl-wave-verdant-multicore-terrain-v4-20261017/metrics.json')['rows'];raw={x['uid']:x for x in raw};found=read(BASE/'government-xl-wave-verdant-assembly-four-worlds-v1-20261017/summary.json')['rows'];decisions=[]
 for uid in ['landsd/301560:0','landsd/304885:0']:
  m=raw[uid];f=[x for x in found if x['uid']==uid];assert len(f)==4 and all(x['strictFoundationAccepted']and x['buried']==0 and x['upwardBuried']==0 for x in f)
  assert m['sourcePreserved']and m['missingTerrain']==0 and m['lowRimChecks']>0 and m['minLowGap']<=.1 and m['maxLowGap']<=1 and m['maxSamplerDelta']<=.004
  contexts=[read(BASE/'government-xl-wave-verdant-podium-grade-context-v3-20261018'/(uid.split('/')[1]+'-'+mode+'.json.gz')) for mode in ['original','literal','left','balanced']]
  assert all(x['sourceSHA256']==m['sourceSHA256']and not x['uncoveredFaces']for x in contexts)
  decisions.append(dict(uid=uid,sourceSHA256=m['sourceSHA256'],rawMinSurfaceGapM=m['minSurfaceGap'],rawMinLowGapM=m['minLowGap'],rawMaxLowGapM=m['maxLowGap'],negativeFacesByMode={x['mode']:x['continuousNegativeFaceIds']for x in contexts},negativeUpwardFacesByMode={x['mode']:x['negativeUpwardFaceIds']for x in contexts},noExposedWitnessFacesByMode={x['mode']:x['negativeWithoutExposedWitness']for x in contexts},originalTinComparison=[x for x in rows if x['uid']==uid],sourceSpecificGroundInterfaceAccepted=True))
 images=[PRIOR/'podium-crossings-plan.png']+[BASE/'government-xl-wave-verdant-private-browser-v5-20261018'/('staged-landsd-'+u+'-0-1280-1500.png') for u in ['301560','304885']]
 refs.extend(images);ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 decision=dict(reviewer='Codex ROOT',rows=decisions,sourceSpecificGroundInterfaceAccepted=True,rawWarningsPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,fullAcceptance=False,installationApproved=False,inspectedImages=[ref(p)for p in images],reason='Retain these exact original podiums with their authenticated original ground interfaces. Every final-terrain adverse face also crosses the government original TIN in all four coordinate representations, with minimum-gap differences below0.001m. The final patch does not create a new set of adverse source faces. Complete existing foundation checks pass with zero faces whose vertices and centroid are all deeper than the existing0.5m burial limit. Low-band upper contact and rendered/sampled terrain agree within existing limits. The source-plan diagram locates the upward crossings in lower podium plates/edges; inspected staged day views preserve the visible podium terraces and external walls in their original pose. No original surface is deleted, filled, translated or simplified to force a generic all-vertices-above-ground rule.',limitations=['This accepts authored original ground intersections for these exact source/terrain tuples only; it does not change the generic0.5m check.','Original source consistency alone does not prove architectural intent. No specific room or engineering function is assigned to hidden faces.','Five Wave and one Verdant face have no exposed witness in the diagnostic; those facts remain explicitly recorded. Zero fully buried under the existing sampled policy does not mean every point of every face is visible.','Images contain ordinary occlusion and do not certify visibility of every face.','Full assembly/current-input qualification, guarded publication and live ledger verification remain required.'])
 save(DOC/'ROOT-PODIUM-REVIEW.json',decision);out=module('wave_podium_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-exact-original-podium-ground-interface-review-v1',list(set(refs)),dict(uids=[x['uid']for x in decisions],sourceSpecificGroundInterfaceAccepted=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
