"""UNEXECUTED scoped source-TIN representation nomination; no terrain deployment."""
from pathlib import Path
import json,sys,time,uuid,subprocess
import numpy as np
import upton_saved_cut_node_ancestor_correspondence_draft_v1_20261013 as prior
from upton_source_family_exact_subdivision_v1_20261013 import subdivide_source_triangle
from run import ROOT,HERE,read,save,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-source35676-35677-scoped-subdivision-v1-20261013'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JOB='7149806d2d5667e8c5c0ac1216ca76873688c93f4a20bb5991fd3e10592f8d2d'
ref,check=prior.ref,prior.check
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 receipt=read(prior.DOC/'result.json');assert receipt['jobId']==JOB
 out=read(prior.DOC/'complete-saved-cut-node-ancestor-correspondence.json.gz');assert len(out['intervalPointRows'])==100 and len(out['areaRows'])==257
 _,_,_,nomination,raw,pv,source,current,drawn,_=prior.prior.prior.load()
 assert nomination['wholeSourceOriginalFaceInventory'][35676]['emittedCandidateFaces']==[380]and nomination['wholeSourceOriginalFaceInventory'][35677]['emittedCandidateFaces']==list(range(381,390))
 p=pv[380];assert p['kind']=='originalTIN'and p['originalFace']==35676 and p['savedInputByteExact']and not p['computedFragment']and p['region']=='sourceOutsideProtection'
 assert raw[380].tobytes()==source[35676].tobytes()
 node=tuple(prior.F(v)for v in out['cutNodeIdealXYZ']);exact_source=prior.exact(source[35676])
 row=next(r for r in out['completeClosedProjectedSourceAncestorNominees']if r['originalSourceFace']==35676);assert row['untouchedOriginalXYZ']==prior.serial(exact_source)
 assert [r['candidateFace']for r in out['allCompleteCandidateNodeIncidents']if r['exact3DNodeIncident']]==[381,382]and not any(r['literalWholeCurrentProtected']for r in out['allCompleteCandidateNodeIncidents'])
 protected=[i for i,p in enumerate(pv)if p.get('region')=='wholeCurrentProtectionFacet'];assert len(protected)==68 and 380 not in protected
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.prior.prior.prior.CURRENT
 return pins,receipt,out,nomination,raw,pv,source,node,exact_source,protected
def schema_only():
 p,r,o,n,raw,pv,s,node,t,protected=load()
 return dict(passed=True,caller=ref(Path(__file__)),oldCandidateFaces=11575,sourceAncestorFamily=[35676,35677],targetOldCandidate=380,heldOtherFamilyCandidates=list(range(381,390)),protectedWholeCurrentTriplets=68,savedIntervalRows=100,savedAreaRows=257,noSubdivisionPackingWorkerOrLease=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,receipt,out,nomination,raw,pv,source,node,t,protected=load()
 validation=read(PROPOSAL/'helper-validation.json');assert validation['passedTests']==9 and validation['failedTests']==0 and validation['exitCode']==0
 assert validation['executedCodeRefs']==[ref(HERE/'upton_source_family_exact_subdivision_v1_20261013.py'),ref(HERE/'test_upton_source_family_exact_subdivision_v1_20261013.py')]
 for q in validation['executedCodeRefs']+[validation['actualLog']]:check(q)
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'helper-validation.json')]+receipt['evidenceRefs']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 for q in refs:check(q);pulse()
 proof=subdivide_source_triangle(t,node,1);pieces=proof['exactPiecesXYZ'];candidate=[];provenance=[];mapping=[];expected_node=np.asarray([float(prior.F(v))for v in out['cutNodeActualPackedXYZ']],dtype='<f8')
 def append(face,record):
  value=np.asarray(face,dtype='<f8');assert value.shape==(3,3)and np.isfinite(value).all();j=len(candidate);candidate.append(value);provenance.append({**record,'candidateFace':j,'rawNominationFaceSHA256':prior.prior.prior.prior.prior.sha(value)});return j
 for i,(face,p)in enumerate(zip(raw,pv)):
  if i==380:
   ids=[]
   for part,q in enumerate(pieces):
    value=np.asarray([[float(v)for v in a]for a in q],dtype='<f4').astype('<f8')
    for vertex,ip in enumerate(q):
     if ip in t:value[vertex]=raw[380][t.index(ip)] # Original endpoint bytes, including zero sign.
     if ip==node:assert value[vertex].tobytes()==expected_node.tobytes()
    # SAME saved node and nearest Float32 storage, with exact original ideal
    # source plane before packing. Packed planes require fresh finite checks.
    ids.append(append(value,{**p,'computedFragment':True,'savedInputByteExact':False,'exactOriginalPlanePoints':prior.serial(q),'scopedSourceFamilySubdivision':dict(oldCandidateFace=380,originalFace=35676,part=part,exactNodeXYZ=prior.serial(node),governmentSourceUnchanged=True)}))
  else:ids=[append(face,p)];assert candidate[ids[0]].tobytes()==face.tobytes()
  mapping.append(dict(oldCandidateFace=i,newCandidateFaces=ids,oldRawTripletSHA256=prior.prior.prior.prior.prior.sha(face),allOldRawBytesUnchanged=i!=380))
  if i%256==0:pulse()
 candidate=np.asarray(candidate,dtype='<f8');assert candidate.shape==(11576,3,3)
 protected_rows=[]
 for i in protected:
  j=mapping[i]['newCandidateFaces'][0];assert candidate[j].tobytes()==raw[i].tobytes();protected_rows.append(dict(oldCandidate=i,newCandidate=j,rawTripletSHA256=prior.prior.prior.prior.prior.sha(raw[i]),provenanceVerbatim=pv[i]))
 assert all(mapping[i]['allOldRawBytesUnchanged']for i in range(11575)if i!=380)
 DOC.mkdir(parents=True);save(DOC/'private-source-family-subdivision-nomination.json.gz',prior.serial(dict(originalNomination=ref(prior.prior.prior.prior.V6/'complete-nominations-before-guards.json.gz'),originalSourceTriplets=nomination['allSourceOriginalTriplets'],originalWhole35676Triplet=proof['exactOriginalXYZ'],exactSourceFamilyPartitionProof=proof,candidateRawPositionTriplets=candidate.tolist(),candidateFaceProvenance=provenance,completeOldNewIndexMapping=mapping,protectedWholeCurrentTripletsUnchanged=protected_rows,completeUnchangedSource35677CandidateFamily=[pv[i]for i in range(381,390)],completeSavedFailuresVerbatim=dict(interval=out['intervalPointRows'],area=out['areaRows']),allActualDrawCoverageOrdinaryForeignSamplerOverlapValidatorChecksUnexecuted=True,physicalAccepted=False,installationApproved=False,originalBuildingGeometryPoseChanges=0)))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 for q in refs:check(q);pulse()
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.prior.prior.prior.CURRENT;pulse(True)
 prior.prior.prior.prior.prior.module(prior.prior.prior.prior.prior.FREEZER,'upton_scoped_subdivision_freezer').freeze(BATCH,'private-original-source-family-representation-only',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=prior.prior.prior.prior.prior.OWNED+[prior.prior.prior.prior.prior.SECONDARY,prior.prior.prior.prior.prior.NATIVE],sourceOnly=True,privateNomination=True,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--nominate-source-family-subdivision-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 uids=prior.prior.prior.prior.prior.OWNED+[prior.prior.prior.prior.prior.SECONDARY,prior.prior.prior.prior.prior.NATIVE,prior.prior.prior.prior.prior.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-source-family-subdivision-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
