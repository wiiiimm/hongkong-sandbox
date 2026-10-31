"""Source-context views of the exact failing wall and its immutable roof path."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BATCH = 'government-xl-nam-cheong-wall-source-views-v1-20261023'
RUNTIME = 'government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-runtime'
GRADE = 'government-xl-nam-cheong-wall-grade-path-v2-20261023'


def main():
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / BATCH
    assert not doc.exists()
    refs, pins = [Path(__file__)], {}
    for name in [RUNTIME, GRADE]:
        _, pins[name] = authenticate(base / name)
        refs.append(base / name / 'result.json')
    def take(name, path):
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    g = next(r for r in take(RUNTIME, HERE / 'local' / RUNTIME / 'runtime-geometry.json.gz')['rows'] if r['uid'] == 'landsd/268867:0')
    tri = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
    ground = np.asarray(g['drawnGroundGeometry']).reshape(-1, 3, 3)
    grade = take(GRADE, base / GRADE / 'literal.json.gz')
    assert digest(tri.tobytes()) == grade['sourceWorldSHA256']
    assert digest(ground.tobytes()) == grade['groundSHA256']
    wall = tri[11390]
    path = grade['originalPath']
    assert path == [11390, 11391, 11411, 11410, 2642]
    center = wall.mean(0)
    lo, hi = center + [-6,-1,-6], center + [6,5,6]
    def candidates(values):
        return np.flatnonzero(np.all(values.max(1)>=lo,axis=1)&np.all(values.min(1)<=hi,axis=1))
    a, b = candidates(tri), candidates(ground)
    doc.mkdir()
    views = []
    for name, azimuth in [('southwest', -125), ('northeast', 55)]:
        fig = plt.figure(figsize=(10,8));ax = fig.add_subplot(projection='3d')
        for values, ids, color, alpha in [(ground,b,'#9b9586',.35),(tri,a,'#92aac1',.18),(tri,path,'#e39926',.7),(tri,[11390],'#d11925',1)]:
            local = values[ids].copy();local[:,:,[0,2]] -= center[[0,2]]
            ax.add_collection3d(Poly3DCollection(local[:,:,[0,2,1]],facecolor=color,edgecolor='none',alpha=alpha))
        ax.set_xlim(-6,6);ax.set_ylim(-6,6);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect([12,12,6]);ax.view_init(elev=22,azim=azimuth)
        ax.set(xlabel='Local east (m)',ylabel='Local Z (m)',zlabel='HKPD height (m)',title='Nam Cheong wall11390 (red), original roof path (orange), current ground (grey)')
        fig.tight_layout();pathout=doc/(name+'.png');fig.savefig(pathout,dpi=135);plt.close(fig)
        views.append(dict(path=str(pathout.relative_to(ROOT)),sha256=digest(pathout.read_bytes())))
    summary=dict(uids=[g['uid']],sourceSHA256=g['sourceSHA256'],sourceFace=11390,originalPath=path,views=views,
                 plottedContextSourceFaces=list(map(int,a)),plottedContextGroundFaces=list(map(int,b)),
                 currentFullSourceWorldSHA256=digest(tri.tobytes()),currentCompleteGroundSHA256=digest(ground.tobytes()),
                 sourceRoleAccepted=False,installationApproved=False,
                 qualification='Original immutable faces only. Plot frame clips wider context and may occlude path sections; no geometry editing or inferred role/root/support approval from colours or source adjacency alone.')
    save(doc/'summary.json',summary)
    module('nam_wall_source_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-bound-one-original-wall-and-roof-path-views',refs,summary)


if __name__=='__main__':
    main()
