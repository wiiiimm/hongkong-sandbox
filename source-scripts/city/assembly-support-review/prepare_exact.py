import json,shutil
from pathlib import Path
import native_terrain as n
h=Path(__file__).resolve().parent;p=n.ROOT/'source-scripts/city/landmark-preflight/snapshots/3887f2f23fbad306';c=n.read(p/'catalogue.json');uids={'landsd/103538:0','landsd/176291:0','landsd/176748:0','landsd/257313:0'};c['models']=[m for m in c['models'] if m['uid'] in uids];d=h/'exact-candidates';d.mkdir(exist_ok=True)
for m in c['models']:
 assert n.sha(p/'assets'/m['asset'])==m['sha256'];shutil.copyfile(p/'assets'/m['asset'],d/m['asset'])
c['counts']['packedModels']=len(c['models']);(d/'catalogue.json').write_text(json.dumps(c,indent=2)+'\n');r=n.read(n.ROOT/'docs/astra-city/landmark-preflight/report.json');(h/'selection-exact.json').write_text(json.dumps({'snapshot':'3887f2f23fbad306','parts':[{'uid':m['uid'],'name':m['name'],'landmarks':m['landmarkIds']} for m in r['parts'] if m['uid'] in uids]},indent=2)+'\n')
s=(h/'framing-terrain.mjs').read_text().replace('selection-terrain.json','selection-exact.json').replace("approved-terrain/","exact-candidates/").replace('support-terrain-framing','support-exact-framing').replace("framing-terrain/","framing-exact/")
a=s.index(" const tb=await read(");b=s.index(" await page.goto",a)
s=s[:a]+''' const tb=await read('docs/astra-city/assembly-support-review/exact-tin.json'),rootPatches=[];
 for(const p of tb.patches){const child=await read(p.path);if(p.parentTerrainURL==='city/data/terrain.json'){const url='city/data/'+child.id+'.json';rootPatches.push({url,resolution:1,area:'Native TIN review'});await page.route('**/'+url,r=>r.fulfill({json:child}));}else{const data=await read('3d-viewer/'+p.parentTerrainURL);data.patches=[...(data.patches||[]),child];await page.route('**/'+p.parentTerrainURL,r=>r.fulfill({json:data}));}}
 await page.route('**/city/data/manifest.json',async r=>{const response=await r.fetch(),m=await response.json();m.officialModelCatalogues=[...m.officialModelCatalogues,dest];m.terrainPatches.push(...rootPatches);await r.fulfill({response,json:m});});
'''+s[b:];(h/'framing-exact.mjs').write_text(s)
