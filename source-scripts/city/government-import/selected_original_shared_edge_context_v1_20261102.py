"""Measure an entire existing rendered terrain seam; no admission or geometry edits."""
import argparse,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from original_terrain_point_contact_v1_20261025 import extent
from coordinated_native_boundary_v1_20261023 import seam_segments,seam_comparison_report
sys.path.insert(0,str(HERE.parent/'island-detail-integration'))
from coordinated_native_boundary import triangles
BASE=ROOT/'docs/astra-city/government-import'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','scope','patch']:p.add_argument('--'+name,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.scope,a.patch])
    out=BASE/a.batch;lp=HERE/'local'/(a.batch+'-lease')/'reservation.json';assert not out.exists()
    refs=[Path(__file__)];pins={};receipts={}
    def take(batch,path):
        if batch not in pins:receipts[batch],pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    scopepath=BASE/a.scope/'scope.json';scope=take(a.scope,scopepath)
    take(a.patch,BASE/a.patch/'summary.json');candidate=receipts[a.patch]['candidate'];patchpath=ROOT/candidate['path'];patch=take(a.patch,patchpath)
    parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=take(a.patch,parentpath)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifest.read_bytes());assert sha==pins[a.scope][str(manifest.relative_to(ROOT))]==pins[a.patch][str(manifest.relative_to(ROOT))];refs.append(manifest)
    assert scope['positiveAreaTerrainOverlaps']==0 and not scope['touchingNativeUids']
    urls={r['url']for r in read(manifest)['terrainPatches']};old={};resources={'terrain:city/data/terrain.json'}|{'building:'+u for u in scope['uids']}
    for c in scope['terrainContacts']:
        assert c['url']in urls
        path=ROOT/'3d-viewer'/c['url'];old[c['url']]=take(a.scope,path)
        resources.add('terrain:'+c['url']);resources.update('building:'+u for u in old[c['url']]['meta']['targetUids'])
    assert old
    if not a.owned:
        assert not lp.parent.exists();claim=reservations.claim('original-shared-edge-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==resources
    bounds=extent(patch,parent);assert bounds==scope['regionalParentExtent']and not patch.get('patches')and not patch.get('children');newtri=triangles(patch);rows=[];bindings=[]
    for c in scope['terrainContacts']:
        node=old[c['url']];assert not node.get('patches')and not node.get('children')
        other=extent(node,parent);assert other==c['extent']and c['coarseOverlapAreaM2']==0
        assert len(c['packedContacts'])==1 and c['packedContacts'][0]['hierarchy']==[]and c['packedContacts'][0]['overlapAreaM2']==0 and c['packedContacts'][0]['packedBounds']==other
        xlo,xhi=max(bounds[0],other[0]),min(bounds[2],other[2]);zlo,zhi=max(bounds[1],other[1]),min(bounds[3],other[3])
        assert (xlo==xhi and zlo<zhi)or(zlo==zhi and xlo<xhi),'Expected one finite shared edge'
        axis,coordinate,start,end=(0,xlo,zlo,zhi)if xlo==xhi else(2,zlo,xlo,xhi)
        oldtri=triangles(node);left=seam_segments(newtri,axis,coordinate,start,end);right=seam_segments(oldtri,axis,coordinate,start,end)
        comparison=seam_comparison_report(left,right,start,end)
        rows.append(dict(url=c['url'],axis=axis,coordinate=coordinate,interval=[start,end],completeCandidateFaces=len(newtri),completeOldFaces=len(oldtri),candidateFiniteSegments=len(left),oldFiniteSegments=len(right),comparison=comparison))
        path=ROOT/'3d-viewer'/c['url'];bindings.append(dict(url=c['url'],path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    assert reservations.owns(lease)and digest(manifest.read_bytes())==sha
    ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    result=dict(uids=scope['uids'],rows=rows,candidateBinding=candidate,oldTerrainBindings=bindings,scopeBinding=ref(scopepath),parentBinding=ref(parentpath),currentManifestSHA256=sha,allExistingBoundaryComparisonsPassed=all(r['comparison']['passed']for r in rows),sourceGeometryChanges=0,terrainGeometryChanges=0,installationApproved=False,publication=False,admissionGranted=False,qualification='Diagnostic replay of existing complete finite rendered-Float32 seam/upper-envelope checker at its unchanged strict1cm boundary limit. Every kink, interval limit and point is checked, with full coverage required. No point-only guard changed, no coordinated-boundary marker added, no publisher or model acceptance granted.')
    save(out/'summary.json',result);refs.extend([HERE/'coordinated_native_boundary_v1_20261023.py',HERE/'original_terrain_point_contact_v1_20261025.py',HERE.parent/'island-detail-integration/coordinated_native_boundary.py',ROOT/'3d-viewer/city/native-terrain.js'])
    module('original_shared_edge_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-existing-native-shared-edge-diagnostic-no-admission',list(dict.fromkeys(refs)),result)
    print(dict(rows=rows,admissionGranted=False),flush=True)
if __name__=='__main__':main()
