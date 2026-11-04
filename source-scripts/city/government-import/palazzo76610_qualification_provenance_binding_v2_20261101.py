"""Bind unchanged twenty-source qualification to the repaired terrain audit revision."""
import argparse,copy,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';PRIOR=P+'twenty-original-qualification-v1-20261101';REPAIR=P+'terrain-provenance-repair-v1-20261101';BATCH=P+'twenty-original-qualification-v2-20261101'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();lp=HERE/'local'/BATCH/'reservation.json';out=BASE/BATCH;assert not out.exists();q=read(BASE/PRIOR/'ROOT-SOURCE-REVIEW.json');resources=q['leaseResources']
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('palazzo-qualified-provenance-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);refs=[Path(__file__)]
    for batch in [PRIOR,REPAIR]:
        receipt,pins=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    repair=read(BASE/REPAIR/'summary.json');assert repair['fullCanonicalPatchValidatorPassed']and repair['identicalRendererPayloadExcludingProofAnnotation']and repair['sourceBytesAndExpectedSHA256Preserved']and repair['sourceGeometryChanges']==repair['terrainGeometryChanges']==repair['sourcePoseChanges']==0
    before=read(ROOT/repair['originalCandidate']['path']);after=read(ROOT/repair['candidate']['path']);b=copy.deepcopy(before);a=copy.deepcopy(after);b['nativeMesh'].pop('sourceOverlap');a['nativeMesh'].pop('sourceOverlap');assert b==a
    manifest=ROOT/q['currentManifest']['path'];assert digest(manifest.read_bytes())==q['currentManifest']['sha256']
    selection=read(BASE/(P+'twenty-authentic-tin-runtime-v1-20261101')/'selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==q['sourceSHA256ByUid']
    for r in selection['rows']:asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
    result=copy.deepcopy(q);result.update(terrainCandidate=repair['candidate'],priorTerrainCandidate=repair['originalCandidate'],terrainProvenanceRepair=dict(path=str((BASE/REPAIR/'result.json').relative_to(ROOT)),sha256=digest((BASE/REPAIR/'result.json').read_bytes())),terrainRendererPayloadUnchanged=True,sourceModelRevisionUnchanged=True,terrainGeometryChanges=0,qualification=__doc__+' Fresh binding to the repaired derived-terrain artifact. All twenty model bytes/metadata/source poses are unchanged. Every terrain rendering/sampling field is identical; only source-overlap evidence pointer/hash differ, and the new audit restores the exact expected immutable pre-annotation bytes. Full unchanged canonical patch validation passes. Prior image/ground/source evidence remains applicable by exact payload equality; full publisher dryrun, exact qualified-stage lifecycle and live/fenced publication remain required. No optimisation variants or geometry edits.')
    assert reservations.owns(lease);save(out/'ROOT-SOURCE-REVIEW.json',result);save(out/'ROOT-PHYSICAL-REVIEW.json',result);module('palazzo_qualification_provenance_binding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'twenty-original-qualification-exact-repaired-terrain-provenance-binding',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
