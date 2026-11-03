"""Batch failed exposed-grade paths against their existing verified roots."""
import argparse, sys, uuid
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_endpoint_root_retry_grouped_v1_20261103 import retry_paths
from original_endpoint_root_retry_v1_20261102 import passed


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch','uid','prior','runtime','attributes','resources-plan']:
        p.add_argument('--'+key, required=True)
    p.add_argument('--owned', action='store_true'); a = p.parse_args()
    base = ROOT/'docs/astra-city/government-import'; out = base/a.batch
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch,a.prior,a.runtime,a.attributes])
    pp = (ROOT/a.resources_plan).resolve(); assert pp.is_relative_to(base)
    resources = read(pp)['resources']; assert {'building:'+a.uid,'terrain:city/data/terrain.json'} <= set(resources)
    lp = HERE/'local'/a.batch/'reservation.json'
    if not a.owned:
        assert not out.exists() and not lp.parent.exists()
        c = reservations.claim('existing-grade-endpoint-retry-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease = read(lp); assert reservations.owns(lease) and set(lease['resources']) == set(resources)
    refs, pins = [Path(__file__),pp], {}
    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(base/batch)[1]; refs.append(base/batch/'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    selection = take(a.runtime,base/a.runtime/'selection.json.gz')
    source = next(r for r in selection['rows'] if r['uid'] == a.uid)
    attrs = take(a.attributes,base/a.attributes/'attributes.json.gz'); assert attrs['startEndAllInputsVerified']
    attr = next(r for r in attrs['rows'] if r['uid'] == a.uid)
    g = next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows'] if r['uid'] == a.uid)
    asset = ROOT/source['candidate']['path']; assert digest(asset.read_bytes()) == source['sourceSHA256'] == attr['sourceSHA256'] == g['sourceSHA256']; refs.append(asset)
    worlds = represented(attr,decode_original_world_triangles(asset.read_bytes()))
    ground = np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3); rows = []
    prior_summary = take(a.prior,base/a.prior/'summary.json'); assert prior_summary['uids'] == [a.uid] and prior_summary['sourceSHA256'] == source['sourceSHA256']
    for mode, tri in worlds.items():
        assert reservations.owns(lease)
        old = take(a.prior,base/a.prior/(mode+'.json.gz'))
        assert old['sourceWorldSHA256'] == digest(tri.astype('<f8').tobytes()) and old['completeGroundSHA256'] == digest(ground.tobytes())
        anchors = old['acceptedOriginalWallRoots']; assert anchors
        verified = {(r['sourceFace'],tuple(r['position'])):r for r in old['completeRootReplays'] if r['accepted']}
        for anchor in anchors:
            assert len(anchor['incidentFaces']) == 1
            replay = verified[anchor['incidentFaces'][0],tuple(anchor['position'])]
            assert F(-1,10) <= F(replay['exactGapM']) <= 1 and anchor['strictAccepted'] is True
            assert min(F(r['proof']['exactMinimumFiniteColumnGapM']) for r in replay['completeGroundProofs']) == F(replay['exactGapM'])
        paths, attempts = retry_paths(tri,old['rows'],anchors)
        assert len(paths) == len(old['rows']) and [r['witness'] for r in paths] == [r['witness'] for r in old['rows']]
        result = dict(mode=mode,sourceWorldSHA256=old['sourceWorldSHA256'],completeGroundSHA256=old['completeGroundSHA256'],previousRows=old['rows'],rows=paths,attempts=attempts,nonrenderingOnlyWarnings=old['nonrenderingOnlyWarnings'],rawCanonicalWarningIndices=old['rawCanonicalWarningIndices'],existingVerifiedRoots=anchors,physicalAcceptance=False)
        save(out/(mode+'.json.gz'),result)
        rows.append(dict(mode=mode,renderingWarnings=len(paths),previousEndpointFailures=sum(not passed(r) for r in old['rows']),remainingEndpointFailures=sum(not passed(r) for r in paths),rootAttempts=len(attempts),sharedGraphBuilds=len({r['anchorIndex'] for r in attempts}),allPathsPass=all(passed(r) for r in paths)))
        print(rows[-1],flush=True)
    manifest = ROOT/'3d-viewer/city/data/manifest.json'; assert digest(manifest.read_bytes()) == selection['manifestSHA256']; refs.append(manifest)
    assert reservations.owns(lease)
    refs.extend(HERE/n for n in ['original_endpoint_root_retry_v1_20261102.py','original_endpoint_root_retry_grouped_v1_20261103.py','original_face_attachment_minimax_v2_20261024.py','original_assembly_four_world_pair_context_v3_20261101.py','exact_packed_world_geometry_20261009.py'])
    summary = dict(uids=[a.uid],sourceSHA256=source['sourceSHA256'],rows=rows,allFourCanonicalRenderingPathsPass=all(r['allPathsPass'] for r in rows),sourceGeometryChanges=0,sourcePoseChanges=0,newRootsCreated=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' Original failed rows retained; stop after the first complete passing witness per target. Every root, gap interval, original endpoint ceiling and1mm source-incidence check is unchanged.')
    save(out/'summary.json',summary)
    module('existing_grade_endpoint_retry_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'existing-verified-original-grade-endpoint-alternative-path-diagnostic',refs,summary)


if __name__ == '__main__': main()
