"""Build a rectangular metadata template around complete unchanged rendered surfaces.

This helper neither inserts terrain nor publishes anything. Every retained native
face, duplicate multiplicity and low face must survive the actual renderer capture.
"""
from collections import Counter
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from retained_native_template_v3_20261023 import verify_existing_low_faces


def face_multiset(triangles):
    values=np.asarray(triangles,dtype='float32').astype('float64')
    assert values.ndim==3 and values.shape[1:]==(3,3) and np.isfinite(values).all()
    return Counter(tuple(sorted(map(tuple,face)))for face in values)


def verify_retained_faces(baseline, originals, domain):
    baseline=np.asarray(baseline,dtype='float64')
    assert baseline.ndim==3 and baseline.shape[1:]==(3,3) and np.isfinite(baseline).all()
    assert np.array_equal(baseline,baseline.astype('float32').astype('float64')),'Capture is not production Float32'
    bounds=domain.bounds
    assert np.all(baseline[:,:,[0,2]].min((0,1))>=np.asarray(bounds[:2]))
    assert np.all(baseline[:,:,[0,2]].max((0,1))<=np.asarray(bounds[2:]))
    expected=Counter()
    for original in originals:expected.update(face_multiset(original))
    actual=face_multiset(baseline)
    assert not(expected-actual),'Retained native face changed, removed or duplicate multiplicity lost'
    return dict(retainedOriginalFaces=sum(expected.values()),completeCapturedFaces=len(baseline),
                retainedNativeFaceMultisetPreserved=True,otherCapturedFaces=len(baseline)-sum(expected.values()))


def reuse_union_template(cells,parent,baseline,retained,outer,doc,local,builder,uids):
    assert 2<=len(retained)<=4 and len({r['url']for r in retained})==len(retained)
    bounds=builder.extent(cells,parent);domain=shapely.box(*bounds)
    sources=[];originals=[];nodes=[]
    for row in retained:
        path=ROOT/'3d-viewer'/row['url'];assert digest(path.read_bytes())==row['sha256']
        node=read(path);assert node.get('nativeMesh')and not node.get('patches')and not node.get('hydro')
        assert node['meta']['parentTerrain']=='city/data/terrain.json'
        assert node['meta']['parentSha256']==digest((ROOT/'3d-viewer/city/data/terrain.json').read_bytes())
        vertices=np.asarray(node['nativeMesh']['position']).reshape(-1,3)
        originals.append(vertices[np.asarray(node['nativeMesh']['index']).reshape(-1,3)])
        nodes.append(node);sources.append(dict(path=str(path.relative_to(ROOT)),sha256=row['sha256']))
    proof=verify_retained_faces(baseline,originals,domain)
    assert domain.covers(outer)and outer.distance(domain.boundary)>0
    lineage=[dict(kind='unchanged',parentFace=i)for i in range(len(baseline))]
    low=verify_existing_low_faces(baseline,baseline,lineage,outer)
    # Native geometry supplies heights. The regular metadata grid retains the
    # existing root water classification and exact native vegetation node values.
    terrain=builder.terrain
    rendered=terrain.fine.DemSampler(parent,rendered=True);raw=terrain.fine.DemSampler(parent)
    pg=parent['meta']['georef'];step=min(5,abs(pg['aE'])/5)
    assert all(n['cell']==step and n['meta']['georef']['aE']==step for n in nodes),'Different grid resolutions require a separate exact colour binding'
    w=round((bounds[2]-bounds[0])/step)+1;h=round((bounds[3]-bounds[1])/step)+1
    elev=[];heights=[];vegetation=[]
    for r in range(h):
        z=bounds[1]+r*step
        for c in range(w):
            x=bounds[0]+c*step;before=raw.ground(x,z);after=rendered.ground(x,z)
            elev.append(float(before)if before<=0 or after<=0 else float(after));heights.append(float(after))
            pc=min(parent['w']-1,max(0,round((x+834500-pg['bE'])/pg['aE'])));pr=min(parent['h']-1,max(0,round((816500-z-pg['bN'])/pg['aN'])))
            vegetation.append(parent['vegetation'][pr*parent['w']+pc])
    for node in nodes:
        ng=node['meta']['georef'];dc=(ng['bE']-(bounds[0]+834500))/step;dr=((816500-bounds[1])-ng['bN'])/step
        assert dc==int(dc)and dr==int(dr)
        for r in range(node['h']):
            for c in range(node['w']):
                before=r*node['w']+c;after=(r+int(dr))*w+c+int(dc)
                assert vegetation[after]==node['vegetation'][before],'Retained native vegetation/colour grid changed'
                assert (elev[after]<=0)==(node['elev'][before]<=0),'Retained water classification changed'
    template=dict(id='government-native-retained-union-'+uids[0].replace('/','-').replace(':','-'),
        w=w,h=h,cell=step,elev=elev,renderedElev=heights,vegetation=vegetation,coarseCells=cells,
        meta=dict(georef=dict(aE=step,aN=-step,bE=bounds[0]+834500,bN=816500-bounds[1],W=w,H=h),
            parentTerrain='city/data/terrain.json',parentSha256=digest((ROOT/'3d-viewer/city/data/terrain.json').read_bytes()),
            targetUids=sorted(set(uids)|{uid for row in retained for uid in row['retainedUids']}),
            source=dict(provider='Lands Department/HKSAR',crs='EPSG:2326',verticalDatum='HKPD',nativeSources=sources,
                policy='Complete unchanged current renderer faces inside a closed whole-envelope union; no source simplification or model edits.')),
        nativeMesh=dict(position=np.asarray(baseline).reshape(-1).tolist(),index=list(range(len(baseline)*3)),
            source=dict(verticalDatum='HKPD',verticalScale=1,retainedNativeSources=retained,
                policy='Exact production Float32 whole-face capture, including every retained original face and duplicate.')))
    from float32_coverage import approve_roundoff
    from native_patch_resolution import projected_context
    _,polygons,_,_=projected_context(template,bounds)
    if shapely.union_all(polygons).symmetric_difference(domain).area:
        save(doc/'retained-union-roundoff.json',approve_roundoff(template,bounds))
    from primrose_compound_foundation_v2_20261015 import module
    overlap=module('retained_union_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=doc/'retained-union-overlap';overlap.DOC.mkdir()
    overlap.overlap_proof(template,[local/'parent.json',Path(__file__),*[ROOT/q['path']for q in sources]])
    builder.validate_patch(template,parent)
    save(doc/'retained-union-template-proof.json',dict(proof,lowFaces=low,coarseCells=cells,retained=retained,
        unchangedVegetationAndWaterClassification=True,qualification='Exact unchanged captured surface template only. Fresh inset/full-neighbour/source review and atomic multi-patch publication remain separate.'))
    return template
