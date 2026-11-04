"""Authenticate ROOT's exact staged-image review; no acceptance by CLI Boolean."""

def validate_review(review, *, job, report_ref, stage_ref, functional_ref,
                    manifest_sha, image_refs):
    assert review['reviewer']=='Codex ROOT'
    assert review['stagedExportsAccepted'] is True
    assert review['stagedJobId']==job
    assert review['stagedBrowser']==report_ref and review['sourceStage']==stage_ref
    assert review['acceptedFunctionalReview']==functional_ref
    assert review['currentManifestSHA256']==manifest_sha
    assert review['all12ExportedImagesInspected'] is True
    assert review['strictOriginalInterfacePassed'] is False
    expected={(q['path'],q['sha256'])for q in image_refs}
    actual=review['imagesActuallyInspected']
    assert len(image_refs)==len(expected)==len(actual)==12
    assert {(q['path'],q['sha256'])for q in actual}==expected
    return dict(ROOTStagedImageReviewVerbatim=review,strictInterfacePassed=False,
                all12StagedExportsInspected=True,stagedImageReviewAccepted=True)

def inventory_delta(previous, models, *, manifest_sha, snapshot):
    assert previous['manifestSHA256']==manifest_sha and previous['snapshotId']==snapshot
    rows=previous['rows'];assert len(rows)==len({r['sourceKey']for r in rows})==previous['counts']['total']==521
    known=[r for r in rows if r['uid']is not None];assert len(known)==len({r['uid']for r in known});assert all(not r['installedVerified']for r in rows if r['uid']is None)
    assert sum(r['installedVerified']for r in rows)==previous['counts']['installedVerified']
    by_uid={r['uid']:r for r in known};new=[]
    for m in models:
        if m['uid']in by_uid:
            r=by_uid[m['uid']];assert not r['installedVerified']
            assert r['indexedSourceSHA256']==m['sha256']
            new.append(m['uid'])
    return dict(returnedModels=len(models),fixedXLTotal=521,newFixedXLUids=new,
                expectedFixedXLDelta=len(new),previousInstalled=previous['counts']['installedVerified'])
