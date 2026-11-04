"""Expand a retained envelope using only independently matched already-drawn faces."""
import copy
from collections import Counter
from pathlib import Path
import math
import numpy as np
import shapely
from run import ROOT,read,save,digest
from retained_native_template_v3_20261023 import reuse_template as same_extent,verify_existing_low_faces


def face_counter(faces):
    a=np.asarray(faces,dtype=float);assert a.ndim==3 and a.shape[1:]==(3,3)and np.isfinite(a).all()
    return Counter(tuple(sorted(map(tuple,f)))for f in a)


def rendered_root_faces(parent,cells,excluded):
    c0,r0,c1,r1=cells;a,b,c,d=excluded;g=parent['meta']['georef'];w=parent['w'];faces=[];rendered_values=parent.get('renderedElev')
    assert all(type(i)is int for i in cells+excluded)
    assert 0<=c0<=a<c<=c1<w and 0<=r0<=b<d<=r1<parent['h']
    def vertex(col,row):
        i=row*w+col;e=parent['elev'][i];height=rendered_values[i]if rendered_values is not None else None
        if height is None or not math.isfinite(height):height=max(1.2,e)if e>0 else -4
        return np.asarray([g['bE']+col*g['aE']-834500,height,816500-(g['bN']+row*g['aN'])],dtype=np.float32).astype(float)
    for row in range(r0,r1):
        for col in range(c0,c1):
            if a<=col<c and b<=row<d:continue
            ids=[row*w+col,row*w+col+1,(row+1)*w+col,(row+1)*w+col+1]
            if all(not parent['elev'][i]for i in ids):continue
            aa,bb,dd,ee=vertex(col,row),vertex(col+1,row),vertex(col,row+1),vertex(col+1,row+1)
            faces.extend([[aa,dd,bb],[bb,dd,ee]])
    return np.asarray(faces,dtype=float).reshape(-1,3,3)


def verify_capture(old_faces,baseline,parent,cells,old_cells):
    old=np.asarray(old_faces,dtype=np.float32).astype(float);baseline=np.asarray(baseline,dtype=float)
    required=face_counter(old);actual=face_counter(baseline);assert not(required-actual),'Existing rendered native face or multiplicity missing'
    extras=rendered_root_faces(parent,cells,old_cells)
    assert actual-required==face_counter(extras),'Expanded capture differs from exact root faces outside retained cells'
    assert len(baseline)==len(old)+len(extras),'Unexpected duplicate or missing parent face'
    return dict(existingRenderedFaces=len(old),exactAddedRootFaces=len(extras),completeCapturedFaces=len(baseline),allRetainedRenderedFacesAndMultiplicityPreserved=True,allExtraFacesMatchProductionRoot=True)


