"""Inspect complete authenticated foreign contacts; no suppression or approval."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face
from exact_contact_role_context_v1_20261023 import contact_role


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-west-kowloon-bus-';batch=prefix+'foreign-contact-views-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,f):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        p=base/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    capture=prefix+'protected-full-foreign-v1-20261024';runtime=prefix+'protected-return-runtime-v1-20261024';scope=prefix+'protected-full-model-scope-v1-20261024'
    selection=take(runtime,'selection.json.gz');row=selection['rows'][0];assert row['uid']=='landsd/255415:0';asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    source=decode_original_world_triangles(asset.read_bytes());basic=take(capture,'basic.json');meshes={r['uid']:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in basic['rows']};forms={r['building']['uid']:r['building']for r in take(scope,'255415:0-forms.json.gz')};summary=take(capture,'summary.json');rows=[]
    for rec in summary['rows']:
        uid=rec['foreignUid'];positive=next(m for m in rec['modes']if m['mode']=='original')['positiveContactPairs']
        if not positive:continue
        foreign=meshes[uid];proof=take(capture,'255415:0--'+uid.split('/')[1]+'--original.json.gz');assert proof['allPairsExamined'];classified=[]
        for c in proof['contacts']:
            points=[tuple(Fraction(v)for v in q)for q in c['exactPoints']]
            role=contact_role(rational_face(source[c['sourceFaceA']]),rational_face(foreign[c['sourceFaceB']]),points,c['dimension'],[c['sourcePrimitiveDimensionA'],c['sourcePrimitiveDimensionB']])
            classified.append(dict(c,contactRole=role))
        save(out/(uid.split('/')[1]+'-roles.json.gz'),classified)
        pts=np.asarray([[float(Fraction(v))for v in q]for c in classified for q in c['exactPoints']]);lo=pts.min(0)-3;hi=pts.max(0)+3;centre=(lo+hi)/2
        hits=sorted({c['sourceFaceA']for c in classified});foreignhits=sorted({c['sourceFaceB']for c in classified});near=np.flatnonzero(np.all(source.max(1)>=lo,axis=1)&np.all(source.min(1)<=hi,axis=1));fig=plt.figure(figsize=(16,8))
        for i,az in enumerate([-125,55]):
            ax=fig.add_subplot(1,2,i+1,projection='3d')
            for tri,ids,col,alpha in [(source,near,'#8d9da9',.1),(foreign,range(len(foreign)),'#326e99',.14),(source,hits,'#ee8822',.7),(foreign,foreignhits,'#326e99',.45)]:
                ax.add_collection3d(Poly3DCollection((tri[list(ids)]-centre)[:,:,[0,2,1]],facecolor=col,edgecolor='none',alpha=alpha))
            q=(pts-centre)[:,[0,2,1]];ax.scatter(*q.T,c='#ba2020',s=3,depthshade=False)
            ax.set_xlim(lo[0]-centre[0],hi[0]-centre[0]);ax.set_ylim(lo[2]-centre[2],hi[2]-centre[2]);ax.set_zlim(lo[1]-centre[1],hi[1]-centre[1]);ax.set_box_aspect((hi-lo)[[0,2,1]].copy());ax.view_init(25,az);ax.set(xlabel='Local X m',ylabel='Local Z m',zlabel='Height m')
        fig.suptitle(uid+': orange original / blue retained BASIC / red exact contacts; no acceptance');fig.tight_layout();image=out/(uid.split('/')[1]+'.png');image.parent.mkdir(parents=True,exist_ok=True);fig.savefig(image,dpi=120);plt.close(fig)
        rows.append(dict(foreignUid=uid,form=forms[uid],roles=dict(Counter(c['contactRole']for c in classified)),sourceFaces=hits,foreignFaces=foreignhits,intersectionBounds=[pts.min(0).tolist(),pts.max(0).tolist()],image=str(image.relative_to(ROOT)),imageSHA256=digest(image.read_bytes()),allFourRawMetrics=rec['modes']))
    for p,h in basic['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],currentManifestSHA256=selection['manifestSHA256'],rows=rows,sourceGeometryChanges=0,suppressionApproved=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='All saved original-world finite contacts classified and plotted, with all four raw coordinate results preserved. Basic actors remain unchanged. Overlap does not establish common ownership, acceptable collision or permission to suppress.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_shell_intersections_20261009.py','exact_contact_role_context_v1_20261023.py']);module('west_foreign_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'current-complete-foreign-contact-role-and-view-diagnostic',refs,result);print(dict(pairs=len(rows)),flush=True)

if __name__=='__main__':main()
