"""Complete original fragment/glyph association and visual context; no acceptance."""
import importlib.util
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-citic-original-fragment40-glyph35-context-v1-20261011'
DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261010-citic-current-original-complete-support-v1'
PROBE=BASE/'government-xl-terrain-recovery-citic-complete-original-current-probe-v1-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 g=read(GRAPH/'diagnostic.json.gz');selected=read(PROBE/'selection.json.gz')['rows']
 assets=[ROOT/next(r for r in selected if r['uid']==a['uid'])['candidate']['path']for a in g['actors']]
 for a,p in zip(g['actors'],assets):assert ref(p)['sha256']==a['sourceSHA256']
 original=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets])
 assert original.shape==(14036,3,3)and digest(original.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256']
 runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime=read(runtimepath)
 literal=np.concatenate([np.asarray(next(r for r in runtime['rows']if r['uid']==a['uid'])['position'],float).reshape(-1,3)[np.asarray(next(r for r in runtime['rows']if r['uid']==a['uid'])['index'],np.uint32).reshape(-1,3)]for a in g['actors']])
 assert literal.shape==original.shape and np.isfinite(literal).all()
 sourceids=g['components'][40]['globalOriginalFaces'];hostids=g['components'][35]['globalOriginalFaces']
 assert len(sourceids)==1 and len(hostids)==189 and all(g['components'][k]['actorUID']=='landsd/278303:0'for k in [35,40])
 rows=[]
 for mode,tri in [('untouched-provider-original',original),('historical-production-literal',literal)]:
  result=verify(tri[sourceids[0]],tri[hostids])
  for r in result.get('completeExactFootRegionRecords',[]):r['globalOriginalHostFace']=hostids[r['originalHostFace']]
  rows.append(dict(mode=mode,completeFragmentFaceIds=sourceids,completeHostFaceIds=hostids,fragmentWorldTrianglesSHA256=digest(tri[sourceids].tobytes()),hostWorldTrianglesSHA256=digest(tri[hostids].tobytes()),finiteHostAssociation=result))
 fig=plt.figure(figsize=(18,9),dpi=100);fragment=original[sourceids];host=original[hostids]
 centers=[(host.min((0,1))+host.max((0,1)))/2,(fragment.min((0,1))+fragment.max((0,1)))/2]
 extents=[max(host.max((0,1))-host.min((0,1)))*.65,.18]
 for n,(center,extent)in enumerate(zip(centers,extents)):
  ax=fig.add_subplot(1,2,n+1,projection='3d')
  swap=lambda x:x[:,:,[0,2,1]]
  ax.add_collection3d(Poly3DCollection(swap(host-center),facecolor='#bbc9d4',edgecolor='#566775',alpha=.55,linewidth=.3))
  ax.add_collection3d(Poly3DCollection(swap(fragment-center),facecolor='#e85b2c',edgecolor='#121212',alpha=1,linewidth=1.5))
  ax.set_xlim(-extent,extent);ax.set_ylim(-extent,extent);ax.set_zlim(-extent,extent);ax.set_box_aspect((1,1,1));ax.view_init(elev=18,azim=130)
  ax.set_xlabel('local X (m)');ax.set_ylabel('local Z (m)');ax.set_zlabel('local Y (m)');ax.set_title('Complete original I component 35 / fragment 40'if n==0 else'Unchanged fragment close-up; full host drawn, view cropped')
 DOC.mkdir(parents=True);fig.tight_layout();image=DOC/'original-fragment40-glyph35-1800x900.png';fig.savefig(image,dpi=100);plt.close(fig)
 refs=[ref(p)for p in [Path(__file__),*assets,runtimepath,GRAPH/'diagnostic.json.gz',GRAPH/'result.json',PROBE/'selection.json.gz',PROBE/'result.json',HERE/'exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py',image]]
 result=dict(rows=rows,image=ref(image),pixelDimensions=[1800,900],sourceGeometryChanges=0,sourceOnlyHistoricalAssociation=True,physicalAttachmentCertified=False,visualRoleAccepted=False,structuralRootCredit=False,installationApproved=False,evidenceRefs=refs,qualification='Complete unchanged one-face fragment tested against all 189 original glyph faces in both original and historical literal representations. Fixed .1 m finite-host association is diagnostic only; no containment, closed solid, attachment, function, current/F32 or installation credit.')
 save(DOC/'diagnostic.json.gz',result)
 spec=importlib.util.spec_from_file_location('citic_fragment_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 frozen=m.freeze(BATCH,'complete-original-fragment-glyph-finite-host-context-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=['landsd/278303:0'],sourceGeometryChanges=0,sourceOnlyHistoricalAssociation=True,wholeFacetAssociated=[r['finiteHostAssociation']['wholeFacetAssociated']for r in rows],visualRoleAccepted=False,installationApproved=False))
 print(dict(jobId=frozen['jobId'],wholeFacetAssociated=[r['finiteHostAssociation']['wholeFacetAssociated']for r in rows]),flush=True)
if __name__=='__main__':main()
