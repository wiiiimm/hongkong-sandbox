"""Original Park Resort lower-face paths at the existing 1 mm membership tolerance."""
from fractions import Fraction as F
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_point_triangle_distance_20261018 import squared_distance
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-park-foundations-contacts-v1-20261018';BATCH='government-xl-olympian-two-park-resort-paths-v1-20261018';DOC=BASE/BATCH;UID='landsd/82096:0'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 inputs=read(PRIOR/'geometry-inputs.json.gz');inputs['rows']=[s for s in inputs['rows']if s['uid']==UID or s['uid']not in inputs['towerUIDs']];inputs['towerUIDs']=[UID];save(DOC/'geometry-inputs.json.gz',inputs)
 checks=read(PRIOR/'support-checks.json.gz');checks['rows']=[x for x in checks['rows']if x['uid']==UID];assert len(checks['rows'])==1;save(DOC/'support-checks.json.gz',checks)
 details=[];limit=F(.001)**2
 for d in checks['rows'][0]['unresolved']:
  faces=[dict(faceIndex=f['faceIndex'],exactSquaredDistance=str(squared_distance(d['position'],f['vertices'])))for f in d['originalSourceFaces']]
  details.append(dict(position=d['position'],faces=faces,exactStartFaces=[f['faceIndex']for f in faces if F(f['exactSquaredDistance'])<=limit]))
 assert len(details)==9;save(DOC/'exact-start-faces.json.gz',dict(rows=[dict(uid=UID,details=details)],squaredTolerance=str(limit),qualification='Existing support-interface 1 mm finite-face membership. Exact rational distances, no snapping or mesh modification.'))
 tool=HERE/'olympian-two-source-face-paths-v4-20261018.mjs';subprocess.run(['node',str(tool),str(DOC),str(DOC/'paths.json.gz'),str(DOC/'exact-start-faces.json.gz')],cwd=ROOT,check=True)
 rows=read(DOC/'paths.json.gz')['rows'];summary=dict(uids=[UID],rows=[{k:v for k,v in row.items()if k!='details'}for row in rows],fullAcceptance=False,newlyInstalled=0);save(DOC/'summary.json',summary)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs=[Path(__file__),tool,HERE/'exact_point_triangle_distance_20261018.py',HERE/'support-contact.mjs',PRIOR/'result.json',*[ROOT/p for p in pins]]
 out=module('park_resort_path_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-park-resort-original-paths-v1',refs,summary);print(out['jobId'],flush=True)
if __name__=='__main__':main()
