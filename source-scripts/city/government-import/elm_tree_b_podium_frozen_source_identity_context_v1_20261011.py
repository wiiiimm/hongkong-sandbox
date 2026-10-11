"""DRAFT immutable source identity context before any Elm authentic-TIN processing.
Existing fixed spatial bounds only, no actual current collision/support clearance.
"""
from pathlib import Path
import importlib.util,json,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-elm-tree-b-podium-frozen-source-identity-context-v1-20261011';DOC=B/BATCH;CAP=B/'government-xl-beverly-elm-complete-current-support-ground-capture-v2-20261011';NOM=B/'government-xl-fixed295-simple-source-support-nomination-census-v1-20261011';CONTACT=B/'government-xl-elm-tree-b-original-podium-complete-finite-contact-inventory-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__)),ref(HERE/'exact_packed_world_geometry_20261009.py'),ref(HERE/'xl-final-script-pass.py')]
 for folder in [CAP,NOM,CONTACT]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(ref(folder/'result.json'))
 pre=read(CAP/'support-source-preflight.json');spec=importlib.util.spec_from_file_location('reviewed_fixed_identity_context',HERE/'xl-final-script-pass.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);forms=[(r['building'],m.form_polygon(r['building']),r['tile'])for r in pre['fullCurrentRelevantForeignBasicAndNativeFormInventory']];tower=next(r for r in read(NOM/'diagnostic.json.gz')['rows']if r['uid']=='landsd/253874:0');podium=next(r for r in read(CAP/'selection.json.gz')['rows']if r['uid']=='landsd/258892:0');old_podium_selection=B/'government-xl-elm-tree-podium-physical-20261007/selection.json.gz';old_podium=next(r for r in read(old_podium_selection)['rows']if r['uid']=='landsd/258892:0');assert old_podium['sourceSHA256']==podium['candidate']['entry']['sha256'];refs.append(ref(old_podium_selection));sources=[];contact=read(CONTACT/'diagnostic.json.gz')
 for uid,assetref,model,expectedcount,expectedworld in [('landsd/253874:0',tower['sourceAsset'],tower['nativeProviderModel'],12164,contact['completeTowerWorldSHA256']),('landsd/258892:0',ref(ROOT/podium['candidate']['path']),old_podium['native']['model'],764,contact['completePodiumWorldSHA256'])]:
  asset=ROOT/assetref['path'];assert ref(asset)==assetref;world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(expectedcount,3,3)and digest(world.tobytes())==expectedworld;form=next(f for f,p,t in forms if f['uid']==uid);candidate=model.get('candidate');assert candidate and candidate['objectId']==form['objectId']and candidate['buildingCSUID']==form['buildingCSUID'];sources.append((uid,world,dict(uid=uid,native=dict(model=model)),assetref['sha256']));refs.append(assetref)
 pworld=next(w for u,w,r,h in sources if u=='landsd/258892:0');lo,hi=pworld.min((0,1)),pworld.max((0,1));query=[float(lo[0]-30),float(lo[2]-30),float(hi[0]+30),float(hi[2]+30)];rows=[]
 for uid,world,row,sha in sources:
  assert world[:,:,0].min()>=query[0]and world[:,:,0].max()<=query[2]and world[:,:,2].min()>=query[1]and world[:,:,2].max()<=query[3],'Tower source outside frozen podium30m complete form inventory; new capture required';c=m.identity_context(row,world,forms);reasons=[]
  if c['targetCoveredBySourceProjection']<.95:reasons.append('targetCoveredBySourceProjection')
  if c['sourceExcessMaximumDistanceFromTargetM']>10:reasons.append('sourceExcessMaximumDistanceFromTargetM')
  if c['sourceExcessCoveredByUnrelatedFormsM2']>1:reasons.append('sourceExcessCoveredByUnrelatedFormsM2')
  rows.append(dict(uid=uid,sourceSHA256=sha,completeOriginalWorldSHA256=digest(world.tobytes()),completeOriginalFaces=len(world),rawFixedSpatialIdentityContext=c,fixedSpatialBoundsOnlyFailedFields=reasons,wholeIdentityAccepted=False,sourceOrdinaryTerrainProved=False,currentCollisionCleared=False))
 refs.extend(ref(p)for p in [CAP/'support-source-preflight.json',CAP/'selection.json.gz',NOM/'diagnostic.json.gz',CONTACT/'diagnostic.json.gz']);save(DOC/'diagnostic.json.gz',dict(uids=[r['uid']for r in rows],rows=rows,sourceOnly=True,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,historicalExactCurrentManifest=pre['currentManifest'],frozenCompleteCurrentFormsScope=query,noMutableCapture=True,allRawHistoricalObligations=pre['historicalObligations'],qualification='Existing Shapely original footprint context only; exactObject/CSUID source-route metadata is distinct from full current acceptance. Full P764 current finite burial223facets/min−9.371756m, old BASIC233656/253871 regressions, all306tower bodies/grade root and source-to-current foreign/native/runtime obligations remain. No authored source intent, changed thresholds, narrowed component role or actual collision exemption; any spatial conflict requires independent source/actual finite geometry evidence before authenticTIN processing.',evidenceRefs=refs));print(json.dumps(dict(rows=[dict(uid=r['uid'],fixedSpatialFailedFields=r['fixedSpatialBoundsOnlyFailedFields'])for r in rows],currentAcceptance=False)))
if __name__=='__main__':main()
