"""Integrate two inactive exact-source extent scopes; no source installation."""
import copy,json,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
REVIEW='government-xl-disneyland-piers-extent-identity-review-v1-20261029'

def main():
    receipt,pins=authenticate(BASE/REVIEW);assert receipt['sourceIdentityInterpretationApproved']and receipt['identityOnlyApproved']and not receipt['installationApproved']
    registry=ROOT/'3d-viewer/city/official-model-reviewed-original-feature-data.js';before=registry.read_text();old=json.loads(before.split('Object.freeze(',1)[1].rsplit(');',1)[0]);new=copy.deepcopy(old);rows=[]
    for uid in receipt['uids']:
        part=uid.split('/')[1];scopepath=BASE/REVIEW/part/'prepared-scope.json';decisionpath=BASE/REVIEW/part/'ROOT-SOURCE-IDENTITY-DECISION.json'
        for p in [scopepath,decisionpath]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
        scope=read(scopepath);key='reviewed-original-feature:'+uid;assert key not in new and scope['uid']==uid and scope['identityReviewed']and scope['sourceReview']==dict(path=str(decisionpath.relative_to(ROOT)),sha256=digest(decisionpath.read_bytes()))
        new[key]=scope;rows.append((uid,scope,decisionpath))
    assert all(new[k]==v for k,v in old.items())and len(new)==len(old)+2
    registry.write_text('// Exact original-feature source review; no model geometry or GIS record edits.\nexport const reviewedOriginalFeatureScopes=Object.freeze('+json.dumps(new,sort_keys=True,separators=(',',':'))+');\n')
    child=[]
    for uid,scope,decisionpath in rows:
        batch='government-xl-disneyland-pier-'+uid.split('/')[1].split(':')[0]+'-feature-scope-v1-20261029';out=BASE/batch;assert not out.exists()
        save(out/'prepared-scope.json',scope);save(out/'ROOT-SOURCE-IDENTITY-DECISION.json',read(decisionpath))
        result=dict(uids=[uid],sourceIdentityInterpretationApproved=True,identityOnlyApproved=True,productionIntegrated=True,inactiveUntilSourceCatalogueInstalled=True,sourceGeometryChanges=0,placementApproved=False,installationApproved=False,publication=False,qualification='Exact-source extent scope only. Existing installed scopes remain identical; no source catalogue added. Generic model validation, all contact/terrain/neighbour/runtime/browser/publication gates remain unchanged.')
        save(out/'summary.json',result);module('disneyland_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-pier-inactive-feature-extent-scope',[Path(__file__),BASE/REVIEW/'result.json',BASE/REVIEW/uid.split('/')[1]/'prepared-scope.json',decisionpath,registry,ROOT/'3d-viewer/city/official-model-reviewed-original-feature-footprint.js'],result);child.append(batch)
    print(dict(scopesAdded=2,oldScopesPreserved=len(old),batches=child,installationApproved=False),flush=True)

if __name__=='__main__':main()
