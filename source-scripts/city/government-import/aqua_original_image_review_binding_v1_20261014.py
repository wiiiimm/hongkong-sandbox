"""Four exact ROOT-inspected staged source exports, not a CLI Boolean."""
from upton_staged_image_review_binding_v1_20261014 import inventory_delta

def validate_review(review,*,job,report_ref,stage_ref,functional_ref,manifest_sha,image_refs):
    assert review['reviewer']=='Codex ROOT'and review['stagedExportsAccepted']is True and review['stagedJobId']==job
    assert review['stagedBrowser']==report_ref and review['sourceStage']==stage_ref and review['acceptedFunctionalReview']==functional_ref and review['currentManifestSHA256']==manifest_sha
    assert review['all4ExportedImagesInspected']is True and review['rawStrictFoundationPassed']is False
    expected={(r['path'],r['sha256'])for r in image_refs};actual=review['imagesActuallyInspected'];assert len(image_refs)==len(expected)==len(actual)==4 and {(r['path'],r['sha256'])for r in actual}==expected
    assert review['ownedUID']=='landsd/193086:0'and review['sourceSHA256']=='d24d090ed2711744be1b4cd326da724a2a17baa5368720c8ac12e7bd42823b91'
    return dict(ROOTStagedImageReviewVerbatim=review,rawStrictFoundationPassed=False,all4StagedExportsInspected=True,stagedImageReviewAccepted=True)

# Exact authorized publisher/ledger progress outputs. Source proofs keep these
# original bytes as history rather than restoring them to pretend still-current.
MUTABLE_CURRENT={'3d-viewer/city/data/manifest.json','docs/astra-city/model-integration-20260909/current-source-review.json','3d-viewer/city/data/building-progress.json','3d-viewer/scripts/building-progress/review-proof.json','3d-viewer/scripts/building-progress/screening-proof.json','docs/astra-city/landmark-completion-audit/neon-snapshot.json'}
