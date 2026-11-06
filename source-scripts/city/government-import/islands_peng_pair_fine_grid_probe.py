"""Private 1 m authentic-TIN probe for the unresolved Peng original pair.

Preserves source buildings, terrain domain, 10 m return and parent water mask.
All current acceptance/regression checks must run afresh; no approval is granted.
"""
import argparse
import copy
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path
import numpy as np
from islands_direct_stage import ROOT, HERE, read, save, sha, rel, module
from run import reservations
from source_triangle_windows import TriangleWindows

BATCH = 'government-islands-peng-chau-paired-fine-grid-20261106-v2'
SOURCE = 'government-islands-peng-chau-paired-neighbour-20261106-v1'


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--owned',action='store_true'); a=p.parse_args()
    base=ROOT/'docs/astra-city/government-import'; doc=base/BATCH; local=HERE/'local'/BATCH; stage=HERE/'accepted'/BATCH
    source_doc=base/SOURCE; source_stage=HERE/'accepted'/SOURCE
    selection=read(source_doc/'selection.json.gz'); expected=selection['manifestSHA256']; uids=sorted(r['uid'] for r in selection['rows'])
    assert uids==['landsd/190119:0','landsd/297799:0'] and expected==sha(ROOT/'3d-viewer/city/data/manifest.json')
    lease=local/'reservation.json'
    if not a.owned:
        assert not local.exists() and not doc.exists() and not stage.exists()
        owner='codex-islands-fine-grid-'+str(uuid.uuid4()); deadline=time.monotonic()+14400
        while True:
            assert expected==sha(ROOT/'3d-viewer/city/data/manifest.json') and time.monotonic()<deadline
            claim=reservations.claim(owner,['building:'+u for u in uids]+['terrain:city/data/terrain.json'],batch=BATCH,ttl=3600)
            if claim['ok']:break
            time.sleep(15)
        save(lease,json.loads(json.dumps(claim['reservation'],default=str)))
        subprocess.run([sys.executable,HERE.parent/'shared-modelling/reservations.py','run','--lease-file',lease,'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
        return
    assert reservations.owns(read(lease)) and not doc.exists() and not stage.exists()
    neighbours=read(source_doc/'neighbour-inputs.json.gz'); pins=copy.deepcopy(neighbours['inputHashes'])
    for path,h in pins.items():assert sha(ROOT/path)==h,path
    patch_info=neighbours['patches'][0]; original=read(ROOT/patch_info['path']); assert sha(ROOT/patch_info['path'])==patch_info['sha256']
    old=module('fine_grid_terrain',HERE/'tai-o-terrain-pass.py'); resolve=old.resolve
    parent=read(ROOT/'3d-viewer/city/data/terrain.json'); bounds=resolve.extent(original['coarseCells'],parent)
    step=1; w=round(bounds[2]-bounds[0])+1; h=round(bounds[3]-bounds[1])+1
    assert w*h<=100000 and 2*(w-1)*(h-1)<=25000
    xx,zz=np.meshgrid(np.arange(w)+bounds[0],np.arange(h)+bounds[1]); points=np.c_[xx.ravel(),zz.ravel()]
    values=np.full(len(points),-np.inf)
    for native in original['meta']['source']['nativeSources']:
        gltfs=[]
        for member in native['sourceFiles']:
            path=ROOT/member['path']; assert sha(path)==member['sha256']; pins[rel(path)]=sha(path)
            if path.suffix=='.gltf':gltfs.append(path)
        tri=np.concatenate([resolve.context.triangles(path) for path in gltfs]);tri=TriangleWindows(tri).select(bounds)
        polygons=resolve.shapely.polygons(tri[:,:,[0,2]]); valid=resolve.shapely.area(polygons)>1e-12
        if valid.any():values=np.maximum(values,old.context.shared.samples(points,tri[valid],resolve.shapely.STRtree(polygons[valid])))
    rendered_sampler=old.terrain_helpers.fine.DemSampler(parent,rendered=True); raw_sampler=old.terrain_helpers.fine.DemSampler(parent)
    g=parent['meta']['georef']; cell=abs(g['aE']); elev=[]; rendered=[]; vegetation=[]; boundary=0; water_changes=0
    for i,(x,z) in enumerate(points):
        c=i%w;r=i//w;before=rendered_sampler.ground(x,z);raw=raw_sampler.ground(x,z);alpha=min(1,min(c,r,w-1-c,h-1-r)*step/10)
        if not np.isfinite(values[i]) or raw<=0:alpha=0
        after=float(values[i]*alpha+before*(1-alpha)) if alpha else before
        value=raw if raw<=0 else after
        elev.append(round(value,6));rendered.append(round(after,6))
        cc=min(parent['w']-1,max(0,round((x+834500-g['bE'])/cell)));rr=min(parent['h']-1,max(0,round((z-816500+g['bN'])/cell)))
        vegetation.append(parent['vegetation'][rr*parent['w']+cc]);water_changes+=int(raw<=0 and value>0)
        if c in (0,w-1) or r in (0,h-1):boundary=max(boundary,abs(after-before))
    patch=copy.deepcopy(original);patch.update(id=BATCH.removeprefix('government-'),w=w,h=h,cell=1,elev=elev,renderedElev=rendered,vegetation=vegetation)
    patch['meta']['georef'].update(aE=1,aN=-1,W=w,H=h)
    patch['meta']['source']['policy']='Authentic source TIN barycentric sampling on a bounded 1 m grid; unchanged 10 m parent return and parent water mask. Original building geometry and source placement unchanged. Private probe, fresh acceptance required.'
    assert boundary<1e-5 and water_changes==0; resolve.validate_patch(patch,parent)
    target=stage/'terrain'/(patch['id']+'.json');save(target,patch);pins[rel(target)]=sha(target)
    catalogue=read(source_stage/'catalogue.json')
    for entry in catalogue['models']:
        source=source_stage/entry['asset'];assert sha(source)==entry['sha256'];pins[rel(source)]=sha(source)
        dest=stage/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())
    save(stage/'catalogue.json',catalogue);save(stage/'catalogue-index.json',{'models':len(uids),'catalogues':['catalogue.json']})
    selection['batch']=BATCH;save(doc/'selection.json.gz',selection)
    top=read(source_stage/'plan.json')['topLevelTerrainPatches'][0]
    top.update(source=rel(target),sha256=sha(target),destination='city/data/'+patch['id']+'.json',resolution=1)
    save(stage/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':rel(stage/'catalogue.json'),'destination':f'city/data/official-models/{BATCH}/catalogue.json','terrain':[]}],'topLevelTerrainPatches':[top]})
    for path in (source_doc/'proposal.json',source_doc/'runtime-current/results.json.gz',source_doc/'runtime-current/neon-sync.json',Path(__file__),HERE/'tai-o-terrain-pass.py'):
        pins[rel(path)]=sha(path)
    patch_info.update(path=rel(target),sha256=sha(target))
    save(doc/'neighbour-inputs.json.gz',{**neighbours,'patches':[patch_info],'inputHashes':pins})
    save(doc/'terrain-candidates.json',[{'path':rel(target),'sha256':sha(target)}])
    save(doc/'identity-evidence.json.gz',read(source_doc/'identity-evidence.json.gz'))
    save(doc/'terrain-stage.json',{'sourceUids':uids,'modelsExamined':2,'stagedSourceCandidates':2,'sourceGeometryChanges':0,'gridSpacingMetres':1,'gridNodes':w*h,'terrainArraysChanged':True,'boundaryMaximumDelta':boundary,'waterMaskChanges':water_changes,'priorNegativeEvidence':rel(source_doc/'runtime-current/results.json.gz'),'inputHashes':pins,'publication':False})
    assert reservations.owns(read(lease))
    print({'models':2,'gridNodes':w*h,'sourceGeometryChanges':0,'publication':False},flush=True)


if __name__=='__main__':main()
