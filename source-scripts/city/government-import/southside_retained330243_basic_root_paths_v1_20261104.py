"""Seek existing strict support anchors for the six actual BASIC fallback warnings.

This preserves the terminal original-source disposition: the procedural BASIC
mesh is a different asset and supplies no support credit to that original tower.
"""
import argparse
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from original_face_attachment_minimax_v2_20261024 import attachment_paths
from pool_incident_wall_contacts_v1_20261017 import closest
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-retained330243-basic-root-paths-v1-20261104'
OUT = BASE/BATCH
LEASE = HERE/'local'/BATCH/'reservation.json'
SUPPORT = 'government-xl-southside-current-basic-original-support-v1-20261104'
CONTEXT = 'government-xl-southside-current-basic-compound-context-v1-20261104'
UID = 'landsd/330243:0'
PODIUM = 'landsd/315025:0'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owned', action='store_true')
    args = p.parse_args()
    assert not OUT.exists()
    if not args.owned:
        assert not LEASE.parent.exists()
        claim = reservations.claim('southside-retained-basic-existing-roots-'+str(uuid.uuid4()), ['building:'+UID, 'building:'+PODIUM, 'terrain:city/data/terrain.json'], batch=BATCH, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])
    lease = read(LEASE)
    assert reservations.owns(lease)
    refs = [Path(__file__)]
    pins = {}

    def take(batch, name):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE/batch)
            refs.append(BASE/batch/'result.json')
        path = BASE/batch/name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    inp = take(SUPPORT, 'input.json.gz')
    checks = take(SUPPORT, 'checks.json.gz')
    context = take(CONTEXT, 'summary.json')
    assert context['sourceSHA256'] == inp['sourceSHA256']
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == inp['currentManifestSHA256'] == context['currentManifestSHA256']
    refs.append(manifest)
    body = [b for b in checks['bodies'] if b['uid']==UID]
    assert len(body)==1
    body = body[0]
    tri = np.asarray(body['position'],dtype='<f8').reshape(-1,3)[np.asarray(body['index']).reshape(-1,3)]
    assert len(tri)==116
    for path, sha in checks['inputHashes'].items():
        assert digest((ROOT/path).read_bytes())==sha
        refs.append(ROOT/path)
    tool = HERE/'original_strict_support_roots_v1_20261024.mjs'
    summaries, done = [], {}
    for mode in inp['supportModes']:
        name = mode['name']
        old = next(r['proof'] for r in checks['rows'] if r['uid']==UID and r['mode']==name)
        clearance = next(r for r in context['rows'] if r['uid']==UID and r['mode']==name)
        assert clearance['establishedFoundationPolicyPassed'] and clearance['exactNegativeFaceCount']==10
        original = take(CONTEXT, UID.split('/')[1]+'-'+name+'.json.gz')
        assert original['sourceWorldSHA256']==digest(tri.tobytes())
        if mode['worldSHA256'] in done:
            source, report = done[mode['worldSHA256']]
            save(OUT/(name+'.json.gz'),dict(**report,mode=name,exactCompleteSupportArrayReusedFromMode=source))
            summaries.append(dict(summaries[-1],mode=name,exactCompleteSupportArrayReusedFromMode=source))
            continue
        podium = np.asarray(mode['geometry']['position'],dtype='<f8').reshape(-1,3)[np.asarray(mode['geometry']['index']).reshape(-1,3)]
        assert digest(podium.tobytes())==mode['worldSHA256']
        path = OUT/(name+'-root-input.json.gz')
        save(path,dict(rows=[dict(uid=UID,position=body['position'],index=body['index'])],podium=podium.tolist()))
        rootpath = OUT/(name+'-strict-roots.json.gz')
        subprocess.run(['node',str(tool),str(path),str(rootpath)],cwd=ROOT,check=True)
        roots = read(rootpath)
        assert roots['inputSHA256']==digest(path.read_bytes()) and roots['strict']==old['strictLowRim']
        low, high = tri.min(1), tri.max(1)
        real = np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)>0

        def incident(point):
            point = np.asarray(point)
            candidates = np.flatnonzero(real & np.all(low<=point+.001,axis=1) & np.all(high>=point-.001,axis=1))
            result = [int(i) for i in candidates if np.linalg.norm(closest(point,tri[i])-point)<=.001]
            assert result
            return result

        anchors = [dict(root,incidentFaces=incident(root['position'])) for root in roots['roots'] if root['strictAccepted']]
        assert len(anchors)==old['strictContacts']==430
        targets = [dict(witness=w,incidentFaces=incident(w['position'])) for w in old['unresolved']]
        assert len(targets)==6
        paths = attachment_paths(tri,dict(targets=targets,proof=dict(contacts=[])),[],strict_anchors=anchors)
        report = dict(uid=UID,basicWorldSHA256=digest(tri.tobytes()),supportWorldSHA256=mode['worldSHA256'],canonicalStrictAnchors=len(anchors),rows=paths,noIntercomponentJoins=True,sourceOriginalTowerSupportApproved=False,installationApproved=False)
        save(OUT/(name+'.json.gz'),dict(report,mode=name))
        summary = dict(mode=name,strictAnchors=len(anchors),targets=6,finiteAttachmentPaths=sum(r['hasUnrestrictedFiniteAttachment'] for r in paths),pathsWithinExistingEndpointCeiling=sum(r.get('passesExistingEndpointHeight',False) for r in paths),exactNegativeFacesPreserved=10,ordinaryFoundationPolicyPassed=True,supportApproved=False)
        done[mode['worldSHA256']] = name, report
        summaries.append(summary)
        print(summary,flush=True)
        assert reservations.owns(lease)
    refs += [tool,HERE/'original_face_attachment_minimax_v2_20261024.py',HERE/'pool_incident_wall_contacts_v1_20261017.py']
    result = dict(uids=[PODIUM],retainedBasicUid=UID,rows=summaries,rawOriginalTowerTerminalDispositionUnchanged=True,basicAndOriginalAreDifferentAssets=True,rawGroundGapAndSupportFailuresPreserved=True,originalTowerSupportApproved=False,retainedBasicSupportApproved=False,physicalAccepted=False,installationApproved=False,geometryChanges=0,qualification=__doc__+' Complete actual unchanged BASIC faces use the existing strict canonical podium roots and source-edge/endpoint/incidence kernel. Every10 exact finite negative face and6 direct-support warning remains. Root paths alone do not approve synthetic bottom-closure roles, full current neighbour scope, runtime fallback or publication.')
    save(OUT/'summary.json',result)
    assert reservations.owns(lease)
    module('southside_retained_basic_existing_roots_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'actual-basic-fallback-existing-strict-root-paths',list(dict.fromkeys(refs)),result)


if __name__=='__main__':
    main()
