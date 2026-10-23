"""Locate unchanged government tower counterparts for Hanford's retained basic family."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-west-kowloon-bus-foreign-original-discovery-v1-20261024';out=base/batch;assert not out.exists()
    runtime='government-xl-next-repairs-west-kowloon-bus-protected-return-runtime-v1-20261024';_,pins=authenticate(base/runtime);selection=base/runtime/'selection.json.gz';assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))];podium=next(r for r in read(selection)['rows']if r['uid']=='landsd/255415:0')
    scope=base/'government-xl-next-repairs-west-kowloon-bus-protected-full-model-scope-v1-20261024';_,sp=authenticate(scope);formpath=scope/'255415:0-forms.json.gz';assert digest(formpath.read_bytes())==sp[str(formpath.relative_to(ROOT))]
    forms=[r['building']for r in read(formpath)if r['building']['uid']in ['landsd/231056:0','landsd/261098:0','landsd/267223:0','landsd/267327:0','landsd/292042:0']];assert len(forms)==5
    tile=ROOT/'3d-viewer'/podium['source']['tile']
    byuid={b['uid']:b for b in forms};prefixes=['B'+b['buildingCSUID'][:10]+'01'for b in forms];refs=[Path(__file__),base/runtime/'result.json',selection,tile,scope/'result.json',formpath]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        sources=db.execute("SELECT r.cache_key,r.result_sha,i.sheet,m.value FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members n USING(cache_key) JOIN astra_modelling.native_stage_inputs i USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models')m(value) WHERE n.run_id=%s AND (m.value->'candidate'->>'uid'=ANY(%s) OR left(m.value->>'modelId',13)=ANY(%s))",(NATIVE_RUN,sorted(byuid),prefixes)).fetchall()
    names=subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.glb.gz','source-scripts/city','3d-viewer/city/data'],cwd=ROOT,text=True).splitlines();lookup={}
    for name in names:lookup.setdefault(Path(name).name.removesuffix('.glb.gz'),[]).append(name)
    rows=[]
    for key,resultsha,sheet,model in sources:
        uid=(model.get('candidate')or{}).get('uid');matches=[b for b in forms if uid==b['uid']or model['modelId'].startswith('B'+b['buildingCSUID'][:10]+'01')]
        for b in matches:
            asset=model.get('asset',{});sha=asset.get('sha256');verified=[]
            for name in lookup.get(sha,[]):
                path=ROOT/name
                if path.stat().st_size==asset['bytes']and digest(path.read_bytes())==sha:
                    geometry=decode_original_world_triangles(path.read_bytes());verified=[dict(path=name,sha256=sha,completeTriangles=len(geometry),completeOriginalWorldBounds=[geometry.min((0,1)).tolist(),geometry.max((0,1)).tolist()])];refs.append(path);break
            rows.append(dict(uid=b['uid'],currentBasicForm=b,cacheKey=key,resultSHA256=resultsha,sheet=sheet,model=model,verifiedLocalOriginals=verified,installationApproved=False))
    save(out/'source-families.json.gz',dict(rows=rows,requestedForms=forms,podiumSourceSHA256=podium['sourceSHA256']))
    result=dict(uids=sorted(byuid),matchedRecords=len(rows),withVerifiedLocalOriginals=sum(bool(r['verifiedLocalOriginals'])for r in rows),sourceGeometryChanges=0,installationApproved=False,publication=False,sourceIdentityApprovalTransferred=False)
    save(out/'summary.json',result);module('west_foreign_original_discovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'current-overlapping-basic-original-counterpart-discovery',refs,result);print(result,flush=True)
    for r in rows:print(dict(uid=r['uid'],currentBasicBase=r['currentBasicForm']['base'],originalBounds=r['verifiedLocalOriginals'][0]['completeOriginalWorldBounds']if r['verifiedLocalOriginals']else r['model'].get('worldBounds'),local=bool(r['verifiedLocalOriginals'])),flush=True)


if __name__=='__main__':main()
