"""Compare existing canonical identity route with alternative; retain fresh-source failures."""
from pathlib import Path
import shutil
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_source_ownership import document,graph_reasons
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-verdant-identity-residuals-v1-20261018';BATCH='government-xl-wave-verdant-identity-routes-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 sources={}
 for name,file,key in [('government-xl-wave-all-original-support-distance-v1-20261017','support-inputs.json','sources'),('government-xl-wave-verdant-podium-support-v1-20261017','support-inputs.json','sources'),('government-xl-wave-verdant-block2-original-recovery-v1-20261017','selection.json.gz','rows'),('government-xl-wave-verdant-194544-original-recovery-v1-20261017','selection.json.gz','rows')]:
  p=BASE/name/file;refs.append(p);sources.update({x['uid']:x for x in read(p)[key]})
 second=module('wave_fresh_projection_route',HERE/'xl-second-pass.py');policy=module('wave_existing_policy_route',HERE/'acceptance-policy.py');proofs=read(BASE/'government-xl-wave-verdant-authoritative-identity-v1-20261018/summary.json')['rows'];rows=[]
 for q in proofs:
  uid=q['uid'];row=sources[uid];e=row['candidate']['entry'];form=row['source']['building'];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);metrics=second.projection_metrics(tri,Polygon(form['rings'][0],form['rings'][1:]));graph=graph_reasons(document(raw),row['native']['model']['modelId'],row['native']['model']['triangles']);matches=row['native']['model']['matching'];unique=all(len(matches[k])==1 and matches[k][0]['objectId']==form['objectId'] and matches[k][0]['buildingCSUID']==form['buildingCSUID'] and (k!='viewerMatches' or matches[k][0]['uid']==uid)for k in ['officialCandidates','officialMatches','viewerMatches'])
  # Evaluate only strict-identity-fit from the actual unchanged policy. The
  # synthetic other inputs are explicitly NOT physical/runtime acceptance.
  def canonical(overlap,centroid):
   metric=dict(sourcePreserved=True,sourceSHA256=row['sourceSHA256'],minSurfaceGap=0,minLowGap=0,maxLowGap=0,maxSamplerDelta=0,lowRimChecks=1,identity=dict(overlap=overlap,centroidDistance=centroid),budget=dict(triangles=0,geometryBytes=0,residentBytes=0))
   reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256']),metric,dict(triangles=0,geometryBytes=0,residentBytes=0));return 'strict-identity-fit'not in reasons
  cached=canonical(e['overlapOfSmallerFootprint'],e['footprintCentroidDistanceMetres']);fresh=canonical(metrics['overlapOfSmaller'],metrics['centroidDistance']);canonical_pass=cached and fresh and unique and not graph;alternative=q['proof']['passed'];rows.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],exactUniqueIdentifiers=unique,graphReasons=graph,cachedCanonicalPass=cached,freshCanonicalPass=fresh,canonicalIdentityPass=canonical_pass,alternativeIdentityPass=alternative,identityRouteAvailable=canonical_pass or alternative,cachedIdentity=dict(overlap=e['overlapOfSmallerFootprint'],centroid=e['footprintCentroidDistanceMetres']),freshProjection=metrics,alternativeReasons=q['proof']['reasons']));print({k:rows[-1][k]for k in ['uid','canonicalIdentityPass','alternativeIdentityPass','identityRouteAvailable']},flush=True)
 assert next(x for x in rows if x['uid']=='landsd/301558:0')['canonicalIdentityPass']
 save(DOC/'summary.json',dict(rows=rows,fullAcceptance=False,installationApproved=False,qualification='Only identity route accounting. Canonical identity predicate is the existing acceptance-policy.py threshold with no exception flags, confirmed against both cached and fresh complete-source metrics plus unique source IDs and original graph ownership. Alternative whole-georef route is not universally mandatory. Synthetic non-identity inputs are not support, placement, runtime or physical evidence. All historical alternate-route warnings remain recorded.'))
 DOC.mkdir(exist_ok=True);shutil.copyfile('/tmp/wave-verdant-identity-boundaries.png',DOC/'complete-boundaries.png')
 refs.extend([HERE/'xl-second-pass.py',HERE/'acceptance-policy.py',HERE/'original_source_ownership.py',HERE/'exact_packed_world_geometry_20261009.py',*[ROOT/p for p in pins]])
 out=module('wave_routes_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-identity-existing-policy-route-accounting-v1',list(set(refs)),dict(uids=[x['uid']for x in rows],identityRoutesAvailable=sum(x['identityRouteAvailable']for x in rows),fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
