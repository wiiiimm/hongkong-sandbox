"""Unexecuted readonly saved-data context; no production sampler/guard replay."""
from pathlib import Path
import json,gzip,hashlib,sys
from fractions import Fraction as F
import polyu_nine_basic_saved_height_context_draft_v1_20261013 as m
R=Path(__file__).resolve().parents[3];B=R/'docs/astra-city/government-import';D=B/'government-xl-polyu-sports305582-authentic-local-private-terrain-draft-v1-20261013/nine-basic-saved-height-regression-context-draft-v1';RUN=B/'government-xl-polyu-sports305582-saved-private-candidate-runtime-only-v1-20261013';BUILD=B/'government-xl-polyu-sports305582-authentic-local-private-terrain-v2-20261013';FEAS=B/'government-xl-polyu-sports305582-authentic-terrain-feasibility-draft-v2-20261013/calculation-v1/feasibility.json.gz';CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7';NINE={'landsd/'+str(i)+':0'for i in [63758,72322,89540,258381,258681,258852,198620,305600,305626]}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def preflight():
 pins={r['path']:r['sha256']for r in read(D/'input-pins.json')['filePins']};pins[str((D/'input-pins.json').relative_to(R))]=sha(D/'input-pins.json');q=read(RUN/'result.json');assert q['jobId']=='ce2589c6c43d007f527d6bc78e51204abf4344a261fd41b0436dc1c6234d316f'
 for r in q['evidenceRefs']:assert r['path']not in pins or pins[r['path']]==r['sha256'];pins[r['path']]=r['sha256']
 for p,h in pins.items():assert sha(R/p)==h,p
 assert sha(R/'3d-viewer/city/data/manifest.json')==CURRENT
 a=read(BUILD/'full-computed-private-candidate-and-account.json.gz');patch=read(R/a['candidatePath']);assert sha(R/a['candidatePath'])==a['candidateSHA256'];proof=a['account']['all25CompleteProductionBasicAndExplicitNativeInputsVerbatim'];rows=[r for r in proof['rows']if r['uid']in NINE];assert len(rows)==9 and all(r['classification']=='actual-production-BASIC'for r in rows)
 guard=read(RUN/'neighbour-checks.json');failed=[r for r in guard['rows']if r['reasons']==['increased-neighbour-ground-gap']];assert {r['uid']for r in failed}==NINE
 probes=[json.loads(line)for line in (RUN/'actual-interface-max-ray-rows.ndjson').read_text().splitlines()];assert len(probes)==6701 and [r['probe']for r in probes]==list(range(6701))and all(r['existingRayAgreementGuardPass']is True for r in probes)
 for p in pins:assert sha(R/p)==pins[p]
 return pins,a,patch,rows,failed,probes,read(FEAS)['allCurrent12GroundFacetsVerbatim']
def main():
 pins,a,patch,rows,failed,probes,parents=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(allPassed=True,nineRawFailuresRetained=True,savedMAXProbes=6701,currentManifestSHA256=CURRENT,noDB=True,noLease=True,noSavedGeometryProcessing=True)));return
 assert '--calculate-saved-height-context-only'in sys.argv;out=D/'calculation-v1';out.mkdir(exist_ok=False);positions=patch['nativeMesh']['position'];indices=patch['nativeMesh']['index'];triangles=[[positions[j*3:j*3+3]for j in indices[i:i+3]]for i in range(0,len(indices),3)];assert len(triangles)==3214;bins=m.bins_for_triangles(triangles);pbins=m.bins_for_triangles(parents);decoded={r['uid']:m.decode_complete_basic(r)for r in rows};records=[]
 for probe in probes:
  xz=tuple(F(v)for v in probe['exactXZ']);members=[]
  for row in rows:
   modes=[]
   for mode,geometry in decoded[row['uid']].items():
    faces=m.nominated_closed_faces(xz,geometry['triangles'],geometry['bins'])
    if faces:modes.append(dict(arithmetic=mode,completeActualBasicProjectionFaceIds=faces))
   if modes:members.append(dict(uid=row['uid'],wholeFourWorldMembershipRows=modes))
  if not members:continue
  original_faces=m.nominated_closed_faces(xz,parents,pbins);original_heights=[(i,m.exact_plane_height(xz,parents[i]))for i in original_faces];values=[y for _,y in original_heights if y is not None];candidate_faces=m.nominated_closed_faces(xz,triangles,bins);lineage=[a['account']['completeOutputFacetLineage'][i]for i in candidate_faces]
  records.append(dict(savedProbeVerbatim=probe,exactXZ=xz,completeNineActorMembership=members,completeClosedCapturedParentFaceIds=original_faces,exactCapturedParentPlaneHeights=original_heights,exactParentUpperHeight=max(values)if values else None,savedActualPrivateSceneSamplerHeight=probe['actualPrivateSceneSamplerHeight'],sourcePlaneMinusSavedSamplerContextOnly=max(values)-F(probe['actualPrivateSceneSamplerHeight'])if values else None,completeClosedCandidateProjectionFaces=candidate_faces,completeCandidateSourceOrCollarParentLineage=lineage,noOriginalGuardSampleCorrespondenceClaim=True))
 result=dict(fullNineRawGuardFailuresVerbatim=failed,allNineCompleteCurrentForms=[r['currentForm']for r in rows],allNineWholeActualBasicBuffersAndIndexEvidenceVerbatim=rows,allClosedSavedProbeContexts=records,allOriginal752FailuresAndWholeSourceRolesRemain=a['account']['all752FourModeRawNegativesAnd21BodiesVerbatim'],native59527BeforeAfterStillPending=True,notCoverageGuardFailure=True,noRestorationMaskOrFullDomainHeightProof=True,saved6701ProbesAreNotOriginalGuardSampleSet=True,noNewProductionSamplerOrGuardQueries=True,noGroundPredicateOrFullFiniteReplay=True,currentAcceptance=False,physicalAccepted=False,inputHashes=pins)
 for p,h in pins.items():assert sha(R/p)==h,p
 assert sha(R/'3d-viewer/city/data/manifest.json')==CURRENT
 with gzip.open(out/'context.json.gz','wt')as f:json.dump(result,f,sort_keys=True,default=lambda x:str(x)if isinstance(x,F)else None)
 print(json.dumps(dict(actors=9,savedContextRecords=len(records),contextSHA256=sha(out/'context.json.gz'),noRestorationMaskProof=True,currentAcceptance=False)))
if __name__=='__main__':main()
