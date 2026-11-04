"""Reconcile original installed approval history without changing catalogue flags."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-parkview-podium-flag-audit-v2-20261020';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;UID='landsd/254491:0'
assert not DOC.exists()
catpath=ROOT/'3d-viewer/city/data/official-models/government-xxl-parkview-20260913/catalogue.json';cat=read(catpath);entries=[e for e in cat['models']if e['uid']==UID];assert len(entries)==1;entry=entries[0]
pointerpath=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointerpath)
old=BASE/'government-xxl-20260911/second-pass/fourth-pass/parkview';acceptance=read(old/'installed-acceptance.json');decision=read(old/'decision.json')
assert digest(catpath.read_bytes())==acceptance['catalogueSHA256']==decision['catalogueSHA256']=='b6847cf99be9220c54a48589b579d22d4191e035b6cd85c67d5cf5507450dcf9'
assert entry['publicationApproved']is False and entry['placementReviewed']is True and entry['sourceIdentityReviewed']is True and entry['identityReviewApproved']is True
refs=[Path(__file__),catpath,pointerpath,old/'installed-acceptance.json',old/'decision.json']
for key,file in [('metricsSHA256','metrics.json'),('validationSHA256','validation.json'),('stagedBrowserSHA256','staged-browser.json'),('liveBrowserSHA256','live-browser.json')]:
 p=old/file;assert digest(p.read_bytes())==acceptance[key];refs.append(p)
p=ROOT/acceptance['deterministicBundledFormReview']['path'];assert digest(p.read_bytes())==acceptance['deterministicBundledFormReview']['sha256'];assert read(p)['passed']and not read(p)['reasons'];refs.append(p)
asset=catpath.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256']==acceptance['sourceSHA256'];refs.append(asset)
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 r=c.execute('SELECT review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],UID)).fetchone();assert r[0]=='installed-verified'and r[1]==entry['sha256'];assert r[2]['sha256']==digest((old/'installed-acceptance.json').read_bytes())
 events=c.execute('SELECT id,review_state,created_at FROM astra_modelling.model_review_events WHERE uid=%s ORDER BY id',(UID,)).fetchall();assert [e[1]for e in events]==['held','approved-for-integration','installed-verified'];assert events[-1][0]==1032
assert read(pointerpath)==pointer and digest(catpath.read_bytes())==acceptance['catalogueSHA256']
report=dict(uid=UID,sourceSHA256=entry['sha256'],catalogueSHA256=acceptance['catalogueSHA256'],snapshotId=pointer['snapshotId'],reviewState=r[0],reviewHistory=[dict(id=e[0],state=e[1],createdAt=str(e[2]))for e in events],sameCatalogueAsInstalledAcceptance=True,noLaterHoldOrRejection=True,legacyCatalogueFlagFalse=True,evidenceBackedOriginalApprovalReconciliation=True,catalogueChanged=False,optimisationApproval=False,installationCountDelta=0,basis='The exact current catalogue, including its false publication flag, is the catalogue bound to approved and installed original-source evidence. All bound source, metric, validation, staged and live browser evidence hashes verify. The authoritative review history contains an initial held state followed by approval and installation, with no subsequent rejection. This supports a guarded metadata correction for this exact original source only; it does not approve derived assets or transfer approval to changed bytes.')
save(DOC/'audit.json',report)
module('parkview_podium_flag_audit_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'installed-original-approval-flag-history-audit',refs,dict(uids=[UID],evidenceBackedOriginalApprovalReconciliation=True,catalogueChanged=False,installationCountDelta=0))
