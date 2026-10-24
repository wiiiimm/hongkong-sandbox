"""Locate unchanged government tower counterparts for Sung Fung and its overlapping current podium."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-sung-fung-lee-man-original-family-discovery-v1-20261024';out=base/batch;assert not out.exists()
    runtime='government-xl-next-repairs-beverly-sung-fung-runtime-v1-20261023';_,pins=authenticate(base/runtime);selection=base/runtime/'selection.json.gz';assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))];podium=next(r for r in read(selection)['rows']if r['uid']=='landsd/79098:0')
    tile=ROOT/'3d-viewer'/podium['source']['tile'];assert digest(tile.read_bytes())==pins[str(tile.relative_to(ROOT))];forms=[b for b in read(tile)['buildings']if b['uid']in ['landsd/79098:0','landsd/45779:0','landsd/47160:0']];assert len(forms)==3
    byuid={b['uid']:b for b in forms};prefixes=['B'+b['buildingCSUID'][:10]+('01' if b['structureType']=='Tower' else '02')for b in forms];refs=[Path(__file__),base/runtime/'result.json',selection,tile]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        sources=db.execute("SELECT r.cache_key,r.result_sha,i.sheet,m.value FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members n USING(cache_key) JOIN astra_modelling.native_stage_inputs i USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models')m(value) WHERE n.run_id=%s AND (m.value->'candidate'->>'uid'=ANY(%s) OR left(m.value->>'modelId',13)=ANY(%s))",(NATIVE_RUN,sorted(byuid),prefixes)).fetchall()
    names=subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.glb.gz','source-scripts/city','3d-viewer/city/data'],cwd=ROOT,text=True).splitlines();lookup={}
    for name in names:lookup.setdefault(Path(name).name.removesuffix('.glb.gz'),[]).append(name)
    rows=[]
    for key,resultsha,sheet,model in sources:
        uid=(model.get('candidate')or{}).get('uid');matches=[b for b in forms if uid==b['uid']or model['modelId'].startswith('B'+b['buildingCSUID'][:10]+('01' if b['structureType']=='Tower' else '02'))]
        for b in matches:
            asset=model.get('asset',{});sha=asset.get('sha256');verified=[]
            for name in lookup.get(sha,[]):
                path=ROOT/name
                if path.stat().st_size==asset['bytes']and digest(path.read_bytes())==sha:
                    geometry=decode_original_world_triangles(path.read_bytes());verified=[dict(path=name,sha256=sha,completeTriangles=len(geometry),completeOriginalWorldBounds=[geometry.min((0,1)).tolist(),geometry.max((0,1)).tolist()])];refs.append(path);break
            rows.append(dict(uid=b['uid'],currentBasicForm=b,cacheKey=key,resultSHA256=resultsha,sheet=sheet,model=model,verifiedLocalOriginals=verified,installationApproved=False))
    save(out/'source-families.json.gz',dict(rows=rows,requestedForms=forms,podiumSourceSHA256=podium['sourceSHA256']))
    result=dict(uids=sorted(byuid),matchedRecords=len(rows),withVerifiedLocalOriginals=sum(bool(r['verifiedLocalOriginals'])for r in rows),sourceGeometryChanges=0,installationApproved=False,publication=False,sourceIdentityApprovalTransferred=False)
    save(out/'summary.json',result);module('hanford_family_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'current-basic-family-matching-original-source-discovery',refs,result);print(result,flush=True)
    for r in rows:print(dict(uid=r['uid'],currentBasicBase=r['currentBasicForm']['base'],originalBounds=r['verifiedLocalOriginals'][0]['completeOriginalWorldBounds']if r['verifiedLocalOriginals']else r['model'].get('worldBounds'),local=bool(r['verifiedLocalOriginals'])),flush=True)


if __name__=='__main__':main()
