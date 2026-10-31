"""Complete unchanged BASIC body against actual old-parent and proposed ground.
Read-only negative census; no source-owned podium mesh supplies support.
"""
from pathlib import Path
from fractions import Fraction
import importlib.util,json,math
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from original_ordinary_rim_accounting_20261009 import verify as ordinary_rim
BATCH='government-xl-lippo-actual-basic-whole-existing-parent-ground-comparison-v2-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
BODY=DOC.parent/'government-xl-lippo-current-basic-podium-support-inputs-v1-20261011'
OLD=DOC.parent/'government-xl-lippo-upper-originals-actual-basic-podium-support-diagnostic-v1-20261011'
PARENT=ROOT/'3d-viewer/city/data/terrain-government-xl-caine-road-original-pair-installed-v2-20261010.json'
PARENT_SHA='3a56cb25625313f57e16f8a2059942a15bfd94f6556d729672cdb394e1bf461f'
CELLS=[531,0,559,25]

def finite_height_sampler(faces):
    polygons=shapely.polygons(faces[:,:,[0,2]])
    valid=shapely.area(polygons)>0
    assert valid.all(),'Every captured whole root-grid facet must have positive projection'
    tree=shapely.STRtree(polygons);rational={}
    def sample(x,z):
        qx,qz=Fraction(float(x)),Fraction(float(z));values=[]
        for k in tree.query(shapely.Point(x,z)):
            k=int(k)
            if k not in rational:rational[k]=[[Fraction(float(v)) for v in p] for p in faces[k]]
            a,b,c=rational[k];den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
            assert den
            u=((b[2]-c[2])*(qx-c[0])+(c[0]-b[0])*(qz-c[2]))/den
            v=((c[2]-a[2])*(qx-c[0])+(a[0]-c[0])*(qz-c[2]))/den;w=1-u-v
            if min(u,v,w)>=0:values.append(u*a[1]+v*b[1]+w*c[1])
        assert values,'No actual finite parent triangle at complete BASIC sample'
        return float(max(values))
    return sample

