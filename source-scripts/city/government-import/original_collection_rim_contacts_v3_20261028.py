"""Canonical rim diagnostics with actual drawn terrain and exact surveyed support.

All source faces are retained. A geometric contact with an unapproved peer is
not a support root; this deliberately grants no physical/installation credit.
The explicit current scene composition does not approve dependency chains.
"""
import argparse
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--capture', required=True)
    parser.add_argument('--attributes', required=True)
    parser.add_argument('--resources-plan', required=True)
    parser.add_argument('--basic-probe', required=True)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT/'docs/astra-city/government-import'
    doc, local = base/args.batch, HERE/'local'/args.batch
    lease_path = local/'reservation.json'
    capture = base/args.capture
    _, pins = authenticate(capture)
    selection_path = capture/'selection.json.gz'
    assert digest(selection_path.read_bytes()) == pins[str(selection_path.relative_to(ROOT))]
    selection = read(selection_path)
    rows = selection['rows']
    attrdoc=base/args.attributes
    _,ap=authenticate(attrdoc)
    attrpath=attrdoc/'attributes.json.gz'
    assert digest(attrpath.read_bytes())==ap[str(attrpath.relative_to(ROOT))]
    attrdata=read(attrpath);assert attrdata['startEndAllInputsVerified']
    attrs={r['uid']:r for r in attrdata['rows']}
    assert set(attrs)=={r['uid']for r in rows}
    assert 1 < len(rows) <= 20 and len({r['uid'] for r in rows}) == len(rows)
    resources_path = (ROOT/args.resources_plan).resolve()
    assert resources_path.is_relative_to(base) and resources_path.is_file()
    resource_plan = read(resources_path)
    assert set(resource_plan['uids']) == set(attrs)
    resources = set(resource_plan['resources'])
    assert {'building:'+uid for uid in attrs} <= resources
    assert 'terrain:city/data/terrain.json' in resources
    geometry_path = HERE/'local'/args.capture/'runtime-geometry.json.gz'
    assert digest(geometry_path.read_bytes()) == pins[str(geometry_path.relative_to(ROOT))]
    runtime = {r['uid']:r for r in read(geometry_path)['rows']}
    assert set(runtime) == set(attrs)
    basicdoc = base/args.basic_probe
    _, bp = authenticate(basicdoc)
    def basic_take(name):
        path = basicdoc/name
        assert digest(path.read_bytes()) == bp[str(path.relative_to(ROOT))]
        return read(path)
    basic_summary = basic_take('summary.json')
    basic_input = basic_take('support-input.json')
    basic_geometry = basic_take('support-attributes.json.gz')
    assert basic_summary['supportBasicBeforeAfterClear'] is True
    assert basic_summary['candidateUid'] in attrs
    assert basic_summary['supportUid'] not in attrs
    assert basic_input['uid'] == basic_summary['supportUid']
    assert basic_input['csuid'] == basic_summary['supportCSUID']
    assert 'building:'+basic_summary['supportUid'] in resources
    for path,sha in basic_geometry['inputHashes'].items():
        assert digest((ROOT/path).read_bytes()) == sha
    if not args.owned:
        assert not doc.exists() and not local.exists()
        claim = reservations.claim('original-collection-rim-'+str(uuid.uuid4()),
            sorted(resources), batch=args.batch, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], lease_path, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(lease_path)
    assert reservations.owns(lease) and resources <= set(lease['resources']) and not doc.exists()
    tool = HERE/'original_neighbour_rim_contacts_v1_20261028.mjs'
    refs = [Path(__file__), tool, capture/'result.json', selection_path, attrdoc/'result.json',attrpath,
            HERE/'exact_packed_world_geometry_20261009.py', resources_path, geometry_path,
            basicdoc/'result.json',basicdoc/'summary.json',basicdoc/'support-input.json',basicdoc/'support-attributes.json.gz',
            *[ROOT/p for p in basic_geometry['inputHashes']]]
    triangles, sources = {}, {}
    for row in rows:
        path = ROOT/row['candidate']['path']
        raw = path.read_bytes()
        assert digest(raw) == row['sourceSHA256']
        tri = decode_original_world_triangles(raw)
        assert len(tri) == row['triangles'] and np.isfinite(tri).all()
        attr=attrs[row['uid']];assert attr['sourceSHA256']==row['sourceSHA256']
        ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        worlds=dict(original=tri,**{mode:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
        assert all(len(v)==row['triangles'] and np.isfinite(v).all()for v in worlds.values())
        captured = runtime[row['uid']]
        assert captured['sourceSHA256'] == row['sourceSHA256']
        literal = np.asarray(captured['position'],dtype='<f8').reshape(-1,3)[np.asarray(captured['index']).reshape(-1,3)]
        assert np.array_equal(literal,worlds['literal'])
        if row['uid'] == basic_summary['candidateUid']:
            assert row['sourceSHA256'] == basic_summary['sourceSHA256']
        triangles[row['uid']] = worlds
        sources[row['uid']] = dict(uid=row['uid'], sourceSHA256=row['sourceSHA256'],
            sourceKey=row['native']['cacheKey']+'/'+row['modelId'], faces=len(tri),
            originalWorldSHA256=digest(tri.astype('<f8').tobytes()))
        refs.append(path)
    inputs, support_rosters = [], {}
    geometry = lambda tri: dict(position=tri.reshape(-1).tolist(), index=list(range(tri.size//3)))
    for uid in sorted(triangles):
        for mode in ['original','literal','leftF32','balancedF32']:
            roster, parts, offset = [], [], 0
            for other in sorted(set(triangles)-{uid}):
                part = triangles[other][mode]
                roster.append(dict(uid=other, sourceSHA256=sources[other]['sourceSHA256'],
                    sourceFaceRange=[offset, offset+len(part)], originalFaces=len(part)))
                parts.append(part); offset += len(part)
            ground = np.asarray(runtime[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
            assert len(ground) and np.isfinite(ground).all()
            roster.append(dict(kind='actual-drawn-terrain',sourceFaceRange=[offset,offset+len(ground)],
                               geometrySHA256=digest(ground.tobytes()),structuralRootAccepted=False))
            parts.append(ground);offset += len(ground)
            if uid == basic_summary['candidateUid']:
                podium = np.asarray(basic_geometry['position'],dtype='<f8').reshape(-1,3)[np.asarray(basic_geometry['index']).reshape(-1,3)]
                assert np.isfinite(podium).all()
                roster.append(dict(kind='surveyed-basic-podium',uid=basic_summary['supportUid'],
                    sourceFaceRange=[offset,offset+len(podium)],geometrySHA256=digest(podium.tobytes()),
                    currentFormSHA256=digest(__import__('json').dumps(basic_input['building'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()),
                    structuralRootAccepted=False))
                parts.append(podium);offset += len(podium)
            peer = np.concatenate(parts)
            own = triangles[uid][mode]
            support_rosters[uid] = roster
            inputs.append(dict(uid=uid, mode=mode, source=geometry(own), support=geometry(peer),
                sourceMinimumY=float(own[:, :, 1].min()), sourceWorldSHA256=digest(own.astype('<f8').tobytes()),
                supportWorldSHA256=digest(peer.astype('<f8').tobytes())))
    save(doc/'input.json.gz', dict(rows=inputs))
    proc = subprocess.run(['node', str(tool), str((doc/'input.json.gz').relative_to(ROOT)),
        str((doc/'contacts.json.gz').relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True)
    save(doc/'command.json', dict(exitCode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr))
    assert proc.returncode == 0
    report = read(doc/'contacts.json.gz')
    assert {(r['uid'],r['mode'])for r in report['rows']}=={(uid,mode)for uid in triangles for mode in ['original','literal','leftF32','balancedF32']} and len(report['rows'])==len(rows)*4
    for path, sha in report['inputHashes'].items():
        assert digest((ROOT/path).read_bytes()) == sha
        refs.append(ROOT/path)
    summary_rows = [{k:v for k,v in row.items() if k not in ['rawInterface','mapped']} for row in report['rows']]
    out = dict(uids=sorted(triangles), rows=summary_rows, sourceScopes=sources, supportRosters=support_rosters,
        sourceGeometryChanges=0, allOtherOriginalFacesIncluded=True, selfSupportExcluded=True,
        terrainIncluded=True, surveyedBasicSupportIncluded=True, structuralRootsAccepted=False, identityAccepted=False, physicalAccepted=False, currentSceneSupportAccepted=False,
        installationApproved=False,
        qualification='Unchanged canonical footing/interface kernel; every source measured against every complete OTHER original in the explicit collection, with source-face range provenance. Each own model has its exact current drawn terrain; Rex additionally has its separately authenticated full surveyed BASIC podium. Only the explicit retained BASIC form is included, never a replaced candidate extrusion. Peers, terrain roots and dependency chains remain unapproved. A passing contact row therefore cannot grant a structural root, solve a support cycle, clear raw ground/identity/foreign warnings or authorise installation.')
    save(doc/'summary.json', out)
    assert reservations.owns(lease)
    module('original_collection_rim_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'complete-current-ground-peer-and-surveyed-basic-four-world-rim-diagnostic', list(dict.fromkeys(refs)), out)
    print(summary_rows, flush=True)


if __name__ == '__main__':
    main()
