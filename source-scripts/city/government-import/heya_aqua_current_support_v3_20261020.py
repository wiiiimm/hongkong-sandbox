"""Check unchanged Tower2 against the exact currently installed Heya podium."""
from pathlib import Path
import subprocess
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-heya-aqua-current-support-v3-20261020';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-next-twenty-current-terrain-v2-20261020';UID='landsd/184287:0';SUP='landsd/184285:0'
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json');pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']};selection=PRIOR/'selection.json.gz';assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))];row=next(r for r in read(selection)['rows'] if r['uid']==UID)
 refs=[Path(__file__),PRIOR/'result.json',selection];manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);refs.append(manifestpath);catalogue=ROOT/'3d-viewer/city/data/official-models/government-xl-heya-original-podium-installed-20261008/catalogue.json';assert str(catalogue.relative_to(ROOT/'3d-viewer')) in manifest['officialModelCatalogues'];cat=read(catalogue);entry=next(e for e in cat['models'] if e['uid']==SUP);assert entry['publicationApproved'] and entry['sourceIdentityReviewed'];entry={**entry,'rootTranslation':cat['rootTranslation']};asset=catalogue.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];refs.extend([catalogue,asset]);pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';snapshot=read(pointer)['snapshotId'];refs.append(pointer)
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,SUP)).fetchone()==('installed-verified',entry['sha256'])
 forms={}
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for b in read(p)['buildings']:
   if b['uid'] in [UID,SUP]:forms[b['uid']]=(b,tile['url']);refs.append(p)
 assert set(forms)=={UID,SUP};assert forms[UID][0]==row['source']['building'];assert str(forms[SUP][0]['buildingCSUID'])==entry['buildingCSUID'] if 'buildingCSUID' in forms[SUP][0] else True
 support=dict(uid=SUP,sourceSHA256=entry['sha256'],candidate=dict(entry=entry,path=str(asset.relative_to(ROOT))),source=dict(building=forms[SUP][0],tile=forms[SUP][1]));source=ROOT/row['candidate']['path'];assert digest(source.read_bytes())==row['sourceSHA256'];refs.append(source);initial={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in refs}
 save(DOC/'support-inputs.json',dict(sources=[row,support],pairs=[dict(uid=UID,supportUid=SUP)]));tool=HERE/'original-support-closure-interfaces.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 report=read(DOC/'support-checks.json.gz');final=module('heya_original_foundation',HERE/'xl-final-script-pass.py');t=decode_original_world_triangles(source.read_bytes());p=decode_original_world_triangles(asset.read_bytes());b=forms[UID][0];grounddir=BASE/'government-xl-heya-aqua-current-ground-v1-20261020';gr=read(grounddir/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(gr['jobId'],)).fetchone()==('complete',gr)
 gp=HERE/'local'/grounddir.name/'runtime-geometry.json.gz';assert digest(gp.read_bytes())==next(e['sha256'] for e in gr['evidenceRefs'] if e['path']==str(gp.relative_to(ROOT)));refs.extend([grounddir/'result.json',gp]);g=read(gp)['rows'][0];assert g['uid']==UID and g['sourceSHA256']==row['sourceSHA256'];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
 foundation=final.foundation_context(t,np.concatenate([ground,p]),Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',foundation)
 podium_triangles=p.copy()
 for p,h in {**initial,**report['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
 from pool_incident_wall_contacts_v1_20261017 import closest
 targets=[];lo,hi=t.min(1),t.max(1)
 for witness in report['rows'][0]['unresolved']:
  point=np.asarray(witness['position']);possible=np.flatnonzero(np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1));ids=[int(i) for i in possible if np.linalg.norm(closest(point,t[i])-point)<=.001];assert ids;targets.append(dict(witness=witness,incidentFaces=ids))
 ids=sorted({i for x in targets for i in x['incidentFaces']});contacts=exact_finite_contacts(t,ids,podium_triangles,list(range(len(podium_triangles))))
 for x in targets:x['positiveContacts']=[c for c in contacts['contacts'] if c['sourceFaceA'] in x['incidentFaces'] and c['dimension']>0 and c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2]
 save(DOC/'finite-contacts.json.gz',dict(targets=targets,proof=contacts,installationApproved=False));refs.extend([HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'pool_incident_wall_contacts_v1_20261017.py'])
 refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py']);proof=report['rows'][0]['interface'];result=dict(uids=[UID,SUP],sourceSnapshot=snapshot,supportInstalledVerified=True,samples=proof['samples'],strictContacts=proof['strictContacts'],wallIntersections=proof['wallIntersections'],unresolved=len(proof['unresolved']),strictInterfacePassed=proof['passed'],finiteContactWitnesses=sum(bool(x['positiveContacts']) for x in targets),foundation={k:v for k,v in foundation.items() if k!='components'},installationApproved=False,sourceGeometryChanges=0);save(DOC/'summary.json',result);module('heya_current_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-installed-original-podium-contact-and-foundation',list(dict.fromkeys(refs)),result);print(result,flush=True)
if __name__=='__main__':main()
