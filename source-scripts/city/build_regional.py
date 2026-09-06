"""Assemble and independently audit source-backed regional browsing locations.
Run after the three regional generators. Never upgrades a section to reviewed.
The generated module is consumed by the original places module, keeping old URLs.
"""
import json, math, pathlib, re
from pyproj import Transformer
from shapely.geometry import Point, Polygon
from shapely.strtree import STRtree

ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/'3d-viewer/city/data'
GROUPS=('islands','urban','nt')
REGIONS={'lantau','islands','island','kowloon','ntwest','nteast','ntnorth'}
KINDS={'pier','beach','plaza','pitch','apron'}
PROJ=Transformer.from_crs(4326,2326,always_xy=True)

def main():
    packages=[json.loads((OUT/'regional'/f'{key}.json').read_text()) for key in GROUPS]
    expected=set(re.findall(r'^- \[[ xX]\] \*\*(\d+\.\d+)\*\*', (ROOT/'docs/astra-city/SECTION-CHECKLIST.md').read_text(), re.M))
    if len(expected)!=132: raise ValueError('Expected the original 132-section inventory')
    assigned=[]
    for package in packages:
        if package['schemaVersion']!=1: raise ValueError('Unsupported package schema')
        assigned.extend(section['id'] for section in package['sections'])
        if package.get('buildingOverrides'): raise ValueError('Building overrides require explicit source/tile integration before publication')
        for feature in package['surfaces']:
            if feature['kind'] not in KINDS or not feature.get('source'): raise ValueError('Unsupported or unsourced surface')
            rings=feature['rings']
            if any(len(r)<4 or r[0]!=r[-1] for r in rings): raise ValueError('Open surface ring '+feature['id'])
            shape=Polygon(rings[0],rings[1:])
            if not shape.is_valid or shape.area<=0: raise ValueError('Invalid surface '+feature['id'])
    if set(assigned)!=expected or len(assigned)!=len(set(assigned)): raise ValueError('Section ownership mismatch')
    dem=json.loads((OUT/'terrain.json').read_text());manifest=json.loads((OUT/'manifest.json').read_text());dems=[dem]+[json.loads((ROOT/'3d-viewer'/p['url']).read_text()) for p in manifest.get('terrainPatches',[])]
    def ground(x,z):
        dem=dems[0]
        for candidate in dems[1:]:
            g=candidate['meta']['georef'];c=(x+834500-g['bE'])/g['aE'];r=(816500-z-g['bN'])/g['aN']
            if 0<=c<candidate['w']-1 and 0<=r<candidate['h']-1:dem=candidate
        g=dem['meta']['georef'];w,h=dem['w'],dem['h']
        c=(x+834500-g['bE'])/g['aE'];r=(816500-z-g['bN'])/g['aN']
        if not (0<=c<w-1 and 0<=r<h-1): return None,False
        i,j=int(c),int(r);u,v=c-i,r-j
        a,b,d,e=[dem['elev'][idx] for idx in (j*w+i,j*w+i+1,(j+1)*w+i,(j+1)*w+i+1)]
        dry=all(value>0 for value in ((a,b,d) if u+v<=1 else (b,d,e)))
        return (a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)),dry
    manifest=json.loads((OUT/'manifest.json').read_text());blocks=[];heights=[]
    for tile in manifest['tiles']:
        for b in json.loads((ROOT/'3d-viewer'/tile['url']).read_text())['buildings']:
            poly=Polygon(b['rings'][0],b['rings'][1:]).buffer(0)
            if not poly.is_empty: blocks.append(poly);heights.append((b['base']+b['minimum'],b['base']+b['height']))
    tree=STRtree(blocks)
    def audit_spawn(spawn):
        x,z=spawn;y,dry=ground(x,z)
        if y is None or y<=.8 or not dry: return 'Arrival is outside fully dry terrain'
        disc=Point(x,z).buffer(1.2)
        for i in tree.query(disc):
            lo,hi=heights[i]
            if y+1.8>lo and y<hi and blocks[i].intersects(disc): return 'Arrival overlaps building clearance'
        for dx,dz in [(2,0),(-2,0),(0,2),(0,-2)]:
            neighbour,dry=ground(x+dx,z+dz)
            if not dry or neighbour is None or abs(neighbour-y)>=1.5: return 'Arrival is on steep or wet terrain edge'
        return None
    output={};audits=[];covered=set()
    legacy=json.loads((ROOT/'source-scripts/city/destinations.json').read_text())['places']
    for package in packages:
        for entry in package['places']:
            key=entry['id'];section=entry['sectionId'];covered.add(section)
            if key in output or key in legacy: raise ValueError('Duplicate/legacy destination ID '+key)
            if section not in expected or entry['region'] not in REGIONS or not entry.get('source'): raise ValueError('Invalid regional place '+key)
            x,n=PROJ.transform(entry['lon'],entry['lat']);z=816500-n;x-=834500
            terrain_y,dry=ground(x,z)
            if terrain_y is None: raise ValueError('Place outside terrain '+key)
            spawn=entry.get('spawn',[x,z]);assert len(spawn)==2 and all(math.isfinite(v) for v in spawn)
            aerial=bool(entry.get('aerialOnly'));failure=None
            if not aerial:
                if not entry.get('arrivalVerified') or not entry.get('arrivalSource'): failure='No verified mapped public-path arrival supplied'
                else: failure=audit_spawn(spawn)
                if failure: raise ValueError(f'{key}: {failure}')
            p={k:entry[k] for k in ['region','title','zh','sectionId','description','source','lat','lon']}
            p.update(target=entry.get('target',[round(x,1),round(max(35,terrain_y+30),1),round(z,1)]),spawn=[round(v,1) for v in spawn],offset=entry.get('offset',[1150,950,1250]),aerialOnly=aerial)
            if 'arrivalSource' in entry:p['arrivalSource']=entry['arrivalSource']
            if not aerial:
                failure=audit_spawn(p['spawn'])
                if failure:raise ValueError(f'{key}: rounded {failure}')
            output[key]=p
            audits.append({'id':key,'sectionId':section,'aerialOnly':aerial,'arrival':p['spawn'],'arrivalSource':p.get('arrivalSource'),'result':'aerial-only' if aerial else 'dry-public-path-building-clear'})
    if covered!=expected:raise ValueError('Missing section destinations: '+', '.join(sorted(expected-covered)))
    (ROOT/'3d-viewer/city/regional-places.js').write_text('// Generated by source-scripts/city/build_regional.py. Source-based browsing positions, not surveyed locations.\nexport const REGIONAL_PLACES='+json.dumps(output,ensure_ascii=False,indent=2)+';\n')
    report={'schemaVersion':1,'result':'passed','packages':GROUPS,'sections':len(expected),'places':len(output),'walkable':sum(not p['aerialOnly'] for p in output.values()),'aerialOnly':sum(p['aerialOnly'] for p in output.values()),'surfaces':sum(len(p['surfaces']) for p in packages),'checks':['all 132 sections assigned exactly once','valid closed source polygons','original destination IDs preserved','independent dry terrain and 1.2 m building-clearance audit','rounded arrival coordinates audited'],'limits':['Mapped visual surfaces do not change the 70 m terrain or establish surveyed pier elevations.','Arrival checks do not establish a complete walking route or detailed section acceptance.'],'arrivals':audits}
    folder=ROOT/'docs/astra-city/regional';folder.mkdir(parents=True,exist_ok=True);(folder/'arrival-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='arrivals'},ensure_ascii=False))
if __name__=='__main__':main()
