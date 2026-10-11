"""Proportional source-only view: all unit faces plus lower-loop contributing roof.

Earlier v1 used the full long roof-facet plotting extent and a short vertical
axis, making the unit appear slender. This view uses equal metric scaling and only actual lower-loop roof contributors.
Both frozen prior renders remain untouched; no render is acceptance.
"""
from pathlib import Path
import importlib.util
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-parkview-roof-unit324-contributing-roof-context-v3';DOC=BASE/BATCH
INPUT=BASE/'xl-terrain-recovery-20261011-parkview-original-roof-unit324-interface-v1';PROBE=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-current-probe-v1-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();r=read(INPUT/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 d=read(INPUT/'diagnostic.json.gz');row=d['rows'][0];selected=read(PROBE/'selection.json.gz')['rows'];assets=[ROOT/r['candidate']['path']for r in selected]
 for r,p in zip(selected,assets):assert digest(p.read_bytes())==r['sourceSHA256']
 t=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets]);assert digest(t.tobytes())==row['completeCombinedWorldSHA256'];unit=t[row['completeOriginalFaces']];contributing=sorted({p['originalSourceFace']for e in row['completeEveryOriginalBoundaryEdge']if e['isExactMinimumHeightLowerBoundary']for p in e['band']['completeOriginalSurfacePieces']});host=t[contributing];assert len(unit)==72
 center=(unit.min(axis=(0,1))+unit.max(axis=(0,1)))/2;u=(unit-center)[:,:,[0,2,1]];h=(host-center)[:,:,[0,2,1]];lo=u.min(axis=(0,1))-.45;hi=u.max(axis=(0,1))+.45;span=hi-lo
 fig=plt.figure(figsize=(18,9),dpi=100)
 for k,(elev,azim)in enumerate([(24,-55),(23,140)],1):
  ax=fig.add_subplot(1,2,k,projection='3d');ax.add_collection3d(Poly3DCollection(h,facecolors='#9bb8ce',edgecolors='#46657f',linewidths=.55,alpha=.8));ax.add_collection3d(Poly3DCollection(u,facecolors='#d8b470',edgecolors='#553a20',linewidths=.8,alpha=1));ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect(span);ax.view_init(elev,azim);ax.set_xlabel('Original X (m)');ax.set_ylabel('Original Z (m)');ax.set_zlabel('Original Y (m)');ax.set_title('All 72 original unit faces; only actual lower-loop contributing host roof facets')
 fig.tight_layout();DOC.mkdir(parents=True);png=DOC/'original-unit324-contributing-roof-close-context-1800x900.png';fig.savefig(png);plt.close(fig)
 refs=[ref(p)for p in [Path(__file__),png,INPUT/'result.json',INPUT/'diagnostic.json.gz',PROBE/'selection.json.gz',*assets,HERE/'exact_packed_world_geometry_20261009.py']]
 result=dict(uids=[r['uid']for r in selected],component=324,completeUnitFaces=72,completeSourceWorldSHA256=digest(t.tobytes()),originalMetricAxisScale=True,allFiniteLowerLoopContributingHostFacetIds=contributing,completeHostInventoryRetainedInInput=True,contributingHostCameraCropped=True,cameraRelativeXYZBounds=[lo.tolist(),hi.tolist()],historicalV1RenderPreserved=True,sourceOnly=True,roleInterpretation=False,sourceGeometryChanges=0,fullAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
 s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-original-unit324-equal-metric-actual-lower-loop-contributing-host-visual-diagnostic-v3',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],sourceOnly=True,roleInterpretation=False,newlyInstalled=0))
if __name__=='__main__':main()
