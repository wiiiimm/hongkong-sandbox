"""Fail-closed counterexamples against actual source, parent and review records."""
from copy import deepcopy
from pathlib import Path
import gzip, json
from hkdi88343_installed_parent_contract_v1_20261101 import verify_metadata, UID, PARENT, SHA, PSHA
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'docs/astra-city/government-import'
def read(p):
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())
def main():
    review = read(BASE / 'government-xl-hkdi22089-component-identity-review-v1-20261101/ROOT-COMPONENT-IDENTITY-REVIEW.json')
    original = read(BASE / 'government-xl-hkdi88343-after-one-peking-current-v1-20261101-runtime/selection.json.gz')['rows'][0]['candidate']['entry']
    model = read(ROOT / 'source-scripts/city/government-import/local/government-xl-hkdi88343-after-one-peking-unapproved-preview-v1-20261101/catalogue.json')['models'][0]
    args = [[model], {UID: SHA}, {UID: PARENT}, {UID: original}, {PARENT: deepcopy(review['rawInstalledEntry'])}, review]
    before = deepcopy(args)
    assert verify_metadata(*args) and args == before
    mutations = [
        lambda a: a[0][0].update(verticalPlacementOffsetHKPD=1),
        lambda a: a[0][0].update(rootTranslation=[-834500,1,816500]),
        lambda a: a[0][0].update(partialGeometry=True),
        lambda a: a[0][0].update(embeddedModel={'uid': PARENT}),
        lambda a: a[0][0].update(suppressesBuildingUids=[PARENT]),
        lambda a: a[0][0].update(proceduralWindows=True),
        lambda a: a[0][0]['supportDependencies'][0].update(sha256='0'*64),
        lambda a: a[2].update({UID: 'landsd/89613:0'}),
        lambda a: a[1].update({UID: '0'*64}),
        lambda a: a[4][PARENT].update(recordedBaseHeight=99),
        lambda a: a[4][PARENT].update(identityReviewApproved=True),
        lambda a: a[5].update(sourceComponentIdentityAccepted=False),
        lambda a: a[5].pop('reviewedIdentityProof'),
        lambda a: a[5].update(worldTrianglesSHA256='0'*64),
        lambda a: a[5].update(sourceGeometryChanges=1),
        lambda a: a[5].update(rawIdentityReasonsPreserved=[]),
        lambda a: a[0].append(deepcopy(a[0][0])),
    ]
    for number, mutate in enumerate(mutations, 1):
        candidate = deepcopy(args)
        mutate(candidate)
        try: verify_metadata(*candidate)
        except (AssertionError, KeyError): continue
        raise AssertionError('Counterexample admitted: ' + str(number))
    print(json.dumps(dict(positivePassed=True, counterexamplesRejected=len(mutations), originalInputsUnchanged=args==before)))
if __name__ == '__main__': main()
