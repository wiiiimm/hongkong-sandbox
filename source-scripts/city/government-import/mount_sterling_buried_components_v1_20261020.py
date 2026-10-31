"""Locate all flagged original faces against unchanged government terrain."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-mount-sterling-buried-components-v1-20261020';DOC=BASE/BATCH
SRC=BASE/'government-xl-mount-sterling-source-context-v1-20261020'
REC=BASE/'government-xl-mount-sterling-nine-original-recovery-v1-20261020'
GROUND=BASE/'government-xl-mount-sterling-adjoining-ground-v1-20261020'

def clip_display(mesh,bounds):
    result=[]
    for triangle in mesh:
        poly=list(triangle)
        for axis,lo,hi in [(0,bounds[0],bounds[1]),(2,bounds[2],bounds[3]),(1,3,13)]:
            for value,sign in [(lo,1),(hi,-1)]:
                output=[]
                if not poly:break
                for start,end in zip(poly,poly[1:]+poly[:1]):
                    a=sign*(start[axis]-value);b=sign*(end[axis]-value)
                    if a>=0:output.append(start)
                    if (a>=0)!=(b>=0):output.append(start+(end-start)*(a/(a-b)))
                poly=output
        if len(poly)>=3:result.append(np.asarray(poly)[:,[0,2,1]])
    return result

def main():
    assert not DOC.exists()
    refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py'];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in (SRC,REC,GROUND):
            receipt=read(folder/'result.json')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
            refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
    def take(folder,path):
        assert digest(path.read_bytes())==pins[folder][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    row=next(r for r in take(REC,REC/'recovery.json')['rows'] if r['modelId']=='B323332207602063C0')
    asset=ROOT/row['assetPath'];assert digest(asset.read_bytes())==row['sourceSHA256']==pins[REC][row['assetPath']];refs.append(asset)
    t=decode_original_world_triangles(asset.read_bytes())
    g=np.asarray(take(GROUND,HERE/'local'/GROUND.name/'289787:0-ground.json.gz')['completeAdjoiningTerrain'])
    diagnostic=take(SRC,SRC/'complete-face-diagnostic.json.gz');ids=np.array([r['faceIndex'] for r in diagnostic['buriedFaces']])
    bad=np.zeros(len(t),dtype=bool);bad[ids]=True
    final=module('mount_sterling_region_components',HERE/'xl-final-script-pass.py')
    components=final.connected_components(t,bad);records=[]
    for component in components:
        a=t[component];cross=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);areas=np.linalg.norm(cross,axis=1)/2
        records.append(dict(faceIds=[int(i) for i in component],faces=len(component),area=float(areas.sum()),bounds=[a.min((0,1)).tolist(),a.max((0,1)).tolist()],upward=int((cross[:,1]>.25*np.linalg.norm(cross,axis=1)).sum())))
    records.sort(key=lambda r:-r['area']);DOC.mkdir(parents=True)
    # Display every flagged face in one of four non-overlapping X bands.
    xmin,xmax=float(t[ids,:,0].min()),float(t[ids,:,0].max());edges=np.linspace(xmin-.01,xmax+.01,5);centres=t.mean(1)
    regions=[]
    for i,component in enumerate(records):
        if not component['upward'] and component['area']<=20:continue
        selected=np.asarray(component['faceIds'],dtype=int)
        if not len(selected):continue
        lo=t[selected].min((0,1));hi=t[selected].max((0,1));bounds=[float(lo[0]-2),float(hi[0]+2),float(lo[2]-2),float(hi[2]+2)]
        def near(mesh):return (mesh[:,:,0].max(1)>=bounds[0])&(mesh[:,:,0].min(1)<=bounds[1])&(mesh[:,:,2].max(1)>=bounds[2])&(mesh[:,:,2].min(1)<=bounds[3])
        origin=np.array([bounds[0],bounds[2],0]);fig=plt.figure(figsize=(14,7))
        for j,az in enumerate((35,215)):
            ax=fig.add_subplot(1,2,j+1,projection='3d')
            for mesh,color,alpha in ((g[near(g)],'#65a86b',.4),(t[near(t)],'#8294aa',.16),(t[selected],'#da462a',.9)):
                polygons=clip_display(mesh,bounds)
                if polygons:ax.add_collection3d(Poly3DCollection([p-origin for p in polygons],facecolor=color,edgecolor=color,alpha=alpha,linewidth=.15))
            ax.set_xlim(0,bounds[1]-bounds[0]);ax.set_ylim(0,bounds[3]-bounds[2]);ax.set_zlim(3,13);ax.set_box_aspect([bounds[1]-bounds[0],bounds[3]-bounds[2],10]);ax.view_init(25,az);ax.set_xlabel('X offset m');ax.set_ylabel('Z offset m');ax.set_zlabel('HKPD m')
        fig.suptitle(f'Mount Sterling component {i+1}: {len(selected)} flagged source faces\nGovernment terrain green; unchanged source grey/red. Display clipping only; no acceptance.');fig.tight_layout();fig.savefig(DOC/f'region-{i+1}.png',dpi=130);plt.close(fig)
        regions.append(dict(region=i+1,bounds=bounds,faceIds=selected.tolist()))
    assert sum(records[r['region']-1]['upward'] for r in regions)==sum(c['upward'] for c in records)
    summary=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],components=records,regions=regions,flaggedFaces=len(ids),installationApproved=False,sourceGeometryChanges=0)
    save(DOC/'regions.json',summary)
    module('mount_sterling_regions_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'all-upward-and-major-buried-source-component-closeups',refs,summary)
    print(dict(components=len(records),faces=len(ids),regions=len(regions)),flush=True)
if __name__=='__main__':main()
