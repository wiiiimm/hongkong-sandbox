"""Immutable source-specific Olympian City2 assembly identity; no placement approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-park-avenue239350-identity-review-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UID='landsd/239350:0'
IDENTITY=BASE/'government-xl-park-avenue239350-current-identity-runtime-v3-20261018'
ASSEMBLY=BASE/'government-xl-park-avenue239350-assembly-projection-v2-20261018'
COMPANIONS=BASE/'government-xl-park-avenue239350-companion-identity-runtime-v1-20261018'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for directory in [IDENTITY,ASSEMBLY,COMPANIONS]:
   r=read(directory/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(directory/'result.json')
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(IDENTITY/'selection.json.gz')['rows'][0];old=read(IDENTITY/'239350:0-identity.json');proof=verify_files(row,old['context'],LOCAL/'identity-recheck')
 for k in ['uid','sourceSHA256','sourceFormSHA256','worldTrianglesSHA256','freshCurrentIdentity','reasons']:assert proof[k]==old['proof'][k],k
 assert proof['originalOwnership']['sourceGraphVerified'] and proof['exactCurrentComponentRoute']['qualified'] and proof['exactCurrentComponentRoute']['uid']==UID
 assert proof['exactWholeCellCoverage']['covered'] and proof['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==14637 and proof['geographicCell']['targetCoversWholeCell']
 expected={'fresh-current-spatial-bound:'+k for k in ['sourceExcessCoveredByUnrelatedFormsM2','sourceExcessMaximumDistanceFromTargetM','targetCoveredBySourceProjection']}|{'full-source-maximum-extent','full-source-target-coverage','full-source-unrelated-overlap'}
 assert set(proof['reasons'])==expected
 coverage=read(ASSEMBLY/'summary.json');assert coverage['sourceSHA256']==proof['sourceSHA256'];assert abs(coverage['remainingMissingM2']-14.782762416601516)<1e-8
 companions=[]
 for c in read(COMPANIONS/'selection.json.gz')['rows']:
  cp=COMPANIONS/(c['uid'].split('/')[1]+'-identity.json');q=read(cp)['proof'];assert q['passed'] and not q['reasons'] and q['sourceSHA256']==c['sourceSHA256'];companions.append(dict(uid=c['uid'],sourceSHA256=c['sourceSHA256'],identityProofPath=str(cp.relative_to(ROOT))));refs.append(cp)
 assert {c['uid'] for c in companions}=={'landsd/240161:0','landsd/227455:0'}
 review=dict(uid=UID,sourceSHA256=proof['sourceSHA256'],sourceFormSHA256=proof['sourceFormSHA256'],worldTrianglesSHA256=proof['worldTrianglesSHA256'],identityOnlyApproved=True,identityReviewApproved=True,sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,sourceFaces=14637,rawProof=proof,rawReasonsRetained=proof['reasons'],requiredAssemblyOriginals=companions,assemblyCoverage=1-coverage['remainingMissingM2']/coverage['targetAreaM2'],reviewBasis=[
 'ROOT inspected complete original projection, all residual polygons and adjoining installed/recovered original projections. Main outline, circular recess and the separately supplied upper structure align with the target. The source is not translated or rescaled.',
 'Exact original government ObjectID/CSUID/type, unique fresh route, immutable graph and full one-metre GeoRef cell are proven. The recovered upper source240161 independently passes identity and accounts for590.364904m2 of the missing footprint. Complete assembly coverage is99.80113099percent; remaining15pieces total14.782762m2 and follow boundary strips and small corner fragments visible in the complete plot.',
 'Extensions remain unmodified: the north long wing and rounded end, narrow southern perimeter strip and eastern connector are explicit parts of the original podium outline. Recorded maximum extent23.757760866m is retained. Footprint overlap with239351is389.600293m2 but actual original-source projected overlap is0.051352m2; with227455the corresponding values are215.343498m2 and0.141651m2. Differing coarse GIS polygons do not establish a wrong government source.',
 'The archived architect context describes an integrated retail/residential podium development. It is qualitative architectural context, not surveying or proof that source crossings are physically acceptable.',
 'Approval binds only these exact source/form/world inputs and complete companion identities. Raw six reasons stay archived. No terrain, support, collision, neighbour, runtime, browser, actor suppression or publication exemption follows. All1052current buried faces still require terrain repair and complete rechecks.'
 ],placementReviewed=False,publicationApproved=False,installationApproved=False,modelGeometryChanges=0)
 save(DOC/'239350:0-review.json',review)
 refs.extend(ROOT/p for p in pins);refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'routed_original_cell_identity.py',HERE/'component_type_resolution.py',ASSEMBLY/'differences.geojson',ASSEMBLY/'whole-source-differences.png'])
 architect=BASE/'government-xl-olympian-two-primary-architect-v1-20261018';refs.extend(architect/f for f in ['provenance.json','page-text.txt','810_180501-web-project-page.jpg'])
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 out=module('park_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'park-avenue239350-exact-assembly-identity-review-v1',list(set(refs)),dict(uids=[UID],identityOnlyApproved=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
