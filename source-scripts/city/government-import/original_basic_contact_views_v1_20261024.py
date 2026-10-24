"""Plot exact before/after basic contacts; clipping affects diagrams only."""
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from fractions import Fraction
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_context_plot_v3_20261023 import clipped_faces


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','contacts','runtime','uid','foreign']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists();refs=[Path(__file__)];pins={}
    def take(n,filename):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        path=base/n/filename;assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    rows=take(a.runtime,'selection.json.gz')['rows'];row=next(r for r in rows if r['uid']==a.uid);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);original=decode_original_world_triangles(asset.read_bytes())
    basic=take(a.contacts,'basic.json');by={r['uid']:r for r in basic['rows']}
    def geometry(uid):
        r=by[uid];return np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
    before,foreign=geometry(a.uid),geometry(a.foreign);lo=foreign.min((0,1));hi=foreign.max((0,1));center=(lo+hi)/2
    limits=[(lo[0]-2,hi[0]+2),(lo[1]-1,hi[1]+3),(lo[2]-2,hi[2]+2)]
    planes=[(axis,value,lower)for axis,(low,high)in enumerate(limits)for value,lower in [(low,True),(high,False)]]
    def transform(t):
        return (t-center)[:,:,[0,2,1]]
    proofs={};role_rows=[]
    for mode,source in [('before-basic',before),('original',original)]:
        name=a.uid.split('/')[1]+'--'+a.foreign.split('/')[1]+'--'+mode+'.json.gz';proofs[mode]=take(a.contacts,name)
        for c in proofs[mode]['contacts']:
            if c['dimension']<=0:continue
            values=[]
            for t in [source[c['sourceFaceA']],foreign[c['sourceFaceB']]]:
                n=np.cross(t[1]-t[0],t[2]-t[0]);length=np.linalg.norm(n);values.append(float(abs(n[1])/length)if length>0 else None)
            role_rows.append(dict(mode=mode,sourceFace=c['sourceFaceA'],foreignFace=c['sourceFaceB'],dimension=c['dimension'],absoluteNormalY=values,bounds=c['bounds']))
    fig=plt.figure(figsize=(14,12),layout='constrained')
    for rownum,(mode,source)in enumerate([('before-basic',before),('original',original)]):
        clipped=clipped_faces(source,planes);display=np.concatenate([transform(clipped),transform(foreign)]);colors=['#94b1c4']*len(clipped)+['#d6ae50']*len(foreign)
        for col,azim in enumerate([30,210]):
            ax=fig.add_subplot(2,2,rownum*2+col+1,projection='3d');ax.add_collection3d(Poly3DCollection(display,facecolors=colors,edgecolor='#45535c',linewidths=.15,alpha=.85))
            for c in proofs[mode]['contacts']:
                if c['dimension']<=0:continue
                pts=np.asarray([[float(Fraction(v))for v in q]for q in c['exactPoints']])-center;pts=pts[:,[0,2,1]];ax.plot(*pts.T,color='#bb1422',linewidth=2)
            ax.set(xlim=tuple(v-center[0]for v in limits[0]),ylim=tuple(v-center[2]for v in limits[2]),zlim=tuple(v-center[1]for v in limits[1]),xlabel='Local east',ylabel='Local Z',zlabel='Local height',title=mode+' blue / retained basic gold / contacts red');ax.set_box_aspect([limits[i][1]-limits[i][0]for i in [0,2,1]]);ax.view_init(24,azim)
    fig.suptitle(a.uid+' vs '+a.foreign+' — diagram-only clipping; no source edits or acceptance')
    out.mkdir();fig.savefig(out/'before-after-contact-context.png',dpi=130);plt.close(fig)
    result=dict(uids=[a.uid],retainedUid=a.foreign,sourceSHA256=row['sourceSHA256'],diagramClippingWorldBounds=limits,contactContext=role_rows,sourceGeometryChanges=0,installationApproved=False,visualAcceptance=False,qualification='Complete source and exact current basic meshes/proofs supply the diagram. Display clipped around retained actor only; original assets are untouched. Surface orientation, finite contacts and this plot alone do not establish ownership, safe placement, support or approval.')
    save(out/'summary.json',result);refs.extend([HERE/'original_assembly_context_plot_v3_20261023.py',HERE/'exact_packed_world_geometry_20261009.py']);module('original_basic_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unchanged-original-current-basic-contact-context-views',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
