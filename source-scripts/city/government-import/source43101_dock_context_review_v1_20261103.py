"""Record actual whole-source context inspection and reuse complete directory lists."""
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-source43101-dock-context-review-v1-20261103'
CONTEXT = 'government-xl-source43101-dock-contact-context-v1-20261103'
DIRECTORIES = 'government-xl-source43101-fresh-directories-v2-20261103'
COUNTERPARTS = 'government-xl-source43101-root-counterparts-v1-20261029'
LOOKUP = 'government-xl-source43101-dock-native-lookup-v1-20261103'
UIDS = ['landsd/43101:0', 'landsd/316521:0', 'landsd/316522:0']


def owned():
    lease = read(HERE / 'local' / BATCH / 'reservation.json')
    assert reservations.owns(lease)
    refs, pins = [Path(__file__)], {}
    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]; refs.append(BASE / batch / 'result.json')
        p = BASE / batch / name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p); return read(p)
    context = take(CONTEXT, 'summary.json')
    assert context['allSavedContactsExamined'] and context['contactPairs'] == context['bothTrianglesStraddleOtherPlane'] == 72
    assert context['rootStraddleCounts'] == [42, 30] and context['allOriginalFacesShown'] == [24308, 5804]
    for image in context['images']:
        assert digest((ROOT / image['path']).read_bytes()) == image['sha256'] == pins[CONTEXT][image['path']]
        refs.append(ROOT / image['path'])
    counterparts = take(COUNTERPARTS, 'summary.json')
    assert counterparts['sourceSHA256'] == context['sourceSHA256ByUid'][UIDS[0]] and not counterparts['rootsAreExactTranslatedCopies']
    lookup = take(LOOKUP, 'summary.json')
    form = next(r['currentViewerForm'] for r in lookup['rows'] if r['uid'] == UIDS[2])
    assert form['buildingCSUID'] == '4568726811P20250314'
    prefix = 'B' + form['buildingCSUID'][:10]
    directories = take(DIRECTORIES, 'summary.json')
    assert directories['completeBoundedFreshSearch'] and not directories['errors'] and len(directories['rows']) == 4
    searches = []
    for row in directories['rows']:
        assert len(row['completeMembers']) == row['completeEntries'] and len(set(row['completeMembers'])) == row['completeEntries']
        matches = [name for name in row['completeMembers'] if Path(name).name.startswith(prefix)]
        searches.append(dict(family=row['family'], format=row['format'], sheet=row['sheet'], revision=row['revision'],
                             directorySHA256=row['directorySHA256'], completeEntries=row['completeEntries'], exactGeoRefMatches=matches))
    review = dict(reviewer='ROOT', uids=UIDS, sourceSHA256ByUid=context['sourceSHA256ByUid'], images=context['images'],
                  allListedExportsActuallyInspected=True, allOriginalFacesPreserved=[24308, 5804],
                  originalLineContactPairs=72, strictMutualStraddlePairs=72, rootStrictMutualStraddlePairs=[42, 30],
                  rootsAreExactTranslatedCopies=False, exactNewPodiumGeoRefPrefix=prefix, completeCachedDirectorySearch=searches,
                  newHTTPRequests=0, governmentWideAbsenceClaimed=False, CSUIDDateInterpretedAsConstructionDate=False,
                  sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False, sourceEvidenceInterpretationUsedAI=True,
                  identityAccepted=False, physicalAcceptance=False, supportAcceptance=False, collisionExemption=False,
                  installationApproved=False, publication=False, permanentRejection=False,
                  observations='ROOT inspected both whole-original source diagrams. The215degree view shows both complete bridge/stair assemblies extending from the Dock1A context. In the35degree view grey building surfaces obscure portions of them. These whole-scene views do not individually resolve every contact locus; no complete contact-role visual acceptance is claimed. All72saved intersections strictly straddle both original face planes, so they cannot be dismissed as numerical area-count artifacts or simple shared edges. Their architectural/ownership roles remain unresolved. The older exact proof already disproves exact translated copies; do not repeat that claim. The20250314suffix in the newer podium CSUID is metadata, not an established construction date.',
                  nextAction='Retain both roots and every saved contact. Resolve current whole-source/component identity and the72genuine original intersection roles; targeted locus views may reuse saved contacts. The newer podium has no exact prefix in the four explicitly searched cached directories. No repeated directory download is warranted without a new source revision/profile or adjoining source scope. Keep current316522BASIC obligations, four-world/source-ground/foreign/runtime and guarded publication checks.')
    out = BASE / BATCH; save(out / 'ROOT-CONTEXT-INSPECTION.json', review)
    summary = {k: v for k, v in review.items() if k not in ['images', 'observations']}
    summary['review'] = dict(path=str((out / 'ROOT-CONTEXT-INSPECTION.json').relative_to(ROOT)), sha256=digest((out / 'ROOT-CONTEXT-INSPECTION.json').read_bytes()))
    save(out / 'summary.json', summary)
    assert reservations.owns(lease)
    module('source43101_dock_context_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'actual-whole-original-contact-context-and-cached-podium-directory-review', list(dict.fromkeys(refs)), summary)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not (BASE / BATCH).exists() and not (HERE / 'local' / BATCH).exists()
        claim = reservations.claim('source43101-context-review-' + str(uuid.uuid4()), ['building:' + u for u in UIDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], 'Exact source group reservation unavailable'
        execute_reserved(claim['reservation'], HERE / 'local' / BATCH / 'reservation.json', [sys.executable, __file__, '--owned'])
