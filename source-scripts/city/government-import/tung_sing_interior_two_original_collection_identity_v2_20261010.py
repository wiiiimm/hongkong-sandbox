"""Both exact original versions and current native-run membership, identity only."""
from run import connect,NATIVE_RUN
from tung_sing_interior_current_bound_identity_v2_20261010 import verify_files as tower_verify,native_rows,DOC,verify_receipt
from routed_original_cell_identity import verify_files as ordinary_verify
from run import read
UIDS={'landsd/53800:0','landsd/126434:0'};POLICY='tung-sing-two-original-current-full-identity-v1'
def verify_files(row,context,local):
 assert row['uid'] in UIDS
 receipt=read(DOC/'result.json');verify_receipt(receipt);source=read(DOC/'original-source-lookup.json.gz')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert native_rows(c)==source['rows'];assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 native=next(r for r in source['rows'] if r['model']['modelId']==row['modelId']);assert row['native']['model']==native['model'] and row['native']['resultSha']==native['resultSHA256']
 out=tower_verify(row,context,local) if row['uid']=='landsd/53800:0' else ordinary_verify(row,context,local)
 return {**out,'individualIdentityPolicy':out['policy'],'policy':POLICY,'bothSourceVersionsVerified':True,'individualCurrentNativeRunMembershipVerified':True,'physicalAccepted':False,'installationApproved':False}
