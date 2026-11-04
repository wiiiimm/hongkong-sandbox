"""Repair a self-referencing terrain audit using exact pre-annotation bytes only."""
import argparse,copy,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from fuying_five_member_terrain_stage_v1_20261029 import complete_boundary_validators
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-academic309823-after-kai-tak-';ORIGINAL='government-xl-after-disneyland-piers-academic309823-native-inset-v3-20261030';BATCH=P+'terrain-provenance-repair-v1-20261101'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();lp=HERE/'local'/BATCH/'reservation.json';out=BASE/BATCH
    planpath=BASE/(P+'terrain-and-runtime-plan-v1-20261101.json');resources=read(planpath)['resources']
    if not a.owned:
        assert not out.exists();c=reservations.claim('academic-terrain-provenance-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and not out.exists();receipt,pins=authenticate(BASE/ORIGINAL);summary=read(BASE/ORIGINAL/'summary.json');original=ROOT/summary['candidate']['path'];assert digest(original.read_bytes())==pins[str(original.relative_to(ROOT))]==summary['candidate']['sha256'];before=read(original);approval=before['nativeMesh']['sourceOverlap'];auditpath=ROOT/approval['evidencePath'];assert digest(auditpath.read_bytes())==approval['evidenceSHA256']==pins[str(auditpath.relative_to(ROOT))];audit=read(auditpath)
    publisher=module('palazzo_terrain_provenance_publisher',HERE.parent/'island-detail-integration/publish.py');plain=copy.deepcopy(before);plain['nativeMesh'].pop('sourceOverlap');raw=publisher.encoded(plain);expected='0de6e202300795d9a0f452012c1718b1bb2c3b296249c73cfa039cbff2990d28';assert digest(raw)==expected==audit['stagedGeometrySha256']
    old_source_path=BASE/ORIGINAL/'unapproved-terrain.json';assert old_source_path.read_bytes()==original.read_bytes()and digest(old_source_path.read_bytes())==pins[str(old_source_path.relative_to(ROOT))]
    matches=[r for r in audit['source']['files']if r['path']==str(old_source_path.relative_to(ROOT))];assert len(matches)==1 and matches[0]['sha256']==expected
    out.mkdir();archive=out/'terrain-before-overlap-annotation.json';archive.write_bytes(raw);archive.chmod(0o444);assert digest(archive.read_bytes())==expected
    fixed_audit=copy.deepcopy(audit)
    for source in fixed_audit['source']['files']:
        if source['path']==str(old_source_path.relative_to(ROOT)):source['path']=str(archive.relative_to(ROOT))
        path=ROOT/source['path'];assert digest(path.read_bytes())==source['sha256']
    fixed_audit_path=out/'highest-surface-proof.json';save(fixed_audit_path,fixed_audit);candidate=copy.deepcopy(before);candidate['nativeMesh']['sourceOverlap'].update(evidencePath=str(fixed_audit_path.relative_to(ROOT)),evidenceSHA256=digest(fixed_audit_path.read_bytes()));candidatepath=out/'candidate-terrain.json';save(candidatepath,candidate)
    after_plain=copy.deepcopy(candidate);after_plain['nativeMesh'].pop('sourceOverlap');assert publisher.encoded(after_plain)==raw and candidate['nativeMesh']['position']==before['nativeMesh']['position']and candidate['nativeMesh']['index']==before['nativeMesh']['index']
    proof_before=copy.deepcopy(audit);proof_after=copy.deepcopy(fixed_audit);proof_before['source']['files']=proof_after['source']['files'];assert proof_before==proof_after
    with complete_boundary_validators():publisher.validate_patch(candidate,read(ROOT/'3d-viewer/city/data/terrain.json'))
    assert digest(original.read_bytes())==summary['candidate']['sha256']and digest(auditpath.read_bytes())==approval['evidenceSHA256']and reservations.owns(lease)
    result=dict(uids=receipt['uids'],originalCandidate=summary['candidate'],candidate=dict(path=str(candidatepath.relative_to(ROOT)),sha256=digest(candidatepath.read_bytes())),exactPreAnnotationSHA256=expected,immutablePreAnnotationSource=dict(path=str(archive.relative_to(ROOT)),sha256=expected),identicalRendererPayloadExcludingProofAnnotation=True,onlyCandidateFieldsChanged=['nativeMesh.sourceOverlap.evidencePath','nativeMesh.sourceOverlap.evidenceSHA256'],onlyAuditFieldChanged='source.files[matching-old-candidate].path',sourceBytesAndExpectedSHA256Preserved=True,fullCanonicalPatchValidatorPassed=True,sourceGeometryChanges=0,terrainGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,qualification=__doc__+' Original frozen candidate/audit remain untouched. Exact canonical pre-annotation bytes reproduce BOTH recorded source SHA and stagedGeometrySha256. A new audit points to that immutable archive at the same expected SHA; only the new candidate audit pointer/hash change. Full unmodified canonical patch validation passes; every renderer/source/cell/hydro/index/position field is identical. No guard bypass or model/terrain modelling.')
    oldscope=BASE/ORIGINAL/'scope.json';assert digest(oldscope.read_bytes())==pins[str(oldscope.relative_to(ROOT))];(out/'scope.json').write_bytes(oldscope.read_bytes())
    origin=BASE/'government-xl-after-disneyland-piers-next-three-current-ground-v1-20261030/selection.json.gz';assert digest(origin.read_bytes())==pins[str(origin.relative_to(ROOT))]
    parentpath=ROOT/'3d-viewer/city/data/terrain.json';assert digest(parentpath.read_bytes())==pins[str(parentpath.relative_to(ROOT))]
    result.update(status='private-terrain-validator-passed',sourceSHA256ByUid=receipt['sourceSHA256ByUid'],terrainTriangles=len(candidate['nativeMesh']['index'])//3,historicalConstructionScopeOnly=True,identityAccepted=False,physicalAcceptance=False)
    save(out/'summary.json',result);refs=[Path(__file__),planpath,oldscope,out/'scope.json',origin,old_source_path,BASE/ORIGINAL/'result.json',BASE/ORIGINAL/'summary.json',original,auditpath,archive,fixed_audit_path,candidatepath,HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/native_terrain_validation.py',HERE/'fuying_five_member_terrain_stage_v1_20261029.py',ROOT/'3d-viewer/city/data/terrain.json']+[ROOT/r['path']for r in fixed_audit['source']['files']];module('palazzo_terrain_provenance_repair_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-immutable-pre-annotation-terrain-audit-reference-repair',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
