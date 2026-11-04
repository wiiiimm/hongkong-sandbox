"""Read-only reconciliation of frozen XL source keys and deployed source revisions.

Catalogue/review membership is not a fresh physical or runtime acceptance check.
Differently packed bytes are never assumed equivalent from matching counts.
"""
from collections import Counter
from pathlib import Path
from run import ROOT, read, save, digest, connect

BASE = ROOT / 'docs/astra-city/government-import'
PRIOR = BASE / 'government-xl-current-fixed-inventory-audit-v1-20261012/inventory.json.gz'
DOC = BASE / 'government-xl-fixed-inventory-binding-reconciliation-v1-20261012'

def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))

def main():
    assert not DOC.exists()
    audit = read(PRIOR)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    by_uid, by_source, refs = {}, {}, [ref(PRIOR), ref(Path(__file__)), ref(manifest)]
    for url in read(manifest)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        refs.append(ref(path))
        for entry in read(path)['models']:
            binding = dict(catalogue=ref(path), entry=entry,
                           assetPath=str((path.parent / entry['asset']).relative_to(ROOT)))
            assert entry['uid'] not in by_uid
            by_uid[entry['uid']] = binding
            by_source.setdefault((entry['modelId'], entry['sha256']), []).append(binding)
    rows = []
    for source in audit['rows']:
        key = (source['modelId'], source['sourceSHA256'])
        matches = by_source.get(key, [])
        assert len(matches) <= 1, 'Ambiguous exact model/source binding'
        installed = matches[0] if matches else by_uid.get(source['uid'])
        if matches:
            state = 'indexed-uid-and-source-installed' if source['uid'] == installed['entry']['uid'] else 'exact-source-installed-with-recovered-uid'
            assert source['uid'] in (None, installed['entry']['uid']), 'Conflicting indexed identity'
        elif installed:
            state = 'installed-different-packed-source' if source['modelId'] == installed['entry']['modelId'] else 'installed-successor-model-revision'
        else:
            state = 'not-installed'
        rows.append(dict(sourceKey=source['cacheKey']+'/'+source['modelId'],
                         indexedUID=source['uid'], indexedModelId=source['modelId'],
                         indexedSourceSHA256=source['sourceSHA256'], state=state,
                         installedBinding=installed,
                         indexedToInstalledGeometryEquivalenceProved=bool(matches),
                         noNewAcceptance=True))
    bound = [r for r in rows if r['installedBinding']]
    uids = sorted({r['installedBinding']['entry']['uid'] for r in bound})
    assert len(rows) == 521 and len(bound) == len(uids) == 233
    with connect() as c:
        c.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        timestamp = c.execute('SELECT transaction_timestamp()').fetchone()[0].isoformat()
        reviews = c.execute("SELECT DISTINCT ON(uid) uid,source_sha256,review_state,result,updated_at FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC,snapshot_id DESC", (uids,)).fetchall()
    reviews = {u:dict(sourceSHA256=s, state=t, result=r, updatedAt=d.isoformat()) for u,s,t,r,d in reviews}
    for row in bound:
        binding = row['installedBinding']; entry = binding['entry']; review = reviews.get(entry['uid'])
        asset = ref(ROOT/binding['assetPath']); assert asset['sha256'] == entry['sha256']
        evidence = None
        matched_review = bool(review and review['state'] == 'installed-verified' and review['sourceSHA256'] == entry['sha256'])
        if matched_review:
            evidence = ref(ROOT/review['result']['evidence'])
            assert evidence['sha256'] == review['result']['sha256']
            refs.append(evidence)
        row.update(currentInstalledReview=review, currentInstalledSourceReviewMatched=matched_review,
                   installedAsset=asset, historicalAcceptanceEvidence=evidence,
                   acceptanceFollowupRequired=not matched_review)
        refs.append(asset)
    for item in refs:
        assert ref(ROOT/item['path']) == item
    counts = dict(Counter(r['state'] for r in rows))
    assert counts == {'indexed-uid-and-source-installed':216,
                      'exact-source-installed-with-recovered-uid':9,
                      'installed-different-packed-source':7,
                      'installed-successor-model-revision':1,
                      'not-installed':288}
    review_counts = dict(Counter('source-review-matched' if r['currentInstalledSourceReviewMatched'] else 'acceptance-followup-required' for r in bound))
    report = dict(rows=rows, counts=counts, installedReviewBindingCounts=review_counts,
                  total=521, installedCurrentUIDRevisions=233,
                  indexedExactSourceAssetsInstalled=225, notInstalled=288,
                  priorAuditPreserved=True, priorStrictUIDAndSourceCount=216,
                  database={**audit['database'], 'readOnlyTransactionTimestamp':timestamp},
                  evidenceRefs=sorted({(r['path'],r['sha256']):r for r in refs}.values(), key=lambda r:r['path']),
                  reviewWrites=0, jobsCreated=0, queueCreated=False, newlyInstalled=0,
                  sourceGeometryChanges=0, qualification='Current catalogue bytes reconcile the reported 233 deployed UID revisions. Nine exact sources had no UID in the frozen index and now appear under recovered UIDs; catalogue membership alone does not establish their acceptance. Missing or mismatched source-review bindings are explicitly flagged for follow-up. Seven same-model packed hashes differ and one successor model ID differs; any matching current installed acceptance is preserved, but equivalence to the old indexed asset is not inferred. Historical acceptance evidence retains its original runtime bindings. This is membership/provenance accounting, not new physical acceptance, corruption or permanent rejection.')
    save(DOC/'reconciliation.json.gz', report)
    save(DOC/'summary.json', {k:v for k,v in report.items() if k not in ('rows','evidenceRefs')})
    print(counts, flush=True)

if __name__ == '__main__':
    main()
