"""Close hotel terrain sheet coverage using unmodified adjacent government terrain."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
import disney_hotel_original_terrain_feasibility_v1_20261015 as prior

BATCH='government-xl-disney-hotel-two-sheet-ground-v1-20261016'
DOC=ROOT/'docs/astra-city/government-import'/BATCH

def main():
    assert not DOC.exists()
    receipt=read(prior.PRIOR/'result.json');refs=[Path(__file__),Path(prior.__file__),prior.PRIOR/'result.json']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    for ref in receipt['evidenceRefs']:
        assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'];refs.append(ROOT/ref['path'])
    helper=module('hotel_two_sheet_foundation',HERE/'xl-final-script-pass.py')
    pieces=[];sources=[]
    for sheet in ['10-NE-21A','10-NW-25B']:
        folder=prior.TERRAIN.parent/sheet;metadata=read(folder/'download.json');refs.append(folder/'download.json')
        for entry in metadata['entries']:
            path=folder/'decoded'/entry['name'];assert digest(path.read_bytes())==entry['sha256'];refs.append(path)
        paths=list((folder/'decoded').rglob('*.gltf'));assert len(paths)==1
        t=helper.s.context.triangles(paths[0]);pieces.append(t)
        sources.append(dict(sheet=sheet,revision=metadata['revisionDate'],faces=len(t),bounds=[t.min(axis=(0,1)).tolist(),t.max(axis=(0,1)).tolist()]))
    terrain=np.concatenate(pieces)
    source=read(HERE/'local'/prior.PRIOR.name/'runtime-geometry.json.gz')['rows'][0]
    triangles=np.asarray(source['position']).reshape(-1,3)[np.asarray(source['index']).reshape(-1,3)]
    row=read(prior.PRIOR/'selection.json.gz')['rows'][0];b=row['source']['building']
    foundation=helper.foundation_context(triangles,terrain,Polygon(b['rings'][0],b['rings'][1:]))
    lo=triangles.min(axis=(0,1));hi=triangles.max(axis=(0,1))
    mask=(terrain[:,:,0].max(axis=1)>=lo[0]-1)&(terrain[:,:,0].min(axis=1)<=hi[0]+1)&(terrain[:,:,2].max(axis=1)>=lo[2]-1)&(terrain[:,:,2].min(axis=1)<=hi[2]+1)
    ground=terrain[mask];polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10
    ground,polygons=ground[valid],polygons[valid]
    points=np.concatenate([triangles,triangles.mean(axis=1)[:,None,:]],axis=1)
    heights=helper.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),ground,shapely.STRtree(polygons)).reshape(-1,4)
    gaps=points[:,:,1]-heights;bad=np.argwhere(np.isfinite(heights)&(gaps<-.5));cross=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);normal_length=np.linalg.norm(cross,axis=1)
    affected=np.unique(bad[:,0]);vertical=np.abs(cross[affected,1])<=1e-8*normal_length[affected]
    failures=[dict(face=int(i),sample=int(j),position=points[i,j].tolist(),gapM=float(gaps[i,j]))for i,j in bad]
    summary=dict(uid=row['uid'],foundation=foundation,failedSamples=len(bad),affectedFaces=len(affected),verticalAffectedFaces=int(vertical.sum()),nonverticalAffectedFaces=[int(i)for i,v in zip(affected,vertical)if not v],missingSamples=int((~np.isfinite(heights)).sum()),fullAcceptance=False,newlyInstalled=0)
    DOC.mkdir();save(DOC/'summary.json',summary);save(DOC/'source-context.json.gz',dict(sources=sources,failures=failures,affectedFaces=[dict(face=int(i),vertices=triangles[i].tolist())for i in affected],terrainGeometryChanged=False))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    fig,ax=plt.subplots(figsize=(12,8));ax.add_collection(PolyCollection(triangles[:,:,[0,2]],facecolors='none',edgecolors='#8c99a6',linewidths=.15))
    ax.add_collection(PolyCollection(triangles[affected][:,:,[0,2]],facecolors='#d54a4033',edgecolors='#cc3020',linewidths=.65))
    if len(bad):ax.scatter(points[bad[:,0],bad[:,1],0],points[bad[:,0],bad[:,1],2],s=7,color='#bb2211',label='Below original terrain by >0.5 m')
    ax.set_xlim(lo[0]-8,hi[0]+8);ax.set_ylim(lo[2]-8,hi[2]+8);ax.set_aspect('equal');ax.set_xlabel('Viewer X (m)');ax.set_ylabel('Viewer Z (m)');ax.set_title('Disneyland Hotel — complete source and remaining terrain intersections');ax.legend();fig.tight_layout();fig.savefig(DOC/'source-failures-plan.png',dpi=150);plt.close(fig)
    refs += [Path(helper.__file__),Path(helper.s.__file__),Path(helper.s.context.__file__),Path(helper.s.context.shared.__file__)]
    result=module('hotel_two_sheet_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-hotel-adjoining-original-terrain-coverage-v1',refs,dict(uids=[row['uid']],summary=summary,fullAcceptance=False,newlyInstalled=0))
    print(dict(jobId=result['jobId'],summary=summary),flush=True)

if __name__=='__main__':main()
