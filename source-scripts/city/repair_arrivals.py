"""Repair only failed current arrivals using retained public paths and live data rules.

Run after all regional/terrain/building generators. Source snapshots are read-only.
The existing build_places candidate algorithm is reused; the exact JavaScript
terrain sampler and collision volumes validate every candidate and short walk.
"""
import gzip,hashlib,json,os,pathlib,re,shutil,subprocess
from shapely.geometry import Point
from shapely.strtree import STRtree
from build_places import public_paths,arrival_candidates,apply_arrival_overrides

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'3d-viewer/city/data'
DOC=ROOT/'docs/astra-city/arrival-repairs'

class CityArrivalValidator:
    """Persistent data-only bridge to existing geo.js/building-geometry.js."""
    def __init__(self):
        node=os.environ.get('CITY_NODE') or shutil.which('node')
        if not node:raise RuntimeError('Node.js is required for the shared city collision validator')
        self.process=subprocess.Popen([node,str(HERE/'arrival-validator.mjs')],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    def request(self,op,points=None):
        payload={'op':op}
        if points is not None:payload['points']=points
        self.process.stdin.write(json.dumps(payload)+'\n');self.process.stdin.flush()
        line=self.process.stdout.readline()
        if not line:raise RuntimeError('City arrival validator stopped unexpectedly')
        response=json.loads(line)
        if 'error' in response:raise RuntimeError(response['error'])
        return response['result']
    def audit(self,points):return self.request('audit',points)
    def sample(self,points):return self.request('sample',points)
    def close(self):
        if self.process.poll() is None:self.process.stdin.close();self.process.wait(timeout=30)
    def __enter__(self):return self
    def __exit__(self,*_):self.close()


def retained_paths(manifest):
    files={ROOT/source['file'] for source in manifest['sources']}
    files.update((HERE/'regional').glob('*/snapshots/*.json.gz'))
    files.update((HERE/'regional').glob('*/*-osm.json.gz'))
    records={};dates={};origins={};sources=[]
    for path in sorted(files):
        raw=gzip.decompress(path.read_bytes());data=json.loads(raw)
        stamp=data.get('osm3s',{}).get('timestamp_osm_base','');relative=str(path.relative_to(ROOT))
        sources.append({'file':relative,'snapshot':stamp,'sha256Uncompressed':hashlib.sha256(raw).hexdigest()})
        for element in data['elements']:
            oid=f'{element["type"]}/{element["id"]}'
            if 'highway' not in element.get('tags',{}) and oid not in records:continue
            if stamp>=dates.get(oid,''):
                records[oid]=element;dates[oid]=stamp;origins[oid]=relative
    paths,pathids=public_paths(records)
    return records,origins,sources,paths,pathids,STRtree(paths)


def find_repair(validator,centre,paths,pathids,tree):
    lookup=dict(zip(pathids,paths));candidates=arrival_candidates(centre,paths,pathids,tree)
    for first in range(0,len(candidates),150):
        batch=candidates[first:first+150]
        checks=validator.audit([[p.x,p.y] for _,_,p in batch])
        for (distance,oid,p),check in zip(batch,checks):
            if not check['valid']:continue
            line=lookup[oid];along=line.project(p)
            for direction in (1,-1):
                if not 0<=along+direction*2<=line.length:continue
                steps=[line.interpolate(along+direction*step) for step in (.5,1,1.5,2)]
                points=[[round(s.x,1),round(s.y,1)] for s in steps]
                walk=validator.audit(points)
                if all(s['valid'] for s in walk):
                    return {'spawn':[p.x,p.y],'arrivalSource':'https://www.openstreetmap.org/'+oid,
                        'terrainY':round(check['ground'],3),'movementMetres':round(distance,3),
                        'pathRoundingOffsetMetres':line.distance(p),'shortWalk':{'lengthMetres':2,'sourceDirection':direction,'points':points,'checks':walk},'check':check}
    raise ValueError(f'No dry building-clear public-path arrival and 2 m walk within 1 km of {list(centre.coords)[0]}')


def main():
    manifest=json.loads((OUT/'manifest.json').read_text());DOC.mkdir(parents=True,exist_ok=True)
    with CityArrivalValidator() as validator:
        state=validator.request('places');places=state['places']
        walking=[(id,p) for id,p in places.items() if not p.get('aerialOnly')]
        checks=validator.audit([p['spawn'] for _,p in walking]);failures=[(id,p,check) for (id,p),check in zip(walking,checks) if not check['valid']]
        print(f'{len(places)} destinations; {len(walking)} walking; {len(failures)} failed arrivals',flush=True)
        records,origins,sources,paths,pathids,tree=retained_paths(manifest) if failures else ({},{},[],[],[],None)
        repairs=[]
        for id,place,reason in failures:
            repair=find_repair(validator,Point(place['spawn']),paths,pathids,tree)
            oid=repair['arrivalSource'].removeprefix('https://www.openstreetmap.org/')
            repair.update(id=id,title=place['title'],previousSpawn=place['spawn'],failure=reason,sourceFile=origins[oid],sourceTags=records[oid].get('tags',{}))
            repairs.append(repair);print(id,repair['movementMetres'],'m',oid,flush=True)
        override_path=HERE/'arrival-overrides.json'
        overrides=json.loads(override_path.read_text()) if override_path.exists() else {'schemaVersion':1,'purpose':'Preserve validated arrivals after source geometry expands; only failed existing arrivals are moved.','places':{}}
        for repair in repairs:
            overrides['places'][repair['id']]={k:repair[k] for k in ['spawn','arrivalSource','terrainY','previousSpawn','sourceFile']}
        updated=json.loads(json.dumps(places))
        for repair in repairs:updated[repair['id']].update({k:repair[k] for k in ['spawn','arrivalSource','terrainY']})
        after=validator.audit([p['spawn'] for p in updated.values() if not p.get('aerialOnly')])
        if not all(c['valid'] for c in after):raise ValueError('A repaired or retained arrival failed final validation')
        if repairs:
            # Do not rebuild unaffected camera centres or change existing aerial-only status.
            override_path.write_text(json.dumps(overrides,ensure_ascii=False,indent=2)+'\n')
            config_path=HERE/'destinations.json';config=json.loads(config_path.read_text())
            for repair in repairs:
                if repair['id'] in config['places']:
                    entry=config['places'][repair['id']]
                    if 'target' in entry:entry['spawn']=repair['spawn'];entry['arrivalSource']=repair['arrivalSource'];entry.pop('repairArrival',None)
            config_path.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
            module=ROOT/'3d-viewer/city/places.js';text=module.read_text()
            match=re.search(r'const BASE_PLACES=(\{.*?\});\nexport const PLACES',text,re.S)
            if not match:raise ValueError('Cannot locate existing generated base destinations')
            base=json.loads(match.group(1));apply_arrival_overrides(base)
            text=text[:match.start(1)]+json.dumps(base,ensure_ascii=False,indent=2)+text[match.end(1):];module.write_text(text)
            provenance_path=OUT/'destinations-provenance.json';provenance=json.loads(provenance_path.read_text())
            for repair in repairs:
                if repair['id'] in provenance['places']:
                    provenance['places'][repair['id']].update(arrivalWorld=repair['spawn'],arrivalSource=repair['arrivalSource'])
            provenance_path.write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
            for group in ('islands','urban','nt'):
                package_path=OUT/'regional'/f'{group}.json';package=json.loads(package_path.read_text())
                selected={p['id']:p for p in package['places']};apply_arrival_overrides(selected)
                package_path.write_text(json.dumps(package,ensure_ascii=False,separators=(',',':'))+'\n')
            module=ROOT/'3d-viewer/city/regional-places.js';text=module.read_text()
            match=re.search(r'export const REGIONAL_PLACES=(\{.*\});\s*$',text,re.S)
            if not match:raise ValueError('Cannot locate generated regional destinations')
            regional=json.loads(match.group(1));apply_arrival_overrides(regional)
            text=text[:match.start(1)]+json.dumps(regional,ensure_ascii=False,indent=2)+text[match.end(1):];module.write_text(text)
            # Re-import the published modules in a fresh process, not just the
            # candidate dictionary that already contains the repaired positions.
            with CityArrivalValidator() as published:
                live=published.request('places')['places']
                if set(live)!=set(updated):raise ValueError('Published destination IDs changed during repair')
                if any(live[id]['spawn']!=place['spawn'] for id,place in updated.items()):raise ValueError('Published destination spawn differs from validated repair')
                after=published.audit([live[id]['spawn'] for id,_ in walking])
                if not all(check['valid'] for check in after):raise ValueError('Published arrivals failed fresh-process validation')
        report={'schemaVersion':1,'result':'passed','manifestSha256':state['manifestSha256'],'counts':state['counts'],'destinations':len(places),'walkingArrivals':len(walking),'unchangedAerialOnly':len(places)-len(walking),'repaired':len(repairs),'unchangedWalkingArrivals':len(walking)-len(repairs),'repairs':repairs,'sources':sources,'validator':'Existing city geo.js terrain sampler and BuildingIndex/collisionVolumes, via arrival-validator.mjs; no GPU.',
            'policy':'Actual terrain patches and open-sided/model/foundation collision volumes; fully dry triangle; 1.2 m clearance disc; 1.8 m actor; raw/rendered neighbour rises below 1.5 m at four 2 m offsets. Replacements are within 1 km of the previous arrival and pass a sampled 2 m walk along the retained public path. Existing aerial-only flags are unchanged.',
            'checks':[{'id':id,'spawn':updated[id]['spawn'],**check} for (id,_),check in zip(walking,after)],'limits':['A two-metre source-path check is not a complete route accessibility review.','Unmoved legacy camera presets can retain approximate original arrival provenance; this repair does not claim they are newly surveyed public-path points.']}
        name='repairs.json' if repairs else 'verification.json'
        (DOC/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({k:v for k,v in report.items() if k not in ('repairs','sources','checks')},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
