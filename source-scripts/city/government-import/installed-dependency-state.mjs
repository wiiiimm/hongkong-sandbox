/** Resolve historical dependency labels against exact current installed evidence. */
export function installedDependencyState(dependency, support, proof) {
 const base={uid:dependency?.uid,declaredState:dependency?.state,effectiveState:null,passed:false};
 if(!dependency||!support||!proof)return {...base,reason:'installed-dependency-evidence-unavailable'};
 if(!['candidate','installed'].includes(dependency.state))return {...base,reason:'explicit-dependency-state-not-reusable'};
 if(dependency.uid!==support.uid||proof.uid!==support.uid)return {...base,reason:'dependency-uid-mismatch'};
 if(!dependency.csuid||dependency.csuid!==support.buildingCSUID||proof.csuid!==dependency.csuid)return {...base,reason:'dependency-csuid-mismatch'};
 if(proof.reviewState!=='installed-verified'||proof.snapshotVerified!==true||!proof.snapshotId)return {...base,reason:'dependency-current-installed-review-required'};
 if(!support.sha256||proof.sourceSHA256!==support.sha256||proof.assetSHA256!==support.sha256)return {...base,reason:'dependency-current-asset-hash-mismatch'};
 if(support.sourceIdentityReviewed!==true||support.placementReviewed!==true)return {...base,reason:'dependency-current-source-placement-not-approved'};
 if(support.publicationApproved!==true&&proof.installedAcceptanceVerified!==true)return {...base,reason:'dependency-current-installed-acceptance-required'};
 return {...base,effectiveState:'installed',passed:true,sourceSHA256:proof.sourceSHA256,
         snapshotId:proof.snapshotId,qualification:'Historical label retained; exact current installed review/UID/CSUID/asset/source approvals required. Full physical support checks remain separate.'};
}
