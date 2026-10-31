"""Exact assembly/cell context for flagged source identities; no identity approval."""
import argparse
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_projection_coverage_v2_20261010 import exact_coverage
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','capture','identity']:p.add_argument('--'+k,required=True)
    p.add_argument('--uid',action='append',required=True);a=p.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.capture,a.identity])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:
            _,pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.capture,base/a.capture/'selection.json.gz');sources={r['uid']:r for r in selection['rows']}
    assert len(a.uid)==len(set(a.uid))and set(a.uid)<=set(sources)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    triangles={};projections={}
    for uid,r in sources.items():
        path=ROOT/r['candidate']['path'];assert digest(path.read_bytes())==r['sourceSHA256'];refs.append(path)
        tri=decode_original_world_triangles(path.read_bytes());assert len(tri)==r['triangles'];triangles[uid]=tri
        projections[uid]=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
    complete=np.concatenate(list(triangles.values()));assembly=shapely.union_all(list(projections.values()))
    rows=[];fig,axes=plt.subplots(2,2,figsize=(12,12));axes=np.asarray(axes).ravel()
    assert len(a.uid)<=4
    def draw(ax,geometry,**kw):
        for part in shapely.get_parts(geometry):
            if part.geom_type=='Polygon':
                x,z=part.exterior.xy;ax.fill(x,z,**kw)
    for ax,uid in zip(axes,a.uid):
        r=sources[uid];raw=take(a.identity,base/a.identity/(uid.split('/')[1]+'/identity.json'))
        assert raw['sourceSHA256']==r['sourceSHA256']and raw['exactCurrentComponentRoute']['qualified']
        target=shapely.Polygon(r['source']['building']['rings'][0],r['source']['building']['rings'][1:]);projection=projections[uid]
        missing=target.difference(projection);covered=target.intersection(assembly).area/target.area
        x0,z0,x1,z1=raw['geographicCell']['worldXZBounds'];cell=shapely.box(x0,z0,x1,z1)
        halves=[np.array([[x0,0,z0],[x1,0,z0],[x0,0,z1]]),np.array([[x1,0,z0],[x1,0,z1],[x0,0,z1]])]
        proofs=[exact_coverage(t,complete)for t in halves]
        row=dict(uid=uid,sourceSHA256=r['sourceSHA256'],name=r['source']['building'].get('name'),rawReasonsRetained=raw['reasons'],ownTargetCoverage=target.intersection(projection).area/target.area,completeAssemblyTargetCoverage=covered,missingTargetAreaM2=missing.area,missingTargetNotCoveredByOriginalAssemblyM2=missing.difference(assembly).area,symmetricOutlineHausdorffDistanceM=target.hausdorff_distance(projection),rawWholeCellCovered=raw['exactWholeCellCoverage']['covered'],completeAssemblyWholeCellCovered=all(q['exactProjectionCovered']for q in proofs),exactAssemblyCellProof=proofs,exactCurrentComponentRoute=raw['exactCurrentComponentRoute'],sourceGraphVerified=raw['originalOwnership']['sourceGraphVerified'],identityAccepted=False)
        rows.append(row)
        draw(ax,projection,color='#c8cfce',alpha=.9,label='original source')
        draw(ax,missing,color='#cf5345',alpha=.7)
        x,z=target.exterior.xy;ax.plot(x,z,color='#325b8c',linewidth=1.3)
        x,z=cell.exterior.xy;ax.plot(x,z,color='#a23c9d',linewidth=1.2)
        ax.set_aspect('equal');ax.set_title(str(row['name'])+' · '+uid+'\nown coverage '+format(row['ownTargetCoverage'],'.2%')+' · original assembly '+format(covered,'.2%'))
        ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(labelsize=7)
    for ax in axes[len(a.uid):]:ax.set_visible(False)
    fig.suptitle('Original source grey · current record blue · record outside source red · GeoRef cell purple\nDiagnostic only: component routes, mesh ownership, source roles and acceptance remain separate',fontsize=11)
    fig.tight_layout(rect=[0,0,1,.95]);out.mkdir();fig.savefig(out/'source-record-context.png',dpi=150);plt.close(fig)
    result=dict(uids=a.uid,requiredOriginalAssembly={u:r['sourceSHA256']for u,r in sources.items()},completeOriginalFaces=len(complete),currentManifestSHA256=selection['manifestSHA256'],rows=rows,identityAccepted=False,physicalAcceptance=False,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Exact original assembly projections and cell coverage provide additional source relationship context only. Raw individual95percent coverage/cell/graph flags remain. This does not automatically substitute compound coverage for individual identity or approve ownership, physical roles or publication.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_projection_coverage_v2_20261010.py'])
    module('original_assembly_identity_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'original-assembly-exact-source-record-and-georef-cell-context-no-approval',list(dict.fromkeys(refs)),result)
    print([dict(uid=r['uid'],ownCoverage=r['ownTargetCoverage'],assemblyCoverage=r['completeAssemblyTargetCoverage'],outlineDistanceM=r['symmetricOutlineHausdorffDistanceM'],cell=r['completeAssemblyWholeCellCovered'])for r in rows],flush=True)


if __name__=='__main__':main()
