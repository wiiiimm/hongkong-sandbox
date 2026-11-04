"""Source-only close views of every saved original assembly interface; no acceptance."""
import argparse
from collections import Counter
from fractions import Fraction
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'runtime', 'contacts']:
        ap.add_argument('--' + name, required=True)
    ap.add_argument('--include-uid', action='append', required=True)
    a = ap.parse_args(); base = ROOT / 'docs/astra-city/government-import'
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    out = base / a.batch; assert not out.exists()
    refs = [Path(__file__)]; pins = {}
    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]; refs.append(base / batch / 'result.json')
        path = base / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    selection = take(a.runtime, 'selection.json.gz'); summary = take(a.contacts, 'summary.json')
    sources, triangles = {}, {}
    for row in selection['rows']:
        uid = row['uid']; path = ROOT / row['candidate']['path']
        assert digest(path.read_bytes()) == row['sourceSHA256'] == summary['sourceSHA256ByUid'][uid]
        refs.append(path); sources[uid] = row
        triangles[uid] = decode_original_world_triangles(path.read_bytes())
        assert len(triangles[uid]) == row['triangles']
    assert set(sources) == set(summary['uids']) and summary['allRawContactsClassified']
    out.mkdir(); results = []
    for pair in summary['rows']:
        if pair['mode'] != 'original' or pair['strictBoundsSeparated'] or pair['contactCount'] == 0 or not ({pair['uid'], pair['peerUid']} & set(a.include_uid)):
            continue
        u, v = pair['uid'], pair['peerUid']
        raw = take(a.contacts, u.split('/')[1]+'--'+v.split('/')[1]+'--original.json.gz')
        assert len(raw) == pair['contactCount']
        points = [np.asarray([[float(Fraction(z)) for z in p] for p in c['exactPoints']]) for c in raw]
        joined = np.concatenate(points); lo, hi = joined.min(0), joined.max(0)
        # Complete companion and every peer triangle touching the display box.
        limits_lo = np.minimum(lo, triangles[u].min((0, 1))) - [3, 1, 3]
        limits_hi = np.maximum(hi, triangles[u].max((0, 1))) + [3, 1, 3]
        peer = triangles[v]
        mask = np.all(peer.max(1) >= limits_lo, axis=1) & np.all(peer.min(1) <= limits_hi, axis=1)
        shown = [triangles[u], peer[mask]]
        center = (limits_lo+limits_hi)/2
        def transform(t):
            return (np.asarray(t)-center)[..., [0, 2, 1]]
        fig = plt.figure(figsize=(18, 8), layout='constrained')
        for j, angle in enumerate([35, 215]):
            ax = fig.add_subplot(1, 3, j+1, projection='3d')
            for mesh, color in zip(shown, ['#d89d43', '#93abb9']):
                ax.add_collection3d(Poly3DCollection(transform(mesh), facecolors=color, edgecolor='#52616b', linewidth=.15, alpha=.85))
            lines = [transform(p[[i, i+1]]) for p in points for i in range(len(p)-1)]
            if lines: ax.add_collection3d(Line3DCollection(lines, colors='#c82424', linewidths=2))
            bounds = transform(np.asarray([limits_lo, limits_hi]))
            ax.set(xlim=bounds[:,0], ylim=bounds[:,1], zlim=bounds[:,2], xlabel='east offset (m)', ylabel='viewer Z offset (m)', zlabel='height offset (m)')
            ax.set_box_aspect(bounds[1]-bounds[0]); ax.view_init(elev=23, azim=angle)
        ax=fig.add_subplot(1,3,3)
        for mesh, color in zip(shown, ['#d89d43','#93abb9']):
            for f in transform(mesh):
                ax.fill(f[:,0],f[:,1],color=color,alpha=.12,linewidth=.2,edgecolor='#52616b')
        for p in points:
            p=transform(p); ax.plot(p[:,0],p[:,1],color='#c82424',linewidth=1.5)
        bounds=transform(np.asarray([limits_lo,limits_hi]));ax.set(xlim=bounds[:,0],ylim=bounds[:,1],aspect='equal',xlabel='east offset (m)',ylabel='viewer Z offset (m)')
        fig.suptitle(u+' (gold) / '+v+' (blue): every exact original contact in red\nSource-only diagnostic; view crop only; no geometry or approval changes')
        path=out/(u.split('/')[1]+'--'+v.split('/')[1]+'.png');fig.savefig(path,dpi=160);plt.close(fig);refs.append(path)
        results.append(dict(uid=u,peerUid=v,contacts=len(raw),roles=pair['roles'],dimensions=dict(Counter(c['dimension']for c in raw)),contactBounds=[lo.tolist(),hi.tolist()],peerContextFacesShown=int(mask.sum()),completeCompanionFaces=len(triangles[u]),image=str(path.relative_to(ROOT))))
    result=dict(uids=summary['uids'],sourceSHA256ByUid=summary['sourceSHA256ByUid'],rows=results,sourceGeometryChanges=0,physicalAcceptance=False,identityAccepted=False,visualAcceptance=False,installationApproved=False,qualification='Original exact contact points and unchanged source facets, with explicit view-only context crop. All four-world contacts remain in the input receipt. These close views cannot establish common ownership, architectural purpose, terrain clearance, or production browser acceptance.')
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('contact_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-contact-interface-source-close-views',refs,result)
    print(dict(pairs=len(results),installationApproved=False),flush=True)

if __name__=='__main__': main()
