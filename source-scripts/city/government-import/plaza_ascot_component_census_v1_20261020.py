"""Bind original same-complex and flagged neighbour components without approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-component-census-v1-20261020';DOC=BASE/BATCH;ID=BASE/'government-xl-plaza-ascot-identity-v1-20261020';SRC=BASE/'government-xl-next-twenty-current-terrain-v2-20261020';UID='landsd/258411:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [ID,SRC]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  assert digest(p.read_bytes())==pins[d][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 identity=take(ID,ID/'identity.json');row=next(r for r in take(SRC,SRC/'selection.json.gz')['rows']if r['uid']==UID)
 tile=ROOT/'3d-viewer'/row['source']['tile'];forms=read(tile)['buildings'];assert next(b for b in forms if b['uid']==UID)==row['source']['building'];refs.append(tile)
 nominated={b['uid']:b for b in forms if b.get('parent')==row['source']['building']['parent']};flagged={f['uid'] for f in identity['freshCurrentIdentity']['intersectingForms']if not f['sameParent']}
 nominated.update({b['uid']:b for b in forms if b['uid']in flagged})
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');sha,registry=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone();assert sha==row['native']['resultSha']
 matches=[]
 for model in registry['models']:
  uids=set()
  for candidate in model.get('matching',{}).get('officialCandidates',[]):
   for uid,b in nominated.items():
    if candidate.get('objectId')==b.get('objectId')and candidate.get('buildingCSUID')==b.get('buildingCSUID'):uids.add(uid)
  if uids:matches.append(dict(model=model,exactViewerUids=sorted(uids)))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest);installed={}
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;cat=read(p)
  for m in cat['models']:
   if m['uid']in nominated:
    refs.append(p);installed[m['uid']]=dict(catalogue=url,sha256=m['sha256'],entry=m)
 save(DOC/'registry.json.gz',dict(cacheKey=row['native']['cacheKey'],resultSHA256=sha,result=registry))
 save(DOC/'census.json',dict(sourceForms=nominated,flaggedUnrelatedUids=sorted(flagged),nominations=matches,installed=installed,identity=identity['freshCurrentIdentity']))
 summary=dict(uids=[UID],nominatedForms=len(nominated),governmentSourceRecords=len(matches),exactMatchedForms=len({u for r in matches for u in r['exactViewerUids']}),missing=sorted(set(nominated)-{u for r in matches for u in r['exactViewerUids']}),alreadyInstalledUids=sorted(installed),installationApproved=False,sourceGeometryChanges=0)
 save(DOC/'summary.json',summary);module('ascot_census_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-component-and-flagged-neighbour-census',list(dict.fromkeys(refs)),summary);print(summary,flush=True)
if __name__=='__main__':main()
