"""Add complete runtime descriptors to an exact already validated private patch.

No candidate/model bytes or approval flags change. The current replacement owner,
coarse domain, parent and source set must agree exactly before descriptors freeze.
"""
import argparse,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','patch','runtime','resources-plan']:ap.add_argument('--'+k,required=True)
    ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    assert all(n.startswith('government-xl-')and '/'not in n for n in [a.batch,a.patch,a.runtime]);out=BASE/a.batch;assert not out.exists()
    plan=(ROOT/a.resources_plan).resolve();assert plan.is_relative_to(BASE);resources=set(read(plan)['resources'])
    lp=HERE/'local'/(a.batch+'-control')/'reservation.json'
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('validated-patch-runtime-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==resources;refs=[Path(__file__),plan];pins={};receipts={}
    def take(batch,path):
        if batch not in pins:receipts[batch],pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    summary=take(a.patch,BASE/a.patch/'summary.json');assert summary['status']=='private-terrain-validator-passed'
    candidate=summary['candidate'];path=ROOT/candidate['path'];patch=take(a.patch,path);assert digest(path.read_bytes())==candidate['sha256']
    selection=take(a.runtime,BASE/a.runtime/'selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert summary['sourceSHA256ByUid']=={u:sources[u]for u in summary['uids']}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==selection['manifestSHA256']==summary['currentManifestSHA256'];refs.append(manifest)
    parent=ROOT/'3d-viewer'/patch['meta']['parentTerrain'];assert digest(parent.read_bytes())==patch['meta']['parentSha256'];refs.append(parent)
    current={r['url']for r in read(manifest)['terrainPatches']};retained=set();replacements=[]
    for r in summary['replacedNativeTerrain']:
        assert r['url']in current;oldpath=ROOT/'3d-viewer'/r['url'];assert digest(oldpath.read_bytes())==r['sha256'];old=read(oldpath);refs.append(oldpath)
        assert old['meta']['targetUids']==r['targetUids'] and old['coarseCells']==patch['coarseCells']
        assert old['meta']['parentTerrain']==patch['meta']['parentTerrain']and old['meta']['parentSha256']==patch['meta']['parentSha256']
        retained.update(r['targetUids']);replacements.append(dict(r,coarseCells=old['coarseCells']))
        assert 'terrain:'+r['url']in resources
    assert set(patch['meta']['targetUids'])==set(summary['uids'])|retained
    assert {'building:'+u for u in patch['meta']['targetUids']}|{'terrain:city/data/terrain.json'}<=resources
    builder=module('validated_patch_extent',HERE/'resolve_pass_indexed_parent_clipping_v2.py');bounds=builder.extent(patch['coarseCells'],read(parent))
    save(out/'scope.json',dict(uids=summary['uids'],cells=patch['coarseCells'],bounds=bounds,retainedNativeTerrainTargets=sorted(retained),descriptorOnly=True,sourceGeometryChanges=0))
    assert len(replacements) == 1
    old = replacements[0]
    # Existing full-envelope consumer requires this explicit template descriptor.
    # The candidate's entire coarse envelope equals the authenticated old patch;
    # this is not an extension proof or a new geometry/physical approval.
    save(out/'retained-template-proof.json', dict(
        templatePath=old['path'], templateSHA256=old['sha256'],
        coarseCells=patch['coarseCells'], identicalCoarseEnvelope=True,
        sourceGeometryChanges=0, descriptorOnly=True,
        qualification='Exact current native template and equal coarse envelope only; '
        'bounded terrain changes remain governed by the original candidate receipt. '
        'No claim that every terrain face is unchanged, and no acceptance.'))
    context=take(a.patch,BASE/a.patch/'terrain-source-context.json');save(out/'terrain-source-context.json',context)
    result=dict(summary,batch=a.batch,replacedNativeTerrain=replacements,geometryReceipt=dict(path=str((BASE/a.patch/'result.json').relative_to(ROOT)),sha256=digest((BASE/a.patch/'result.json').read_bytes())),runtimeDescriptorsAdded=True,geometryChangedByBinding=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Exact validated private candidate bytes reused, not approval transfer. Added only authenticated coarse bounds/current replacement metadata for existing runtime consumers. Current/retained-native physical, identity, visual and publisher checks still required.')
    save(out/'summary.json',result);assert reservations.owns(lease)and digest(manifest.read_bytes())==mh
    refs.append(HERE/'resolve_pass_indexed_parent_clipping_v2.py');module('validated_retained_runtime_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-private-native-patch-runtime-descriptor-binding',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