def expanded_grid(template,parent,cells,bounds,builder):
    out=copy.deepcopy(template);step=template['cell'];assert step>0
    w=round((bounds[2]-bounds[0])/step)+1;h=round((bounds[3]-bounds[1])/step)+1
    g=template['meta']['georef'];offset_col=(g['bE']-834500-bounds[0])/step;offset_row=(816500-g['bN']-bounds[1])/step
    assert offset_col.is_integer()and offset_row.is_integer();oc,orr=int(offset_col),int(offset_row)
    assert 0<=oc and 0<=orr and oc+template['w']<=w and orr+template['h']<=h
    raw=builder.terrain.fine.DemSampler(parent);rendered=builder.terrain.fine.DemSampler(parent,rendered=True);pg=parent['meta']['georef'];arrays={k:[]for k in ['elev','renderedElev','vegetation']};retained_nodes=0;water_nodes=0
    for row in range(h):
        for col in range(w):
            x,z=bounds[0]+col*step,bounds[1]+row*step;parent_raw=float(raw.ground(x,z));water_nodes+=parent_raw<=0
            if oc<=col<oc+template['w']and orr<=row<orr+template['h']:
                i=(row-orr)*template['w']+col-oc
                for key in arrays:arrays[key].append(template.get(key,template['elev'])[i])
                assert (template['elev'][i]<=0)==(parent_raw<=0),'Existing metadata water mask differs from current parent'
                retained_nodes+=1
            else:
                arrays['elev'].append(parent_raw);arrays['renderedElev'].append(float(rendered.ground(x,z)))
                pc=min(parent['w']-1,max(0,round((x+834500-pg['bE'])/pg['aE'])));pr=min(parent['h']-1,max(0,round((z-816500+pg['bN'])/pg['aE'])));arrays['vegetation'].append(parent['vegetation'][pr*parent['w']+pc])
    assert retained_nodes==template['w']*template['h']
    out.update(w=w,h=h,coarseCells=cells,**arrays);out['meta']['georef']=dict(aE=step,aN=-step,bE=bounds[0]+834500,bN=816500-bounds[1],W=w,H=h)
    out['meta']['source']['parentWaterMask']=dict(waterNodes=int(water_nodes),landNodes=w*h-int(water_nodes),policy='Raw parent water/land classification preserved at every refinement node.')
    out['meta']['source']['expandedRetainedEnvelope']=dict(originalCoarseCells=template['coarseCells'],retainedGridNodes=retained_nodes,policy='Every old grid field copied exactly at its aligned node; extension samples unchanged parent metadata. Drawn geometry is separately matched to complete existing native plus production-root faces.')
    return out


def reuse_template(cells,parent,baseline,retained,outer,doc,local,builder):
    assert len(retained)==1
    path=ROOT/'3d-viewer'/retained[0]['url'];assert digest(path.read_bytes())==retained[0]['sha256'];old=read(path)
    if cells==old['coarseCells']:return same_extent(cells,parent,baseline,retained,outer,doc,local,builder)
    assert not old.get('patches')and not old.get('hydro')
    assert old['meta']['parentTerrain']=='city/data/terrain.json'and old['meta']['parentSha256']==digest((ROOT/'3d-viewer/city/data/terrain.json').read_bytes())
    faces=np.asarray(old['nativeMesh']['position']).reshape(-1,3)[np.asarray(old['nativeMesh']['index']).reshape(-1,3)]
    proof=verify_capture(faces,baseline,parent,cells,old['coarseCells']);bounds=builder.extent(cells,parent)
    low=verify_existing_low_faces(baseline,baseline,[dict(kind='unchanged',parentFace=i)for i in range(len(baseline))],outer)
    template=expanded_grid(old,parent,cells,bounds,builder)
    template['nativeMesh']['position']=np.asarray(baseline).reshape(-1).tolist();template['nativeMesh']['index']=list(range(len(baseline)*3));template['nativeMesh']['source'].pop('numericalCoverageGap',None)
    from float32_coverage import approve_roundoff
    from native_patch_resolution import projected_context
    _,polygons,_,_=projected_context(template,bounds)
    if shapely.union_all(polygons).symmetric_difference(shapely.box(*bounds)).area:save(doc/'expanded-template-coverage.json',approve_roundoff(template,bounds))
    from primrose_compound_foundation_v2_20261015 import module
    overlap=module('expanded_template_overlap',Path(__file__).parent/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=doc/'expanded-template-overlap';overlap.DOC.mkdir();overlap.overlap_proof(template,[path,local/'parent.json',Path(__file__)])
    builder.validate_patch(template,parent)
    save(doc/'retained-template-proof.json',dict(**proof,**low,templatePath=str(path.relative_to(ROOT)),templateSHA256=retained[0]['sha256'],coarseCells=cells,sourceGeometryChanges=0,geometryChangesToCapturedSurface=0,qualification='Separately validated expanded template. Exact complete old Float32 rendered-face multiset and independently reconstructed production coarse-root faces exhaust the captured surface. Every old metadata grid node retained. Existing water/clamp/coverage/overlap/native validators unchanged; no geometry simplification or source edits.'))
    return template
