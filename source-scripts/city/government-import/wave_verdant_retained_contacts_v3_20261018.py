"""Complete retained-actor bounds and exact finite contacts; source contacts are not failures by themselves."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from wave_verdant_assembly_four_worlds_v1_20261017 import UIDS as OLD_UIDS
UIDS=OLD_UIDS+["landsd/194544:0"]
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-verdant-retained-contacts-v3-20261018';DOC=BASE/BATCH
NAMES=['government-xl-wave-verdant-joint-source-records-v1-20261017','government-xl-wave-multicore-private-basic-estimates-v4-20261017','government-xl-wave-multicore-retained-basic-v4-20261017','government-xl-wave-actual-render-attributes-v1-20261017','government-xl-wave-verdant-actual-render-attributes-v1-20261017','government-xl-wave-verdant-block2-render-attributes-v1-20261017']
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES+['government-xl-wave-verdant-retained-contacts-v1-20261017','government-xl-verdant194544-four-world-v1-20261018','government-xl-wave-verdant-current-ground-equivalence-v5-20261018']:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    pins[(e['path'],e['sha256'])]=e['sha256']
 archive=read(BASE/'government-xl-apex227942-original-installed-v1-20261018/result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(archive['jobId'],)).fetchone()==('complete',archive)
 mapping={(x['originalPath'],x['originalSHA256']):x['savedHistoricalBytes'] for x in archive['historicalMutableByteSnapshots']}
 for (p,h) in pins:
  q=ROOT/p
  if digest(q.read_bytes())!=h:
   e=mapping[(p,h)];assert e['sha256']==h;q=ROOT/e['path']
  assert digest(q.read_bytes())==h,p;refs.append(q)
 refs.append(BASE/'government-xl-apex227942-original-installed-v1-20261018/result.json')
 sources={r['uid']:r for r in read(BASE/'government-xl-wave-all-original-support-distance-v1-20261017/support-inputs.json')['sources']};sources.update({r['uid']:r for r in read(BASE/'government-xl-wave-verdant-podium-support-v1-20261017/support-inputs.json')['sources']});sources.update({r['uid']:r for r in read(BASE/'government-xl-wave-verdant-block2-original-recovery-v1-20261017/selection.json.gz')['rows']});attrs={r['uid']:r for n in NAMES[3:]for r in read(BASE/n/'attributes.json.gz')['rows']}
 sources.update({r['uid']:r for r in read(BASE/'government-xl-wave-verdant-194544-original-recovery-v1-20261017/selection.json.gz')['rows']});attrs.update({r['uid']:r for r in read(BASE/'government-xl-verdant194544-four-world-v1-20261018/attributes.json.gz')['rows']})
 oldrows={(r['mode'],r['uid'],r['foreignUid']):r for r in read(BASE/'government-xl-wave-verdant-retained-contacts-v1-20261017/contacts.json.gz')['rows']}
 basic=read(BASE/'government-xl-wave-verdant-multicore-ground-capture-v4-20261017/basic-actors.json.gz')['rows'];updates={r['uid']:r for r in read(BASE/NAMES[1]/'geometry.json.gz')['rows']};retained={}
 for row in basic:
  uid=row['uid']
  if uid in UIDS:continue
  r=updates.get(uid,row)
  if uid in updates:assert r['sourceBefore']==row['building']
  p=np.asarray(r['position']).reshape(-1,3);index=np.asarray(r['index']).reshape(-1,3);t=p[index];retained[uid]=dict(triangles=t,bounds=np.array([p.min(0),p.max(0)]),sha=digest(t.tobytes()),privateBasicCorrection=uid in updates)
 assert read(BASE/'government-xl-wave-verdant-current-ground-capture-v5-20261018/basic-actors.json.gz')['rows']==basic
 assert len(retained)==39 and set(updates)<=set(retained);keys={'literal':'completeLiteralWorldPosition','left':'completeExplicitLeftAssociatedFloat32WorldPosition','balanced':'completeExplicitBalancedFloat32WorldPosition'};worlds={};bounds={}
 for uid in UIDS:
  r=sources[uid];raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];worlds[uid]={'original':decode_original_world_triangles(raw)};bounds[uid]={'original':np.array(packed_world_bounds(raw)['originalWholeSourceBounds'])}
  for mode,key in keys.items():
   p=np.array(attrs[uid][key]).reshape(-1,3);worlds[uid][mode]=p[np.array(attrs[uid]['completeOriginalIndex']).reshape(-1,3)];bounds[uid][mode]=np.array([p.min(0),p.max(0)])
 DOC.mkdir();cache={};rows=[]
 for mode in ['original','literal','left','balanced']:
  for uid in UIDS:
   t=worlds[uid][mode];b=bounds[uid][mode];sha=digest(t.tobytes());assert len(t)==sources[uid]['native']['model']['triangles']
   for foreign,r in retained.items():
    q=r['bounds'];disjoint=bool(np.any(b[1]<q[0])or np.any(q[1]<b[0]));row=dict(mode=mode,uid=uid,foreignUid=foreign,sourceFaces=len(t),foreignFaces=len(r['triangles']),sourceWholeUnusedBounds=b.tolist(),foreignWholeUnusedBounds=q.tolist(),completeBoundsDisjoint=disjoint,sourceGeometrySHA256=sha,foreignGeometrySHA256=r['sha'],privateBasicCorrection=r['privateBasicCorrection'])
    old=oldrows.get((mode,uid,foreign))
    if old is not None:
     assert all(old[k]==v for k,v in row.items()),(mode,uid,foreign)
     row.update({k:old[k] for k in ['proofPath','finiteContacts','trianglePairsTested','solidContainmentNotCertified'] if k in old});row['reusedExactGeometry']=True;rows.append(row);continue
    if not disjoint:
     key=sha+'-'+r['sha']
     if key not in cache:
      proof=exact_finite_contacts(t,list(range(len(t))),r['triangles'],list(range(len(r['triangles']))));assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0;p=DOC/'pairs'/(key+'.json.gz');save(p,proof);cache[key]=(str(p.relative_to(ROOT)),len(proof['contacts']),proof['trianglePairsTested'])
     path,count,tested=cache[key];row.update(proofPath=path,finiteContacts=count,trianglePairsTested=tested,solidContainmentNotCertified=True);print(dict(mode=mode,uid=uid,foreignUid=foreign,finiteContacts=count),flush=True)
    rows.append(row)
   save(DOC/'partial-summary.json',dict(completedSourceModePairs=len(rows)//len(retained),rows=rows,fullAcceptance=False))
 assert len(rows)==4*len(UIDS)*len(retained);summary=dict(sourceModels=len(UIDS),retainedBasicActors=len(retained),actorModePairs=len(rows),boundsDisjoint=sum(r['completeBoundsDisjoint']for r in rows),overlappingActorModePairs=sum(not r['completeBoundsDisjoint']for r in rows),contactActorModePairs=sum(r.get('finiteContacts',0)>0 for r in rows),freshExactGeometryPairs=len(cache),reusedActorModePairs=sum(r.get('reusedExactGeometry',False)for r in rows),fullAcceptance=False);save(DOC/'summary.json',summary);save(DOC/'contacts.json.gz',dict(rows=rows,qualification='Every whole actor bound includes unused vertices. All finite source faces, including degenerate authored primitives, retained for nominated pairs. Complete-bound separation certifies pair separation. Surface contact absence alone never certifies solid clearance; overlaps require source-context/containment review. Authored contacts alone are not placement failures.'))
 refs.extend([HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_packed_world_bounds_v3_20261010.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','wave_verdant_assembly_four_worlds_v1_20261017.py']]);out=module('wave_retained_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'nine-original-thirty-nine-retained-actor-four-mode-finite-contacts-v3',list(set(refs)),dict(uids=UIDS+list(retained),summary=summary,fullAcceptance=False,newlyInstalled=0));print(summary,flush=True);print(out['jobId'],flush=True)
if __name__=='__main__':main()
