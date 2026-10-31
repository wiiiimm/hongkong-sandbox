"""Compare exact original IFC supports and same-assembly footprint coverage."""
from pathlib import Path
import subprocess, numpy as np, shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ifc-original-assembly-support-v1-20261019';DOC=BASE/BATCH
CAP=BASE/'government-xl-ifc-mall-private-ground-v2-20261019';NEAR=BASE/'government-xl-ifc-mall-neighbours-v3-20261019'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,NEAR]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path
 row=read(CAP/'selection.json.gz')['rows'][0];assert row['uid']=='landsd/64856:0';sources=[row]
 forms={r['building']['uid']:r['building']for r in read(NEAR/'neighbour-inputs.json.gz')['rows']};manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;cat=read(path)
  for entry in cat['models']:
   if entry['uid']not in ['landsd/161250:0','landsd/232441:0']:continue
   asset=path.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];assert cat['rootTranslation']==[-834500,0,816500]
   sources.append(dict(uid=entry['uid'],sourceSHA256=entry['sha256'],source=dict(building=forms[entry['uid']]),candidate=dict(entry=dict(entry,rootTranslation=cat['rootTranslation']),path=str(asset.relative_to(ROOT)))))
   refs.extend([path,asset])
 assert len(sources)==3
 target=forms['way/664250327:0'];assert target['parent']==row['source']['building']['parent']=='relation/13849938'
 assert all('relation/13849938'in r['source']['building']['osmRefs']for r in sources)
 poly=Polygon(target['rings'][0],target['rings'][1:]);projections=[];accounts=[]
 for r in sources:
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];tri=decode_original_world_triangles(raw);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));projections.append(projection)
  accounts.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],faces=len(tri),coveredTargetM2=projection.intersection(poly).area,targetAreaM2=poly.area))
 union=shapely.union_all(projections);missing=poly.difference(union)
 save(DOC/'footprint-context.json',dict(targetUid=target['uid'],sameRecordedAssembly='relation/13849938',sources=accounts,combinedCoverage=1-missing.area/poly.area,uncoveredM2=missing.area,uncoveredGeometry=shapely.to_geojson(missing),installationApproved=False))
 save(DOC/'input.json',dict(sources=sources));tool=HERE/'ifc_original_assembly_support_v1_20261019.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 checks=read(DOC/'support-checks.json.gz')
 for path,h in {**pins,**checks['inputHashes']}.items():assert digest((ROOT/path).read_bytes())==h,path;refs.append(ROOT/path)
 refs.extend([tool,HERE/'exact_packed_world_geometry_20261009.py'])
 module('ifc_assembly_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ifc-exact-original-assembly-support-and-footprint-context',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in sources],supportSummaries=[dict(name=r['name'],passed=r['interface']['passed'],samples=r['interface']['samples'],strictContacts=r['interface']['strictContacts'],unresolved=len(r['interface']['unresolved']))for r in checks['rows']],combinedFootprintCoverage=1-missing.area/poly.area,installationApproved=False))
if __name__=='__main__':main()
