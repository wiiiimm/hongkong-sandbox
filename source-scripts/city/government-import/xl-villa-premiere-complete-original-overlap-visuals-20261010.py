"""Draw complete unchanged source and clearly labelled estimated foreign actor."""
import importlib.util
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT, HERE, read, save, digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BATCH = 'government-xl-villa-premiere-complete-original-overlap-visuals-20261010'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
CONTEXT = DOC.parent / 'government-xl-villa-premiere-original-overlap-primary-context-20261010'


def main():
    assert not DOC.exists()
    DOC.mkdir(parents=True)
    context = read(CONTEXT / 'diagnostic.json.gz')
    raw = (ROOT / context['sourceInputPath']).read_bytes()
    assert digest(raw) == context['sourceSHA256']
    triangles = decode_original_world_triangles(raw)
    assert digest(triangles.astype('<f8').tobytes()) == context['worldTrianglesSHA256']
    foreign = next(b for b in context['currentForms'] if b['uid'] == context['foreignUID'])
    rings = [np.asarray(r) for r in foreign['rings']]
    marked = triangles[context['allOverlapOriginalFaceIds']]
    centre = triangles.mean(axis=(0, 1))
    xy = triangles[:, :, [0, 2]]
    figure = plt.figure(figsize=(15, 9), dpi=180)
    ax = figure.add_subplot(121, projection='3d')
    def world(a):
        return np.stack([a[..., 0]-centre[0], -a[..., 2]+centre[2], a[..., 1]], axis=-1)
    ax.add_collection3d(Poly3DCollection(world(triangles), facecolors='#b5bbc1', edgecolors='none', alpha=.67))
    ax.add_collection3d(Poly3DCollection(world(marked), facecolors='#df3528', edgecolors='#8e130b', linewidths=.2))
    for ring in rings:
        for height in [foreign['base'], foreign['base']+foreign['height']]:
            w=world(np.column_stack([ring[:,0],np.full(len(ring),height),ring[:,1]]))
            ax.plot(*w.T,color='#086bd2',lw=1.5)
        for point in ring[:-1]:
            w=world(np.array([[point[0],foreign['base'],point[1]],[point[0],foreign['base']+foreign['height'],point[1]]]))
            ax.plot(*w.T,color='#086bd2',lw=.6,alpha=.6)
    full=world(triangles); low=full.min(axis=(0,1));high=full.max(axis=(0,1))
    ax.set_xlim(low[0],high[0]);ax.set_ylim(low[1],high[1]);ax.set_zlim(0,high[2]+1)
    ax.set_box_aspect((high[0]-low[0],high[1]-low[1],high[2]+1));ax.view_init(28,-60)
    ax.set_title('All 16,669 original podium faces\nRed: all 16 projected-excess faces')
    ax.set_xlabel('East offset (m)');ax.set_ylabel('North offset (m)');ax.set_zlabel('HKPD (m)')
    top=figure.add_subplot(122)
    from matplotlib.collections import PolyCollection
    top.add_collection(PolyCollection(xy.reshape(-1,3,2),facecolors='#b8bdc2',edgecolors='none',alpha=.3))
    top.add_collection(PolyCollection(marked[:,:,[0,2]],facecolors='#df3528',edgecolors='#8e130b',linewidths=.4))
    for b,color in [(next(b for b in context['currentForms'] if b['uid']==context['uid']),'#252525'),(foreign,'#086bd2')]:
        for ring in b['rings']:
            r=np.asarray(ring);top.plot(r[:,0],r[:,1],color=color,lw=1.2)
    top.autoscale();top.set_aspect('equal');top.invert_yaxis();top.set_xlabel('World X (m)');top.set_ylabel('World Z (m)')
    top.set_title('Complete plan-view projection\nBlack: current podium; blue: distinct open-sided structure')
    figure.suptitle('Villa Premiere original source overlap — source geometry unchanged',fontsize=16)
    figure.text(.5,.015,'Blue 3D outline uses current estimated base 6.014 + estimated height 3 m. Provider heights are null; no original canopy or surveyed separation is proved.',ha='center',fontsize=10)
    figure.tight_layout(rect=[0,.05,1,.93])
    path=DOC/'complete-original-and-estimated-foreign-2700x1620.png';figure.savefig(path);plt.close(figure)
    save(DOC/'render.json',dict(width=2700,height=1620,completeOriginalFaces=len(triangles),sourceSHA256=context['sourceSHA256'],worldTrianglesSHA256=context['worldTrianglesSHA256'],sourceGeometryChanges=0,foreignHeightEstimated=True,surveyedSeparationClaim=False))
    spec=importlib.util.spec_from_file_location('villa_visual_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    result=m.freeze(BATCH,'complete-original-villa-overlap-visual-diagnosis-v1',[Path(__file__),CONTEXT/'diagnostic.json.gz',CONTEXT/'result.json',ROOT/context['sourceInputPath']],dict(uids=[context['uid'],context['foreignUID']],identityAccepted=False,physicalAccepted=False,foreignHeightEstimated=True,qualification='Complete original source diagnostic export, not a current viewer scene or surveyed foreign silhouette. All16overlapfaces/58parts remain; no source edits/identity/support credit.'))
    print(json.dumps(dict(jobId=result['jobId'],path=str(path.relative_to(ROOT)))),flush=True)


if __name__ == '__main__':main()
