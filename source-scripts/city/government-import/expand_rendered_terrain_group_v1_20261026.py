"""Extend a regular group's right edge using the already drawn root field.

Existing rows, children and metadata remain exact. New cells honour root water
coverage and other top-level patches. This constructs private data, not approval.
"""
from copy import deepcopy
import math
import numpy as np


def vertex_height(data, col, row):
    i=row*data['w']+col
    value=data.get('renderedElev', [])[i] if data.get('renderedElev') else None
    if value is None:
        value=max(1.2,data['elev'][i]) if data['elev'][i]>0 else -4.
    assert np.isfinite(value)
    return float(np.float32(value))


def root_sample(root, x, z):
    g=root['meta']['georef'];cx=(x+834500-g['bE'])/g['aE'];rz=(816500-z-g['bN'])/g['aN']
    c=min(root['w']-2,max(0,math.floor(cx)));r=min(root['h']-2,max(0,math.floor(rz)))
    u,v=cx-c,rz-r
    assert -1e-12<=u<=1+1e-12 and -1e-12<=v<=1+1e-12
    a,b,t,d=[vertex_height(root,i,j) for i,j in [(c,r),(c,r+1),(c+1,r),(c+1,r+1)]]
    height=(1-u-v)*a+v*b+u*t if u+v<=1 else (1-v)*t+(1-u)*b+(u+v-1)*d
    ids=[r*root['w']+c,r*root['w']+c+1,(r+1)*root['w']+c,(r+1)*root['w']+c+1]
    active=any(root['elev'][i]!=0 for i in ids)
    return height,active,(c,r)


def extend_right(parent, root, *, root_cells, other_root_cells=()):
    assert parent.get('patches') and not parent.get('nativeMesh') and not parent.get('hydro')
    pg,rg=parent['meta']['georef'],root['meta']['georef']
    assert pg['aE']==-pg['aN']==parent['cell'] and rg['aE']==-rg['aN']==root['cell']
    ratio=root['cell']/parent['cell'];assert ratio==int(ratio) and ratio>=1
    old=parent['coarseCells'];assert root_cells[:2]==old[:2] and root_cells[3]==old[3] and root_cells[2]>old[2]
    assert pg['bE']==rg['bE']+old[0]*root['cell'] and pg['bN']==rg['bN']-old[1]*root['cell']
    assert parent['w']-1==(old[2]-old[0])*ratio and parent['h']-1==(old[3]-old[1])*ratio
    extra=int((root_cells[2]-old[2])*ratio);width=parent['w']+extra;out=deepcopy(parent)
    assert width-1==(root_cells[2]-old[0])*ratio
    added=[];blocked=set();max_roundoff=0.
    for name in ['elev','renderedElev','vegetation']:
        assert len(parent[name])==parent['w']*parent['h']
        values=[]
        for row in range(parent['h']):
            values.extend(parent[name][row*parent['w']:(row+1)*parent['w']])
            for col in range(parent['w'],width):
                x=pg['bE']+col*pg['aE']-834500;z=816500-(pg['bN']+row*pg['aN'])
                h,_,(c,r)=root_sample(root,x,z)
                value=root['vegetation'][r*root['w']+c] if name=='vegetation' else h
                # Native-group grid rendering uses elev only for its zero mask.
                # Explicit exclusions below preserve inactive root cells.
                if name=='elev' and value==0:value=-4.
                values.append(value)
                if name=='renderedElev':max_roundoff=max(max_roundoff,abs(float(np.float32(h))-h))
        out[name]=values
    for row in range(parent['h']-1):
        for col in range(parent['w']-1,width-1):
            x=pg['bE']+(col+.5)*pg['aE']-834500;z=816500-(pg['bN']+(row+.5)*pg['aN'])
            _,active,(c,r)=root_sample(root,x,z)
            covered=any(a<=c<b and d<=r<e for a,d,b,e in other_root_cells)
            if not active or covered:blocked.add((col,row))
    # Coalesce horizontal inactive runs, without changing their exact cell set.
    for row in range(parent['h']-1):
        cols=sorted(c for c,r in blocked if r==row)
        while cols:
            first=last=cols.pop(0)
            while cols and cols[0]==last+1:last=cols.pop(0)
            added.append([first,row,last+1,row+1])
    out['w']=width;out['coarseCells']=list(root_cells);out['meta']['georef']['W']=width
    if added:out['patchExclusions']=[*deepcopy(parent.get('patchExclusions',[])),*added]
    assert max_roundoff<.001
    for name in ['elev','renderedElev','vegetation']:
        assert all(out[name][r*width:r*width+parent['w']]==parent[name][r*parent['w']:(r+1)*parent['w']] for r in range(parent['h']))
    assert out['patches']==parent['patches']
    return out,dict(oldWidth=parent['w'],newWidth=width,unchangedOldGridNodes=parent['w']*parent['h'],
        unchangedChildren=len(parent['patches']),newMaskedCells=len(blocked),newExclusionRectangles=added,
        maxNewVertexFloat32HeightRoundoffM=max_roundoff,rootField='Existing rendered Float32 root triangles, unchanged diagonal',
        installationApproved=False,buildingGeometryChanges=0)
