"""Read-only original DTM/root contact diagnostics for exact fresh world meshes."""
import argparse
import importlib.util
import math
import zipfile
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest


def module(name,filename):
    spec=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main():
    p=argparse.ArgumentParser();p.add_argument('--geometry',required=True);p.add_argument('--batch',required=True);a=p.parse_args()
    assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
    doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch;assert not doc.exists() and not local.exists()
    geometry_path=ROOT/a.geometry;geometry=read(geometry_path);assert geometry['diagnosticOnly'] and not geometry['publication']
    for path,sha in geometry['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    source=ROOT/'references/codex/hongkong-3d-model/data/hk-landsd-5m/Whole_HK_DTM_5m.zip'
    dtm=module('fresh_dtm','xl-original-dtm-contact-preview.py');parent=module('fresh_parent','xl-three-original-surfaces-preview.py')
    assert digest(source.read_bytes())==dtm.SHA
    parent_path=ROOT/'3d-viewer/city/data/terrain.json';ground=read(parent_path)
    jobs=[];needed={}
    for row in geometry['rows']:
        vertices=np.asarray(row['position']).reshape(-1,3);faces=vertices[np.asarray(row['index']).reshape(-1,3)];bottom=float(vertices[:,1].min())
        points=[vertices,faces.mean(axis=1)];edges=[]
        for face in faces:
            for i in range(3):
                x,y=face[i],face[(i+1)%3]
                if max(x[1],y[1])>bottom+.35:continue
                n=math.ceil(np.linalg.norm((x-y)[[0,2]]));edges.extend(x+(y-x)*j/n for j in range(1,n))
        if edges:points.append(np.array(edges))
        points=np.concatenate(points);coords=dtm.grid_coordinates(points);lo=np.floor(coords.min(axis=0)).astype(int);hi=np.floor(coords.max(axis=0)).astype(int)+1
        assert 0<=lo[0]<hi[0]<12751 and 0<=lo[1]<hi[1]<9601
        grid=np.full((hi[1]-lo[1]+1,hi[0]-lo[0]+1),np.nan);bounds=[int(lo[0]),int(lo[1]),int(hi[0]),int(hi[1])]
        jobs.append((row,points,bottom,len(edges),bounds,grid))
        for r in range(lo[1],hi[1]+1):needed.setdefault(r,[]).append((grid,r-lo[1],lo[0],hi[0]+1))
    with zipfile.ZipFile(source) as z:
        with z.open(next(n for n in z.namelist() if n.lower().endswith('.asc'))) as stream:
            header=[stream.readline().decode().strip() for _ in range(6)];assert header==read(ROOT/'docs/astra-city/landmark-preflight/terrain-inputs.json')['dtm']['asciiHeader']
            for r in range(max(needed)+1):
                line=stream.readline()
                if r in needed:
                    values=np.fromstring(line.decode(),sep=' ');assert len(values)==12751
                    for grid,ri,c0,c1 in needed[r]:grid[ri]=values[c0:c1]
    rows=[]
    for row,points,bottom,edge_count,bounds,grid in jobs:
        assert np.isfinite(grid).all()
        dh=dtm.heights(points,grid,bounds);ph=parent.parent_heights(points,ground);low=points[:,1]<=bottom+.35
        dg=points[:,1]-dh;pg=points[:,1]-ph
        dv=(dg>=-.5)&(~low|(dg<=1));pv=(pg>=-.5)&(~low|(pg<=1))
        def measures(g):return {'minSurfaceGap':float(g.min()),'minLowGap':float(g[low].min()),'maxLowGap':float(g[low].max()),'lowRimChecks':int(low.sum())}
        grid_path=local/(row['uid'].split('/')[1].replace(':','-')+'-grid.json.gz');save(grid_path,{'bounds':bounds,'heights':grid.tolist(),'sourceSHA256':dtm.SHA})
        result={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'points':len(points),'edgeChecks':edge_count,'originalDTM':measures(dg),'originalParent':measures(pg),
            'originalDTMContactPreviewPass':dtm.eligible(measures(dg)),'originalParentContactPreviewPass':dtm.eligible(measures(pg)),
            'unresolvedAcrossTwoOriginals':int((~(dv|pv)).sum()),'pointwiseTwoSourcePositive':bool((dv|pv).all() and (((dv&(dg<=.1))|(pv&(pg<=.1)))&low).any()),
            'grid':{'path':str(grid_path.relative_to(ROOT)),'sha256':digest(grid_path.read_bytes())}}
        rows.append(result);print({k:result[k] for k in ['uid','originalDTMContactPreviewPass','originalParentContactPreviewPass','pointwiseTwoSourcePositive','unresolvedAcrossTwoOriginals']},flush=True)
    save(doc/'result.json',{'rows':rows,'geometry':{'path':a.geometry,'sha256':digest(geometry_path.read_bytes())},'source':{'path':str(source.relative_to(ROOT)),'sha256':dtm.SHA},
        'parent':{'path':str(parent_path.relative_to(ROOT)),'sha256':digest(parent_path.read_bytes())},'inputHashes':geometry['inputHashes'],'runnerSHA256':digest(Path(__file__).read_bytes()),
        'diagnosticOnly':True,'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,
        'qualification':'Original surfaces and exact fresh runtime poses only. Contact previews never waive full identity, actual terrain/foundation/neighbors, runtime/browser and review/publication guards. Pointwise feasibility does not establish coherent terrain.'})

if __name__=='__main__':main()
