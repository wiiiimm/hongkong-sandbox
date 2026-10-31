"""Bind the current station identity fit to the unchanged original source."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ets-original-source-review-v1-20261015';DOC=BASE/BATCH
UID='landsd/323703:0';SHA='4f483e0d26cd40ba3bf93c6edd1e8485e5d11c2d7cde3cd9243651f0505784ea'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 folders=['combined-identity-context-v1','current-placement-metrics-v1','four-world-ground-v1','native-finite-v1','native-parent-scope-v1','basic-finite-v1']
 for name in folders:
  folder=BASE/('government-xl-ets-'+name+'-20261015');r=read(folder/'result.json');refs.append(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for q in r['evidenceRefs']:
   assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
 def data(name,file):return read(BASE/('government-xl-ets-'+name+'-20261015')/file)
 context=data('combined-identity-context-v1','context.json');assert context['sourceSHA256']==SHA
 metrics=data('current-placement-metrics-v1','metrics.json');row=data('current-placement-metrics-v1','selection.json.gz')['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SHA
 policy=module('ets_actual_policy',HERE/'acceptance-policy.py');policyRows=[]
 for world in context['rows']:
  own=next(x for x in world['overlaps']if x['uid']==UID);metric={**metrics['rows'][0],'identity':{'overlap':own['targetCoverage'],'centroidDistance':own['centroidDistanceM']}}
  reasons=policy.reasons(row,metric,metrics['profiles']['mobile']);assert not reasons,reasons;policyRows.append({'mode':world['mode'],'identity':metric['identity'],'policyReasons':reasons})
 assert data('native-finite-v1','summary.json')['noIntroducedFailures'];assert data('basic-finite-v1','summary.json')['noIntroducedFailures']
 ground=data('four-world-ground-v1','summary.json');assert ground['allFourModesCovered']and ground['allFourModesUnburied']
 primary=BASE/'government-xl-unmapped-two-primary-evidence-v1-20261015'
 refs.extend(primary/n for n in ['README.md','middle-road-official.html','middle-road-a.jpg','middle-road-e.jpg','photos-provenance.json','provenance.json','viewer-bindings.json']);refs.append(HERE/'acceptance-policy.py')
 DOC.mkdir();review={'primaryUID':UID,'sourceSHA256':SHA,'modelId':'B360171738601063C0','identityAccepted':True,'sourceGeometryChanges':0,'sourcePoseChanges':0,'scale':1,'exactLegacyGeoRefClaimed':False,'policyRows':policyRows,'policyExceptions':[],'additionalSuppressionUIDs':[],'observation':'Current station podium footprint is covered 99.6479 percent; centroid offset 0.3726m, passing existing strict fit in all four modes. Government FSO identifies Middle Road playground on East Tsim Sha Tsui station podium. Retrieved official photographs visually inspected show curved playground paths, pergola structures and curved entrance wall, consistent with original platform source and desktop rendered preview. Historical source georef and current CSUID differ; no exact identifier lineage is claimed. Projection extends up to 6.93m beyond current footprint; small overlaps with adjacent current forms are preserved and do not independently fail existing identity or terrain policy. No neighbouring form is suppressed. This review accepts original station platform source identity, not completeness of every modern playground furnishing.','visualPublicationAcceptance':False,'installed':False}
 save(DOC/'ROOT-SOURCE-REVIEW.json',review)
 module('ets_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-station-original-source-identity-existing-policy',refs,{'uids':[UID],'identityAccepted':True,'policyExceptions':[],'fullAcceptance':False,'newlyInstalled':0});print('Source identity and existing policy pass; final visual/publication qualification still pending',flush=True)
if __name__=='__main__':main()
