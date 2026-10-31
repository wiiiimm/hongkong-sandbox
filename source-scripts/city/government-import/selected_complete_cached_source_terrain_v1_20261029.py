"""Find byte-verified original TINs on every indexed sheet a model crosses.

Unlike singleton native-cache terrain lookup, adjacent pinned sheets are included.
No downloads, model/terrain edits, identity approval or publication are performed.
"""
import argparse,subprocess
from collections import defaultdict
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from terrain_source_preflight import SourceSheetIndex

def main():
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--capture',required=True);p.add_argument('--uid',action='append',required=True);a=p.parse_args()
    assert a.batch.startswith('government-xl-')and '/'not in a.batch and 0<len(a.uid)==len(set(a.uid))<=20
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();_,pins=authenticate(base/a.capture);refs=[Path(__file__),base/a.capture/'result.json']
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selected=take(base/a.capture/'selection.json.gz')['rows'];rows=[r for r in selected if r['uid']in a.uid];assert len(rows)==len(a.uid)
    runtime={r['uid']:r for r in take(HERE/'local'/a.capture/'runtime-geometry.json.gz')['rows']}
    indexpath=HERE.parent/'landmark-acquisition/index.json';index=SourceSheetIndex(read(indexpath));refs.append(indexpath)
    wanted={r['uid']:index.covering_sheets(r['native']['model']['worldBounds'])for r in rows};sheets=sorted({s['sheet']for v in wanted.values()for s in v})
    with connect() as db:
        db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        records=db.execute('''SELECT i.sheet,i.cache_key,r.result_sha,r.result->'terrain'
          FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key)
          JOIN astra_modelling.native_stage_members m USING(cache_key)
          WHERE m.run_id=%s AND i.sheet=ANY(%s) ORDER BY i.sheet,i.cache_key''',(NATIVE_RUN,sheets)).fetchall()
    bysheet=defaultdict(list)
    for sheet,key,sha,terrain in records:bysheet[sheet].append(dict(sheet=sheet,cacheKey=key,resultSHA256=sha,terrain=terrain or []))
    byname=defaultdict(list)
    for name in subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.gltf','source-scripts/city'],cwd=ROOT,text=True).splitlines():byname[Path(name).name].append(ROOT/name)
    verified={};missing={}
    for sheet in sheets:
        entries={}
        for record in bysheet[sheet]:
            for t in record['terrain']:
                hashes=t.get('sourceHashes');entry=t.get('sourceEntry')
                if hashes and entry:entries[(entry,tuple(sorted(hashes.items())))]=t
        found=[];unavailable=[]
        for (entry,hashitems),t in entries.items():
            candidates=[]
            for path in byname[Path(entry).name]:
                members=[path.parent/Path(n).name for n,_ in hashitems]
                if all(f.exists()and digest(f.read_bytes())==h for f,(_,h)in zip(members,hashitems)):candidates.append((path,members))
            if candidates:
                path,members=min(candidates,key=lambda v:str(v[0]));found.append(path);refs.extend(members)
            else:unavailable.append(dict(sourceEntry=entry,sourceHashes=dict(hashitems)))
        verified[sheet]=list(dict.fromkeys(found));missing[sheet]=unavailable or ([]if entries else [dict(reason='no-pinned-original-terrain-record')])
    decoder=module('complete_cached_ground_decoder',HERE/'xl-second-pass.py');final=module('complete_cached_foundation',HERE/'xl-final-script-pass.py');results=[]
    for row in rows:
        uid=row['uid'];paths=list(dict.fromkeys(path for s in wanted[uid]for path in verified[s['sheet']]));absent=[dict(sheet=s['sheet'],records=missing[s['sheet']])for s in wanted[uid]if missing[s['sheet']]]
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);g=runtime[uid];assert g['sourceSHA256']==row['sourceSHA256'];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
        result=dict(uid=uid,sourceSHA256=row['sourceSHA256'],indexedSheets=wanted[uid],missingOriginalTerrain=absent,sourceTerrainPaths=[str(path.relative_to(ROOT))for path in paths],installationApproved=False)
        if paths:
            ground=np.concatenate([decoder.terrain_triangles(path)for path in paths]);lo,hi=tri.min((0,1)),tri.max((0,1));keep=(ground[:,:,0].max(1)>=lo[0]-10)&(ground[:,:,0].min(1)<=hi[0]+10)&(ground[:,:,2].max(1)>=lo[2]-10)&(ground[:,:,2].min(1)<=hi[2]+10);ground=ground[keep]
            projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));domain=shapely.union_all(shapely.polygons(ground[:,:,[0,2]]));result['uncoveredSourceProjectionAreaM2']=float(projection.difference(domain).area)
            b=row['source']['building'];result['originalTerrainFoundation']=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]))
        result['status']='complete-indexed-cached-terrain-checked'if paths and not absent else 'incomplete-indexed-cached-terrain'
        save(out/(uid.split('/')[1]+'.json'),result);results.append(result);print(dict(uid=uid,status=result['status'],cachedTerrainFiles=len(paths),missingSheets=[r['sheet']for r in absent],missingProjectionAreaM2=result.get('uncoveredSourceProjectionAreaM2')),flush=True)
    save(out/'pinned-sheet-records.json',dict(nativeRun=NATIVE_RUN,rows=[r for records in bysheet.values()for r in records]))
    result=dict(uids=a.uid,rows=results,sourceGeometryChanges=0,installationApproved=False,qualification='All indexed sheets intersecting each original model are searched in the pinned native run. Existing GLTF and buffer bytes must match the recorded source hashes exactly. Missing cached records remain explicit. Source terrain coverage/foundation diagnostics only; no acquisition, edits, acceptance or publication.')
    save(out/'summary.json',result);refs.extend([indexpath,HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',HERE/'terrain_source_preflight.py'])
    module('complete_cached_source_terrain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-indexed-adjacent-cached-original-terrain-diagnostic',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
