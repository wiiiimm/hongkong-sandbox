"""Read-only provider revision check; no model or publication changes."""
import hashlib
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from run import ROOT,HERE,read,save
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-langham-provider-revision-v1-20261017'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
CACHE=HERE/'local/government-xl-50-second-20260913/sheets/11-NW-19B'
def main():
 assert not DOC.exists()
 receipt=read(CACHE/'original/download.json'); old=read(CACHE/'directory/result.json')
 start=old['centralDirectoryOffset']; size=old['centralDirectoryBytes']
 req=urllib.request.Request(receipt['source'],headers={'Range':f'bytes={start}-{start+size-1}','Accept-Encoding':'identity'})
 with urllib.request.urlopen(req,timeout=45) as response:
  assert response.status==206, 'Provider ignored range; do not download entire archive'
  assert response.headers['Content-Range']==f'bytes {start}-{start+size-1}/{old["archiveBytes"]}'
  data=response.read(size+1); assert len(data)==size
  headers={k:response.headers.get(k) for k in ['ETag','Last-Modified','Content-Range']}
 sha=hashlib.sha256(data).hexdigest()
 summary=dict(checkedAt=datetime.now(timezone.utc).isoformat(),sheet=old['sheet'],headers=headers,centralDirectoryBytes=len(data),directorySHA256=sha,previousDirectorySHA256=old['directorySHA256'],directoryUnchanged=sha==old['directorySHA256'],etagUnchanged=headers['ETag']==old['etag'],installationApproved=False,qualification='Matching central directory and ETag provide no evidence of a new provider revision. This is not a bytewise comparison of the complete remote archive or proof of permanent unavailability.')
 DOC.mkdir(parents=True); (DOC/'central-directory.bin').write_bytes(data); save(DOC/'provider-check.json',summary)
 result=module('langham_provider_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'provider-original-revision-check-v1',[Path(__file__),CACHE/'original/download.json',CACHE/'directory/result.json'],dict(uids=['landsd/79318:0'],summary=summary,fullAcceptance=False,nextStep='Keep the exact original-pair gap on hold; current provider directory is unchanged. Investigate a distinct source or another actionable model rather than retry unchanged geometry.'))
 print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
