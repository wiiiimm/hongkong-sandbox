"""Durably preserve inspected primary plans and current separate identity states."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BATCH='government-xl-man-fuk-man-oi-primary-relations-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=DOC.parent

def main():
    primary=read(DOC/'diagnostic.json')
    assert len(primary['primary'])==2 and primary['relations']==primary['structures']==[]
    assert primary['capturedManifestSHA256']==digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())
    pins={'ha-man-oi-block-k.pdf':'36ff4cfe483a7aa05ab6b689f1ba817e994764e5366d055de0a4544d94fb8bc2',
          'ha-chun-man-estate-url-probe.pdf':'d2dbcef160489ec1acd81e1ffad11f3d3574a3dec9bcb268311d713bc623ec74'}
    for name,pin in pins.items():assert digest((DOC/name).read_bytes())==pin
    records=[];paths=[Path(__file__),HERE/'xl-man-fuk-man-oi-primary-relations-20261010.py']
    for uid,name in [('landsd/266062:0','government-xl-man-fuk-current-original-preflight-20261010'),
                     ('landsd/75697:0','government-xl-man-oi-current-original-preflight-20261010')]:
        folder=BASE/name;report=read(folder/'indexed-preflight.json')
        assert report['manifestSHA256']==primary['capturedManifestSHA256']
        row=next(r for r in report['rows'] if r['uid']==uid)
        records.append(dict(uid=uid,identityAccepted=row['identity']['passed'],
                            reasons=row['identity']['reasons'],canStartTerrainWork=row['canStartTerrainWork']))
        paths.extend(p for p in folder.rglob('*') if p.is_file())
    assert records[0]['identityAccepted'] is False and records[1]['identityAccepted'] is True
    (DOC/'README.md').write_text('''# Man Fuk and Man Oi active primary evidence

Produced by Codex on10October2026 for HKS-203. Exact active primary records for CSUID3644619608P20050726 (Man Fuk podium) and3647219454T20050430 (Man Oi tower) are preserved with original request/response hashes. Their primary-service OBJECTIDs265843/75645 are namespaced to that service; they are not the viewer/native matching-service UID numbers266062/75697. Stable CSUID/BuildingID/type lineage remains explicit. The exact structure-relation query returns zero records; no shared occupation-permit or legal ownership relation is claimed.

Both downloaded official Housing Authority PDFs were rendered and independently inspected. The initially guessed estate URL returned a real titled “Block Plan / Chun Man Court”, showing BlocksA andK inside the illustrated court. The separate typical plan names Man Oi House asBlockK; the prior saved typical plan identifies Man Fuk asBlockA. These are reference plans, not surveyed precision, platform ownership, terrain or support proof. All original bytes, response metadata, page exports and available extracted text remain. No historical Lantau map reference was used.

Current original-source preflights are separately retained. Man Oi passes identity and can start physical checks. Man Fuk retains exactly two projected-overlap reasons against the neighbouring Man Oi form; source/component envelope interpretation remains pending. The previously proved12 mainbody line interfaces at43.375HKPD are source evidence only, not ground roots or whole-source acceptance. All12821faces/97parts are retained.

Next: complete the bounded platform/counterpart identity interpretation and full current original terrain, foundation, all actors, source support, runtime and staged/live publication checks. No user decision or AI remodelling is required by this checkpoint. No model is installed by this evidence pass.
''')
    save(DOC/'current-dispositions.json',dict(rows=records,primaryPlansInspected=True,
         primaryNamedBlocks=['A','K'],surveyPrecisionClaim=False,legalOwnershipClaim=False,
         occupationPermitRelationEstablished=False,supportAccepted=False,identityAcceptedForPair=False,
         currentHeldReason='bounded-original-platform-counterpart-interpretation-and-current-physical-gates-pending'))
    paths += [BASE/'government-xl-man-fuk-original-investigation-checkpoint-20261010/result.json',
              BASE/'government-xl-man-fuk-man-oi-complete-original-contacts-20261010/diagnostic.json.gz']
    spec=importlib.util.spec_from_file_location('man_fuk_primary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.freeze(BATCH,'exact-active-primary-and-inspected-reference-plans-v1',paths,
        dict(uids=primary['uids'],currentManifestSHA256=primary['capturedManifestSHA256'],
             currentPreflightDispositions=records,primaryPlansInspected=True,
             primaryRelationRecords=0,sourceEvidenceInterpretationUsedAI=True,
             scriptFullAcceptancePassed=False,humanDecisionRequired=False,aiGeometryModellingRequired=False,
             currentHeldReason='bounded-original-platform-counterpart-interpretation-and-current-physical-gates-pending',
             nextStep='Complete original platform/counterpart source interpretation and independent whole-source physical gates; Man Oi physical pass proceeds separately.'))

if __name__=='__main__':main()
