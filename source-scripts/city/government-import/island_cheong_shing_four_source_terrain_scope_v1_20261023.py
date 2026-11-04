"""Bind four reviewed source identities to unchanged private terrain geometry."""
from pathlib import Path
import copy
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-cheong-shing-four-source-terrain-scope-v1-20261023';out=base/batch;local=HERE/'local'/batch;assert not out.exists()and not local.exists();refs=[Path(__file__)];cache={}
    def take(batch,name):
        if batch not in cache:cache[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=ROOT/name if name.startswith('source-scripts/')else base/batch/name;assert digest(p.read_bytes())==cache[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    source='government-xl-island-industrial-paired-surface-binding-v4-20261023';surface=take(source,'summary.json');assert surface['bothEffectiveMembersRequired']and surface['status']=='private-coordinated-surface-validator-passed'
    review=take('government-xl-island-cheong-shing-named-identity-review-v1-20261023','summary.json');assert review['identityAccepted']and review['physicalAccepted']is False and review['installationApproved']is False;required=review['coInstallationRequired'];assert len(required)==4
    selected=take('government-xl-island-cheong-shing-four-original-runtime-v2-20261023','selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selected['rows']}==required
    members=[]
    for m in surface['members']:
        old=take(source,m['candidate']['path']);candidate=copy.deepcopy(old);candidate['meta']['targetUids']=sorted(set(candidate['meta']['targetUids'])|set(required));mesh=candidate['nativeMesh'];mesh.pop('sourceOverlap',None);mesh['source'].pop('coordinatedBoundary',None)
        assert mesh['position']==old['nativeMesh']['position']and mesh['index']==old['nativeMesh']['index']
        for key in ['elev','renderedElev','vegetation','water','w','h','coarseCells']:
            assert candidate.get(key)==old.get(key)
        path=local/(m['member']+'-unbound.json');save(path,candidate);refs.append(path);members.append(dict(member=m['member'],candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),replaces=m['replaces'],geometryUnchanged=True,terrainFaces=len(mesh['index'])//3,previousCandidate=m['candidate']))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==review['currentManifestSHA256']==selected['manifestSHA256'];refs.append(manifest)
    result=dict(uids=sorted(required),members=members,coInstallationRequired=required,terrainGeometryUnchanged=True,status='private-paired-four-source-terrain-scope-metadata',sourceGeometryChanges=0,installationApproved=False,qualification='Add the exact fourth source UID to private terrain target metadata only. All vertices, indices, root cells and sampled elevation/vegetation data unchanged. Old coordinated/overlap proofs removed; fresh binding/validators/current checks still required. Identity approval does not grant physical or publication acceptance.')
    save(out/'summary.json',result);module('four_source_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'four-source-private-terrain-target-metadata-only',refs,result)

if __name__=='__main__':main()
