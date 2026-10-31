"""An orphan approval permits a fresh retry only for identical verified evidence."""
def verify_retry(review, *, uid, source_sha, prior_path, prior_sha, prior_decision,
                 browser_passed, prior_installed, current_review, prior_released):
 assert prior_released,'Interrupted worker must have released its reservation'
 assert not prior_installed,'Installed work is not an interrupted acceptance'
 assert current_review is None,'Current review decision requires explicit resolution'
 assert browser_passed and prior_decision.get('passed') and prior_decision.get('checksPassed')
 assert prior_decision.get('uids')==[uid] and prior_decision.get('sourceSHA256')==source_sha
 assert review['review_state']=='approved-for-integration' and review['source_sha256']==source_sha
 result=review['result']
 assert result['evidence']==prior_path and result['sha256']==prior_sha
 assert result['source_sha256']==source_sha and not result['productionPublished']
 assert result['effort']['method']=='scripted' and result['effort']['ai_model'] is None
 return {'uid':uid,'sourceSHA256':source_sha,'priorApprovalSnapshot':review['snapshot_id'],
         'priorAcceptance':{'path':prior_path,'sha256':prior_sha},
         'qualification':'Fresh current checks and staged/live browser acceptance remain mandatory. No installed credit or prior decision override.'}