def main():
    assert not DOC.exists()
    # BODY and OLD are immutable completed source snapshots. This distinct
    # producer records historical maths, never substitutes stale current pins.
    from run import connect
    for folder in [BODY,OLD]:
        r=read(folder/'result.json')
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
    body=read(BODY/'complete-current-basic-podium-geometry.json.gz')
    captured_input_drift={path:dict(capturedSHA256=pin,observedSHA256=digest((ROOT/path).read_bytes())) for path,pin in body['inputHashes'].items() if digest((ROOT/path).read_bytes())!=pin}
    assert not body['originalGovernmentPodiumUsedAsSupport']
    raw=body['completeCurrentRendererBody'];p=np.array(raw['position'],dtype='<f8').reshape(-1,3);idx=np.array(raw['index'],dtype=np.uint32).reshape(-1,3)
    assert np.array_equal(p,p.astype('<f4').astype('<f8')) and len(idx)==284
    old=read(OLD/'diagnostic.json.gz');assert old['completeActualBasicFaces']==284 and old['actualBasicWorldSHA256']==digest(p[idx].tobytes())
    assert len(old['completeBasicRootProofs'])==1
    proof=old['completeBasicRootProofs'][0];assert len(proof['completeSamples'])==4332
    parent=read(PARENT);assert digest(PARENT.read_bytes())==PARENT_SHA and not parent.get('nativeMesh')
    g=parent['meta']['georef'];w,h=parent['w'],parent['h'];origin=[834500,816500]
    def xz(c,r):return [g['aE']*c+g['bE']-origin[0],origin[1]-(g['aN']*r+g['bN'])]
    def cellbox(cells):
        a=xz(cells[0],cells[1]);b=xz(cells[2],cells[3]);return shapely.box(min(a[0],b[0]),min(a[1],b[1]),max(a[0],b[0]),max(a[1],b[1]))
    actual_bounds=shapely.box(p[:,0].min(),p[:,2].min(),p[:,0].max(),p[:,2].max())
    candidate_bounds=cellbox(CELLS);assert candidate_bounds.covers(actual_bounds)
    children=[]
    for child in parent['patches']:
        b=cellbox(child['coarseCells']);assert b.disjoint(actual_bounds),'Actual BASIC projection reaches a current child: capture that child too'
        children.append(dict(id=child['id'],coarseCells=child['coarseCells'],wholeBasicBoundsDisjoint=True,childSHA256=digest(json.dumps(child,sort_keys=True,separators=(',',':')).encode())))
    c0,c1=sorted((actual_bounds.bounds[0]+origin[0]-g['bE'],actual_bounds.bounds[2]+origin[0]-g['bE']))
    c0,c1=c0/g['aE'],c1/g['aE'];r0,r1=sorted(((origin[1]-actual_bounds.bounds[1]-g['bN'])/g['aN'],(origin[1]-actual_bounds.bounds[3]-g['bN'])/g['aN']))
    cells=[max(0,math.floor(c0)),max(0,math.floor(r0)),min(w-1,math.ceil(c1)),min(h-1,math.ceil(r1))]
    terrain=[];cell_ids=[]
    for r in range(cells[1],cells[3]):
        for c in range(cells[0],cells[2]):
            verts=[]
            for cc,rr in ((c,r),(c+1,r),(c,r+1),(c+1,r+1)):
                k=rr*w+cc;override=parent['renderedElev'][k]
                e=parent['elev'][k]
                value=override if isinstance(override,(int,float)) and math.isfinite(override) else max(1.2,e) if e>0 else -4
                assert math.isfinite(value)
                x,z=xz(cc,rr);verts.append([x,value,z])
            for indices in ((0,1,2),(1,3,2)):
                terrain.append([verts[k] for k in indices]);cell_ids.append([c,r,list(indices)])
    terrain=np.array(terrain,dtype='<f8');ground=finite_height_sampler(terrain)
    sp=importlib.util.spec_from_file_location('lippo_existing_fine_sampler',ROOT/'source-scripts/city/mui-wo-buildings/fine_terrain_audit.py');fine=importlib.util.module_from_spec(sp);sp.loader.exec_module(fine)
    established=fine.DemSampler(parent,rendered=True);samples=[];differences=[];max_difference=0
    for source in proof['completeSamples']:
        sample={k:v for k,v in source.items() if k not in ('ground','gap')};x,y,z=sample['point'];height=ground(x,z)
        check=established.ground(x,z);delta=abs(height-check);max_difference=max(max_difference,delta)
        # This records independent arithmetic without granting tolerance/root credit.
        sample.update(ground=height,gap=y-height);samples.append(sample)
        differences.append(dict(point=sample['point'],oldParentGround=height,oldParentGap=sample['gap'],proposedGround=source['ground'],proposedGap=source['gap'],oldParentEstablishedSampler=check,independentSamplerArithmeticDifference=delta))
    bottom=float(p[:,1].min());low=[s for s in samples if s['point'][1]<=bottom+.35]
    metric=dict(checks=len(samples),lowRimChecks=len(low),minSurfaceGap=min(s['gap'] for s in samples),minLowGap=min(s['gap'] for s in low),maxLowGap=max(s['gap'] for s in low))
    try:root=dict(accepted=True,ordinaryRim=ordinary_rim(p,idx,bottom,samples,expected_metric=metric))
    except AssertionError as error:root=dict(accepted=False,reason=str(error))
    result=dict(uid=body['uid'],manifestSHA256=read(BODY/'input.json.gz')['manifestSHA256'],parentSHA256=PARENT_SHA,wholeBasicBounds=[p.min(0).tolist(),p.max(0).tolist()],wholeBasicBoundsInsideCandidateCells=True,allTenCurrentChildrenDisjointFromWholeBasicBounds=children,completeActualBasicFaceCount=284,wholeBasicWorldSHA256=digest(p[idx].tobytes()),completeActualBasicSamples=samples,completeOldVsProposedSampleComparisons=differences,existingParentRoot=root,existingParentMetric=metric,proposedRootWasAccepted=proof['accepted'],proposedMinimumGap=min(s['gap'] for s in proof['completeSamples']),completeCapturedRootGridFaces=len(terrain),rootGridSourceCells=cells,rootGridWholeFacetSourceRecords=cell_ids,rootGridWorldSHA256=digest(terrain.tobytes()),independentEstablishedSamplerMaximumArithmeticDifference=max_difference,originalGovernmentPodiumUsedAsSupport=False,groundSupportAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Complete literal BASIC body remains unrooted even on unchanged parent. Every bounded old-parent grid facet is captured unchanged and unclipped; no source face or tiny fragment omitted. Exact finite samples are compared against the separate proposed terrain. This negative diagnostic grants no surveyed-grade, structural, current-root, collision or installation credit.')
    result.update(historicalCapturedScopeOnly=True,observedCurrentInputDrift=captured_input_drift,freshCurrentAcceptance=False)
    save(DOC/'complete-existing-parent-grid-facets.json.gz',dict(faces=terrain.tolist(),cellRecords=cell_ids,parentSHA256=PARENT_SHA))
    save(DOC/'diagnostic.json.gz',result)
    assert captured_input_drift=={path:dict(capturedSHA256=pin,observedSHA256=digest((ROOT/path).read_bytes())) for path,pin in body['inputHashes'].items() if digest((ROOT/path).read_bytes())!=pin}
    assert digest(PARENT.read_bytes())==PARENT_SHA
    refs=[Path(__file__),BODY/'input.json.gz',BODY/'complete-current-basic-podium-geometry.json.gz',BODY/'result.json',OLD/'diagnostic.json.gz',OLD/'result.json',PARENT,HERE/'original_ordinary_rim_accounting_20261009.py',HERE/'original_wall_rim_accounting_20261009.py',ROOT/'source-scripts/city/mui-wo-buildings/fine_terrain_audit.py',ROOT/'source-scripts/city/mui-wo-buildings/build.py']
    sp=importlib.util.spec_from_file_location('lippo_old_parent_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    receipt=m.freeze(BATCH,'actual-basic-whole-existing-parent-ground-comparison-v2-historical',refs,dict(uids=[body['uid']],completeActualBasicFaces=284,completeActualBasicSamples=len(samples),existingParentRoot=root,existingParentMetric=metric,proposedMinimumGap=result['proposedMinimumGap'],originalGovernmentPodiumUsedAsSupport=False,groundSupportAccepted=False,physicalAccepted=False,installationApproved=False))
    print(json.dumps(dict(jobId=receipt['jobId'],existingParentRoot=root,metric=metric)),flush=True)
if __name__=='__main__':main()
