"""Nominate nearby original podiums for identity-passed sources; no support approval."""
from pathlib import Path
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
SRC=BASE/'government-xl-remaining-forty-original-identity-v2-20261021'
BATCH='government-xl-remaining-forty-support-candidates-v1-20261021';DOC=BASE/BATCH

def main():
 assert not DOC.exists()
 receipt=read(SRC/'result.json');pins={r['path']:r['sha256'] for r in receipt['evidenceRefs']}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 selection=SRC/'selection.json.gz';summary=SRC/'summary.json'
 for p in [selection,summary]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 passed={r['uid']for r in read(summary)['rows']if r['status']=='identity-passed'}
 rows=[r for r in read(selection)['rows']if r['uid']in passed]
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);assert digest(manifestpath.read_bytes())==read(selection)['manifestSHA256']
 refs=[Path(__file__),SRC/'result.json',selection,summary,manifestpath];installed={}
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;catalogue=read(path);refs.append(path)
  for m in catalogue['models']:installed.setdefault(m['uid'],[]).append(dict(catalogue=url,entry=m))
 targets={r['uid']:Polygon(r['source']['building']['rings'][0],r['source']['building']['rings'][1:])for r in rows};found={uid:[]for uid in targets}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];used=False
  for b in read(path)['buildings']:
   if b.get('structureType')!='Podium':continue
   cx,cz=b['centre'];rings=b['rings'];xs=[p[0]for p in rings[0]];zs=[p[1]for p in rings[0]];bounds=(min(xs),min(zs),max(xs),max(zs))
   for row in rows:
    uid=row['uid'];lo,hi=row['native']['model']['worldBounds']
    if b['uid']==uid or bounds[2]<lo[0]-2 or bounds[0]>hi[0]+2 or bounds[3]<lo[2]-2 or bounds[1]>hi[2]+2:continue
    p=Polygon(rings[0],rings[1:]);target=targets[uid]
    if not p.is_valid or not target.is_valid:continue
    distance=p.distance(target)
    if distance>2:continue
    used=True;found[uid].append(dict(uid=b['uid'],name=b.get('name'),source=dict(building=b,tile=tile['url']),distanceM=distance,footprintIntersectionM2=p.intersection(target).area,sameParent=b.get('parent')==row['source']['building'].get('parent'),installed=installed.get(b['uid'],[]),qualification='Nearby GIS podium nomination only; original geometry contact and identity must be checked.'))
  if used:refs.append(path)
 result=dict(uids=sorted(passed),rows=[dict(uid=r['uid'],name=r['source']['building'].get('name'),structureType=r['source']['building']['structureType'],candidates=sorted(found[r['uid']],key=lambda x:(-x['footprintIntersectionM2'],x['distanceM'],x['uid'])))for r in rows],installationApproved=False,supportAccepted=False)
 save(DOC/'nominations.json',result)
 module('forty_support_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-podium-candidate-discovery',refs,result)
 for r in result['rows']:print(r['uid'],r['name'],[(c['uid'],c['name'],bool(c['installed']),round(c['footprintIntersectionM2'],2))for c in r['candidates']],flush=True)
if __name__=='__main__':main()
