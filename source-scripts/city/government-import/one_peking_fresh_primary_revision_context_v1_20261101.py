"""Record the fresh primary revision that rejected the legacy exact identity proof.
No identity/physical/installation approval or legacy revision substitution.
"""
from pathlib import Path
import gzip,json,shutil
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from one_peking_installed_hullett_finite_silhouette_identity_20261010 import provider_polygon,canonical
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-one-peking-after-twin-';BATCH=P+'fresh-primary-revision-context-v1-20261101'
def main():
 out=BASE/BATCH;assert not out.exists();failed=BASE/(P+'fresh-primary-finite-identity-diagnostic-v1-20261101');old=BASE/'government-xl-one-peking-current-bound-installed-foreign-inputs-v3-20261010';_,pins=authenticate(old);priorpath=old/'exact-current-primary.json';assert digest(priorpath.read_bytes())==pins[str(priorpath.relative_to(ROOT))];prior=read(priorpath)
 raw=(failed/'exact-current-primary.json').read_bytes();request=read(failed/'exact-current-primary.request.json');assert digest(raw)==request['decodedSHA256'];assert request['url']=='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
 if request['gzipDecoded']:assert gzip.decompress((failed/'exact-current-primary.provider-original.gz').read_bytes())==raw
 else:assert digest(raw)==request['sha256']
 fresh=json.loads(raw);assert not fresh.get('error')and not fresh.get('exceededTransferLimit')and len(fresh['features'])==len(prior['features'])==3
 out.mkdir();refs=[Path(__file__),old/'result.json',priorpath,HERE/'one_peking_current_primary_identity_diagnostic_v1_20261101.py',HERE/'one_peking_installed_hullett_finite_silhouette_identity_20261010.py'];files=[p for p in failed.iterdir()if p.is_file()];refs.extend(files)
 log=Path('/tmp/astra-xl-one-peking-fresh-primary-finite-identity-v1-20261101.log');text=log.read_text();assert "assert digest(canonical(f['geometry']))==geomsha"in text and 'AssertionError'in text;shutil.copyfile(log,out/'failed-worker.log')
 rows=[]
 for f in fresh['features']:
  csuid=f['attributes']['BuildingCSUID'];p=next(p for p in prior['features']if p['attributes']['BuildingCSUID']==csuid);a,b=provider_polygon(p),provider_polygon(f)
  fields=['BuildingCSUID','BuildingID','GeoRefNo','Status','BuildingBlockType','DateCreate'];stable={k:[p['attributes'].get(k),f['attributes'].get(k)]for k in fields};assert all(v[0]==v[1]for v in stable.values())
  rows.append(dict(buildingCSUID=csuid,stableIdentityFields=stable,legacyObjectId=p['attributes']['OBJECTID'],freshObjectId=f['attributes']['OBJECTID'],legacyGeometrySHA256=digest(canonical(p['geometry'])),freshGeometrySHA256=digest(canonical(f['geometry'])),exactGeometryEqual=p['geometry']==f['geometry'],topologyEqual=a.equals(b),legacyAreaM2=a.area,freshAreaM2=b.area,symmetricDifferenceAreaM2=a.symmetric_difference(b).area,hausdorffDistanceM=float(shapely.hausdorff_distance(a,b))))
 result=dict(uids=['landsd/233985:0','landsd/240487:0','landsd/73140:0'],rows=rows,legacyNamedVerifierPassed=False,legacyFailure='fresh primary footprint differs from pinned historical geometry checksum',stableIdentifierFieldsVerified=True,identityAccepted=False,physicalAcceptance=False,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,qualification=__doc__+' Three primary OBJECTIDs and exact footprint geometries changed. Exact current hashes and unchanged stable identity fields are recorded; no old approval is transferred. Fresh full projection/route/native/current-source identity review remains necessary.')
 save(out/'summary.json',result);refs.extend([out/'failed-worker.log']);module('one_peking_primary_revision_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-primary-revision-negative-and-exact-context-no-approval',refs,result)
if __name__=='__main__':main()
