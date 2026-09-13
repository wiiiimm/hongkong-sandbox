"""Validate explicit identity decisions and emit review candidates, never publish."""
import json,pathlib,hashlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/identity-hold-review'
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
decisions=read(HERE/'decisions.json');audit=read(DOC/'audit.json');browser=read(DOC/'browser/report.json');cpu=read(DOC/'cpu-validation.json');cat=read(HERE/'candidates/catalogue.json')
assert len(audit['rows'])==9 and len(audit['nonGovernmentEntries'])==8
assert len(browser['views'])==29 and not browser['errors'];assert cpu['checksPassed']==5 and not cpu['exceptions']
assert all(v['activeUIDs']==v['uids'] and all(p['uid']==p['hitUid']for p in v['picking']) for v in browser['views']if v['phase']=='after')
assert all(c['csuidUnchanged'] and c['baseTopUnchanged'] and c['intersectionOverLargerArea']>.999 for c in audit['currentGovernmentFootprints'])
for row in audit['rows']:
 for rel,digest in row['sourceHashes'].items():assert sha((ROOT/row['sourceManifest']).parent/rel)==digest
allowed={d['uid']:d for d in decisions['decisions']if d['identityApproved']};assert set(allowed)=={m['uid']for m in cat['models']}
for m in cat['models']:
 src=HERE/'candidates'/m['asset'];assert sha(src)==m['sha256'];m.update(identityReviewApproved=True,publicationApproved=False,placementReviewed=False,identityReviewIssue='HKS-214',identityReview=allowed[m['uid']]['basis'],remainingReview=allowed[m['uid']]['remaining']);dest=HERE/'identity-approved'/m['asset'];dest.parent.mkdir(exist_ok=True);shutil.copyfile(src,dest)
cat['area']='Five identity-resolved native candidates; physical acceptance pending';save(HERE/'identity-approved/catalogue.json',cat);save(HERE/'identity-approved/catalogue-index.json',{'models':5,'catalogues':['catalogue.json']})
inputs=[HERE/'decisions.json',DOC/'audit.json',DOC/'center.json',DOC/'live-footprints.json',DOC/'live-footprints-provenance.json',DOC/'cpu-validation.json',DOC/'browser/report.json',HERE/'candidates/catalogue.json']
for v in browser['views']:assert sha(DOC/'browser'/v['file'])==v['sha256']
report={**decisions,'counts':{'reviewedGovernmentMatchingHolds':9,'identityResolvedCandidates':5,'retainedIdentityOrCoverageHolds':4,'OSMGlassPartsClassified':8,'browserViews':29,'cpuAcceptedCandidates':5,'newPublishedModels':0},'inputHashes':{str(p.relative_to(ROOT)):sha(p)for p in inputs},'approvedCatalogue':str((HERE/'identity-approved/catalogue.json').relative_to(ROOT)),'catalogueSHA256':sha(HERE/'identity-approved/catalogue.json'),'sharedDatabaseWrites':0,'sourceGeometryEdited':False,'verticalScale':1,'limitations':['Identity approval is a separate stage from ground/support/material and whole-landmark acceptance.','The8 OSM parts cannot be assigned fabricated government CSUIDs; no component deletion is authorised.','Initial Langham NE capture encountered camera collision; final review uses useful SW views. Aigburth SW is obscured; NE is useful.','Mobile is390x844 Chromium emulation, not physical iOS/Android performance acceptance.']}
save(DOC/'decisions.json',report);print(json.dumps(report['counts']))
