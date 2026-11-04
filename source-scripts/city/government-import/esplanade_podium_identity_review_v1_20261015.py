"""Replay the bounded root-reviewed original Esplanade podium identity decision.

The unique explicit government/CSUID link and complete footprint evidence support
identity for this exact source. Old centroid and whole-cell negatives are retained.
No generic threshold change, geometry change or placement/publication approval.
"""
from pathlib import Path
import importlib.util
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
UID='landsd/309385:0';SHA='ab5f78c1349cfb01db2d60bb36af0122ec8d374abaa5c8b63eaac63f58cd097c';MODEL='B148452746002063C0';CSUID='1484527460P20191115'
BATCH='government-xl-esplanade-podium-reviewed-identity-v1-20261015';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PHYSICAL=BASE/'government-xl-esplanade-pair-current-physical-v3-20261015'

def main():
 assert not DOC.exists();receipt=read(PHYSICAL/'result.json')
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 row=next(r for r in read(PHYSICAL/'selection.json.gz')['rows']if r['uid']==UID);proof=next(r for r in read(PHYSICAL/'owned-source-identity.json')['rows']if r['uid']==UID);form=row['source']['building'];native=row['native'];model=native['model'];asset=ROOT/row['candidate']['path']
 assert row['modelId']==model['modelId']==MODEL and row['sourceSHA256']==model['asset']['sha256']==SHA==digest(asset.read_bytes());assert form['uid']==UID and form['buildingCSUID']==CSUID and form['objectId']==309385 and form['structureType']=='Podium';assert MODEL[1:11]==CSUID[:10] and MODEL[11:13]=='02' and CSUID[10]=='P'
 assert digest((ROOT/'3d-viewer'/row['source']['tile']).read_bytes())==row['source']['tileSHA256'];live=read(ROOT/'3d-viewer'/row['source']['tile'])['buildings'];assert [b for b in live if b['uid']==UID]==[form]
 assert proof['originalOwnership']['sourceGraphVerified'] and proof['originalOwnership']['originalRootName']==MODEL
 assert set(proof['originalOwnership']['reasons'])=={'cached-spatial-officialCandidates','cached-spatial-officialMatches','cached-spatial-viewerMatches'}
 assert set(proof['reasons'])=={'current-target-does-not-cover-whole-georef-cell','original-source-does-not-cover-whole-georef-cell'}
 for key in ['officialCandidates','officialMatches','viewerMatches']:
  matches=model['matching'][key];assert len(matches)==1;match=matches[0];assert match['objectId']==309385 and match['buildingCSUID']==CSUID
  if key=='viewerMatches':assert match['uid']==UID
 assert proof['exactCurrentComponentRoute']['qualified'] and proof['exactCurrentComponentRoute']['uid']==UID
 identity=proof['freshCurrentIdentity'];assert identity['exactObjectAndCSUID'] and identity['targetCoveredBySourceProjection']>=.95 and identity['sourceExcessMaximumDistanceFromTargetM']<=10 and identity['sourceExcessCoveredByUnrelatedFormsM2']<=1
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,native['cacheKey'])).fetchone()==(native['resultSha'],)
 decision=dict(uid=UID,modelId=MODEL,sourceSHA256=SHA,governmentBuildingCSUID=CSUID,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawFallbackProof=proof,reviewScope='Exact unchanged original Esplanade podium identity only',reviewBasis=['Original named FME root, complete original byte/mesh ownership and fixed source pose verified.','One explicit authoritative candidate, official match and viewer match all identify the same dated podium CSUID and object ID; fresh whole-map route is unique.','Complete current source projection covers 99.64968739482565% of the official footprint; excess maximum distance is 0.2995156249999127 m; unrelated-form overlap is zero.','Root-inspected source/official footprint overlay corroborates the same unusual perimeter. The one-metre identifier cell lies outside both almost-identical footprints, so failure of that sufficient fallback does not contradict the explicit source-record identification.','The 2.558 m centroid difference is retained as a shape diagnostic. Identity is established from exact linkage plus complete footprint evidence, not a relaxed centroid tolerance.'],placementReviewed=False,publicationApproved=False,aiGeometryModelling=False)
 save(DOC/'identity-review.json',decision)
 (DOC/'ROOT-REVIEW.md').write_text('# Esplanade podium source identity review\n\nApproved only for original asset '+SHA+' and dated CSUID '+CSUID+'.\n\n'+'\n\n'.join(decision['reviewBasis'])+'\n\nThis resolves identity only. All terrain, support, other geometry representations, neighbour, runtime and browser checks remain independent. No live catalogue/model-review approval is written. Original negative receipts remain unchanged.\n')
 paths=[Path(__file__),PHYSICAL/'result.json',PHYSICAL/'selection.json.gz',PHYSICAL/'owned-source-identity.json',asset,ROOT/'3d-viewer'/row['source']['tile'],ROOT/'3d-viewer/city/data/manifest.json',BASE/'government-xl-esplanade-pair-current-physical-v1-20261015/podium-source-identity.png',BASE/'government-xl-esplanade-pair-current-physical-v1-20261015/podium-cell-context.json']
 spec=importlib.util.spec_from_file_location('esplanade_identity_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'root-reviewed-exact-original-podium-identity-v1',paths,dict(uids=[UID],sourceSHA256=SHA,identityAccepted=True,sourceIdentityReviewUsedAI=True,identityProof=decision['identityProof'],fullAcceptance=False,nextStep='Complete source-specific placement/support and current staging/browser checks; identity review gives no installation credit.'))
if __name__=='__main__':main()
