"""Bounded unchanged-source facade interpretation; no installation or geometry changes."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-tower3a-facade-role-v1-20261021';DOC=BASE/BATCH
VIEW=BASE/'government-xl-tko-tower3a-attachment-view-v1-20261021';BAND=BASE/'government-xl-tko-tower3a-connected-edge-band-v1-20261021';FAILED=BASE/'government-xl-tko-tower3a-finite-host-band-v1-20261021';PATHS=BASE/'government-xl-tko-complete-paths-v1-20261021';CAP=BASE/'government-xl-tko-complete-capture-v2-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'china_ferry_current_foundations_v1_20261020.py'];pins={};used={}
 for d in [VIEW,BAND,FAILED,PATHS,CAP]:
  _,bound=authenticate(d);pins[d]=bound;refs.append(d/'result.json')
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];used[k]=pins[d][k];refs.append(p);return read(p)
 source=next(r for r in take(CAP,CAP/'selection.json.gz')['rows']if r['uid']=='landsd/32024:0');context=take(VIEW,VIEW/'context.json');bands=take(BAND,BAND/'summary.json');failed=take(FAILED,FAILED/'summary.json')
 assert all(r['edges']==r['completeEdgesAssociated']==8 for r in bands['rows'])and len(bands['rows'])==4
 assert all(r['faces']==12 and r['wholeFacetAssociated']==0 for r in failed['rows'])
 witnesses={}
 for mode in ['original','literal','leftF32','balancedF32']:
  prior=take(PATHS,PATHS/mode/'32024:0.json.gz');w=[x for x in prior['rows']if not x['verifiedPath']];assert len(w)==14;assert set(f for x in w for f in x['incidentFaces'])<=set(context['faceIds']);witnesses[mode]=dict(sourceWorldSHA256=prior['sourceWorldSHA256'],rows=w)
 assert witnesses['original']['sourceWorldSHA256']==context['sourceWorldSHA256']
 images=[]
 for name in ['lower.png','full.png']:
  p=VIEW/name;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[VIEW][k];used[k]=pins[VIEW][k];refs.append(p);images.append(dict(path=k,sha256=pins[VIEW][k]))
 review=dict(uid=source['uid'],sourceSHA256=source['sourceSHA256'],exactFaceIds=context['faceIds'],witnesses=witnesses,reviewer='Codex ROOT',reviewType='bounded-original-facade-source-context',roleInterpretationAccepted=True,reviewedRole='Two projecting facade strips whose open attachment boundaries follow the original tower facade',imagesActuallyInspected=images,basis=[
 'ROOT inspected four-angle lower and full-height exact-source diagnostic exports. Both components are tall narrow projections of the same tower facade, with their open boundaries following its surface; no separate building, ground footing or equipment function is inferred.',
 'Every one of the eight complete geometric boundary edges passes the unchanged exact finite 0.1m facade-band verifier in all four representations. Hosts exclude both residual components and have nondegenerate shared-edge paths to positive finite original podium contacts.',
 'All twelve whole facets fail the whole-facet 0.1m band. Preserve this negative: the projecting surfaces extend away from the wall, whereas the attachment boundary follows it. No tolerance is increased and no source vertex is moved.',
 'The fourteen no-vertical-support samples per representation remain raw failures. For these exact projecting facade faces, review attachment via the complete original boundary rather than invent a new direct footing. This grants no structural root credit or support for unrelated components.'
 ],requiredNextChecks=['Bind every residual witness to a continuous path within its unchanged original component reaching an admitted finite attachment boundary','Verify the corresponding host attachment and positive podium-contact connection in each representation','Retain full source identity, terrain/foundation/collision, podium support, retained neighbours, complete scene runtime and browser acceptance'],rawWholeFacetFailureRetained=True,rawStrictSupportFailuresRetained=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,publicationApproved=False)
 save(DOC/'role-review.json',review)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 module('tko_facade_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-facade-role-context',list(dict.fromkeys(refs)),dict(uids=[source['uid']],roleInterpretationAccepted=True,physicalAccepted=False,installationApproved=False))
if __name__=='__main__':main()
