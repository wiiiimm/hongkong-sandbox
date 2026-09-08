"""Reusable reserved candidate staging and review harness for the next passes."""
import argparse,json,shutil
from pathlib import Path
import native_terrain as n
p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--uids',required=True);p.add_argument('--terrain');a=p.parse_args();h=Path(__file__).resolve().parent;pin=n.ROOT/'source-scripts/city/landmark-preflight/snapshots/3887f2f23fbad306';selection=n.read(Path(a.uids));uids=set(selection if isinstance(selection,list) else [p['uid'] for p in selection['parts']]);c=n.read(pin/'catalogue.json');c['models']=[m for m in c['models'] if m['uid'] in uids];assert len(c['models'])==len(uids);folder=h/(a.name+'-candidates');folder.mkdir(exist_ok=True)
for m in c['models']:
 assert n.sha(pin/'assets'/m['asset'])==m['sha256'];shutil.copyfile(pin/'assets'/m['asset'],folder/m['asset'])
c['counts']['packedModels']=len(c['models']);(folder/'catalogue.json').write_text(json.dumps(c,indent=2)+'\n');r=n.read(n.ROOT/'docs/astra-city/landmark-preflight/report.json');(h/('selection-'+a.name+'.json')).write_text(json.dumps({'snapshot':'3887f2f23fbad306','parts':[{'uid':p['uid'],'name':p['name'],'landmarks':p['landmarkIds']} for p in r['parts'] if p['uid'] in uids]},indent=2)+'\n')
s=(h/'framing-exact.mjs').read_text().replace('selection-exact.json','selection-'+a.name+'.json').replace('exact-candidates/',a.name+'-candidates/').replace('support-exact-framing','support-'+a.name+'-framing').replace('framing-exact/','framing-'+a.name+'/')
if a.terrain:s=s.replace('docs/astra-city/assembly-support-review/exact-tin.json',a.terrain)
else:
 start=s.index(' const tb=await read(');end=s.index(' await page.goto',start);s=s[:start]+" await page.route('**/city/data/manifest.json',async r=>{const response=await r.fetch(),m=await response.json();m.officialModelCatalogues=[...m.officialModelCatalogues,dest];await r.fulfill({response,json:m});});\n"+s[end:];s=s.replace('terrainUnchanged:false','terrainUnchanged:true')
(h/('framing-'+a.name+'.mjs')).write_text(s)
s=(h/'exact_surface_review.mjs').read_text().replace('exact-candidates/',a.name+'-candidates/').replace('exact-surface-review.json',a.name+'-surface-review.json')
if a.terrain:s=s.replace('docs/astra-city/assembly-support-review/exact-tin.json',a.terrain)
else:
 s=s.replace("import {nativeTerrainSurface}","import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';\nimport {nativeTerrainSurface}");start=s.index('const surfaces=');end=s.index(',lighting=',start);s=s[:start]+"const terrain=read('3d-viewer/city/data/terrain.json');terrain.patches=mf.terrainPatches.map(p=>read('3d-viewer/'+p.url));const terrainSampler=makeTerrainSampler(terrain);const surfaces=[{data:{meta:{targetUids:cat.models.map(m=>m.uid)}},surface:terrainSampler}]"+s[end:]
(h/(a.name+'_surface_review.mjs')).write_text(s)
print('Prepared',a.name,len(uids))
