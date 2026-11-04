"""Fail before expensive recovery when a source is already installed or count stale."""
from pathlib import Path
from run import ROOT,read,digest

def require_remaining(count_path, uid, source_sha):
 count=read(count_path)
 manifest=ROOT/'3d-viewer/city/data/manifest.json'
 pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
 assert digest(manifest.read_bytes())==count['manifestSHA256'],'Refresh stale cohort manifest binding'
 assert pointer['snapshotId']==count['snapshotId'],'Refresh stale cohort review snapshot'
 rows=count['rows'];assert len(rows)==len({r['sourceKey']for r in rows})==521
 matches=[r for r in rows if r['uid']==uid and r['indexedSourceSHA256']==source_sha]
 assert len(matches)==1,'Require one exact frozen XL source'
 row=matches[0];assert not row['installedVerified'],'Already installed: do not repeat recovery'
 assert row['runtimeSourceSHA256'] is None,'Source already present: reconcile acceptance before recovery'
 return row

if __name__=='__main__':
 import argparse,json
 ap=argparse.ArgumentParser();ap.add_argument('count');ap.add_argument('uid');ap.add_argument('sha');a=ap.parse_args()
 print(json.dumps(require_remaining(Path(a.count),a.uid,a.sha),sort_keys=True))
