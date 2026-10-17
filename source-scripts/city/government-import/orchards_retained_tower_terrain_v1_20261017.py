"""Test installed Tower 1's exact original support on the recovered podium."""
from pathlib import Path
import subprocess
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-orchards-retained-tower-terrain-v1-20261017';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH

def main():
 assert not DOC.exists();prior=BASE/'government-xl-orchards-podium-current-checks-v1-20261017';receipt=read(prior/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={e['path']:e['sha256']for e in receipt['evidenceRefs']}
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 podium=read(prior/'selection.json.gz')['rows'][0];manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);matches=[];refs=[Path(__file__),prior/'result.json',prior/'selection.json.gz',manifest]
 for url in m['officialModelCatalogues']:
  cat=ROOT/'3d-viewer'/url;data=read(cat)
  for entry in data['models']:
   if entry['uid']=='landsd/254621:0':matches.append((cat,data,entry))
 assert len(matches)==1;cat,data,entry=matches[0];asset=cat.parent/entry['asset'];raw=asset.read_bytes();assert digest(raw)==entry['sha256']=='7da323731cb425039e534f404f30ea162fd38e49238e6739f22784622ff650f8';tri=decode_original_world_triangles(raw);assert len(tri)==10874
 final=module('orchards_retained_support_forms',HERE/'xl-final-script-pass.py');lo,hi=tri.min((0,1)),tri.max((0,1));form,_,tile=next(x for x in final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])if x[0]['uid']==entry['uid']);row=dict(uid=entry['uid'],sourceSHA256=entry['sha256'],source=dict(building=form,tile=tile),candidate=dict(entry={**entry,'rootTranslation':data['rootTranslation']},path=str(asset.relative_to(ROOT))))
 save(DOC/'support-inputs.json',dict(sources=[row,podium],pairs=[dict(uid=row['uid'],supportUid=podium['uid'])]));tool=HERE/'original-support-closure-interfaces.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True);checks=read(DOC/'support-checks.json.gz')
 for p,h in checks['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 terrain=BASE/'government-xl-orchards-connection-overlap-terrain-v1-20261017';second=module('orchards_retained_terrain_decode',HERE/'xl-second-pass.py');second.LOCAL=HERE/'local'/BATCH;ground=[]
 for sheet in read(terrain/'source-recovery.json')['sheets']:
  folder=ROOT/sheet['cache'];proof=read(folder/'original/download.json');assert proof['directorySHA256']==sheet['directorySHA256'];refs.append(folder/'original/download.json')
  for e in sheet['terrainFiles']:
   p=folder/'terrain'/e['name'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
   if p.suffix=='.gltf':ground.append(second.terrain_triangles(p))
 p=ROOT/podium['candidate']['path'];assert digest(p.read_bytes())==podium['sourceSHA256'];support=decode_original_world_triangles(p.read_bytes());f=final.foundation_context(tri,np.concatenate(ground),Polygon(form['rings'][0],form['rings'][1:]));i=checks['rows'][0]['interface'];summary=dict(uid=row['uid'],supportUid=podium['uid'],strictSupportPassed=i['passed'],samples=i['samples'],strictContacts=i['strictContacts'],unresolved=len(i['unresolved']),wallIntersections=i['wallIntersections'],wholeFoundationPassed=f['completeTerrainTriangles']==f['triangles']and f['fullyBuriedAreaFraction']==0,buriedTriangles=f['fullyBuriedTriangles'],installationApproved=False)
 save(DOC/'foundation.json',f);save(DOC/'summary.json',summary);refs.extend([cat,asset,ROOT/'3d-viewer'/tile,p,terrain/'source-recovery.json',tool,HERE/'xl-final-script-pass.py',HERE/'xl-second-pass.py',HERE/'exact_packed_world_geometry_20261009.py']);out=module('orchards_retained_support_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'installed-original-tower-terrain-only-foundation-v1',list(set(refs)),dict(uids=[row['uid'],podium['uid']],summary=summary,fullAcceptance=False,qualification='Terrain-only foundation excludes original podium meshes to distinguish actual soil burial from authored source-to-source intersections. Previous 17 compound-buried faces and all 12 support negatives remain unresolved evidence; this does not approve their interpretation or installation.'));print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
