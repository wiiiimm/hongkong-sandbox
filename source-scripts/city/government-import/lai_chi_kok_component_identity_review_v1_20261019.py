"""Exact-source component identity interpretation; no placement/publication approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-component-identity-review-v1-20261019';DOC=BASE/BATCH
PHASES=['original-component-checks-v1','component-visual-observations-v1','component-boundary-audit-v1','assembly-footprints-v1','eight-render-attributes-v1']
EXPECTED={'landsd/218874:0':'49b5d1d5e066cf371cb67b31212d73a95461658bd92409c3d85491beec3ce981','landsd/206341:0':'7148ba11cc2305ba2d3cf246d48bf5ebc83859ad0363ffc344ef5055d8a11685','landsd/207349:0':'ce8d467ae23366c8f8efa2498dfe92fbfd95d972a4850988cd2129d99f9ad4db','landsd/206337:0':'cf4be5fd195004302c9c7a3d4f3e67bfd062d33f6ac4e9b532e66245a6b190a9'}
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};folders={p:BASE/('government-xl-lai-chi-kok-'+p+'-20261019')for p in PHASES}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in folders.values():
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 observations={r['uid']:r for r in read(folders['component-visual-observations-v1']/'observations.json')['rows']};coverage={r['uid']:r for r in read(folders['assembly-footprints-v1']/'summary.json')['rows']};boundaries={r['uid']:r for r in read(folders['component-boundary-audit-v1']/'summary.json')['rows']};reviews=[]
 for uid,sha in EXPECTED.items():
  p=folders['original-component-checks-v1']/(uid.split('/')[1]+'-identity.json');raw=read(p);scope=raw['freshCurrentIdentity'];own=raw['originalOwnership'];obs=observations[uid];cov=coverage[uid]
  assert raw['sourceSHA256']==own['sourceSHA256']==cov['sourceSHA256']==sha
  assert own['sourceGraphVerified']and scope['exactObjectAndCSUID']and raw['exactCurrentComponentRoute']['qualified']and raw['exactWholeCellCoverage']['covered']
  assert set(raw['reasons'])=={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'}
  assert {r['uid']for r in scope['intersectingForms']}=={uid,'landsd/281463:0'}and scope['sourceExcessCoveredByUnrelatedFormsM2']==0
  assert obs['actuallyViewedByCoordinator']and digest((ROOT/obs['image']['path']).read_bytes())==obs['image']['sha256']
  assert cov['missingAssemblyArea']==0 if uid!='landsd/206337:0'else abs(cov['missingAssemblyArea']-0.0004515342529886699)<1e-12
  reviews.append(dict(uid=uid,sourceSHA256=sha,originalRootName=own['originalRootName'],sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],identityAccepted=True,sourceSpecificAssemblyIdentityAccepted=True,rawPassed=raw['passed'],rawReasons=raw['reasons'],rawProofSHA256=digest(p.read_bytes()),projection=scope,boundaryDifference=boundaries[uid],assemblyCoverage=cov,priorInspectedImage=obs['image'],shapeObservation=obs['observation'],supportAccepted=False,installationApproved=False))
 decision=dict(reviewer='Codex ROOT',rows=reviews,requiredAssemblySources={r['uid']:r['sourceSHA256']for r in read(folders['eight-render-attributes-v1']/'selection.json.gz')['rows']},basis='Exact government object and CSUID routing, verified complete original model graph, shared geographic cell, inspected component outline and complete assembly projection identify these four original components. Their individual outline deficits are accounted by the unchanged platform, apart from the explicitly retained 0.0004515342529886699 square metre residual for206337. No other building competes in the full projection. This accepts component identity only within the exact eight-source assembly; it does not invent architectural names or claim the footprint datasets are identical.',qualification='Preserve raw coverage failures. This source-specific review is not a new coverage threshold, footprint repair, shared-parent assertion, support acceptance or permission to publish. Source or footprint changes invalidate this review.',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,modelGeometryChanges=0,publicationApproved=False,installationApproved=False)
 save(DOC/'ROOT-IDENTITY-REVIEW.json',decision)
 module('component_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-original-component-exact-assembly-identity-review',list(dict.fromkeys(refs)),dict(uids=list(EXPECTED),sourceSpecificAssemblyIdentityAccepted=True,identityAccepted=True,installationApproved=False,remaining=['source-specific lower-wall support acceptance','platform identity and grade review','current neighbours and browser acceptance','guarded installation and commit/push']))
if __name__=='__main__':main()
