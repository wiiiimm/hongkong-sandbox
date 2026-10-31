"""Bind separate shallow-embedded finite-path evidence; no physical approval."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,jobs
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from finite_embedded_basic_support_contract_v1_20261025 import verify_mode
from finite_height_clearance_bound_v1_20261023 import verify as finite_bound
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-k-after-tuen-mun-finite-basic-evidence-v1-20261025'

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'finite_embedded_basic_support_contract_v1_20261025.py',HERE/'test_finite_embedded_basic_support_contract_v1_20261025.py'];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 runtime='government-xl-beverly-k-after-tuen-mun-runtime-v1-20261025';source=take(runtime,'selection.json.gz')['rows'][0];assert source['uid']=='landsd/255543:0'
 checks='government-xl-beverly-k-after-tuen-mun-four-world-basic-diagnostic-v1-20261025';payload=take(checks,'mode-inputs.json.gz')['rows'][0];canonical=take(checks,'mode-checks.json.gz')['rows'];assert len(canonical)==len(payload['modes'])==4 and payload['sourceSHA256']==source['sourceSHA256']
 basic=take('government-xl-beverly-k-after-tuen-mun-basic-contacts-v2-20261025','checks.json.gz')['rows'][0];assert basic['basicIsCurrentFinalSupport']and not basic['canonicalContactPassed']and basic['supportUid']=='landsd/233218:0'
 form=basic['supportForm'];assert form['parent']==source['source']['building']['parent']and form['parent']and form['heightSource']=='landsd'
 g=payload['supportGeometry'];p=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];rows=[];clearance=[]
 for mode in payload['modes']:
  x=mode['geometry'];t=np.asarray(x['position']).reshape(-1,3)[np.asarray(x['index']).reshape(-1,3)]
  raw=next(r['proof']for r in canonical if r['mode']==mode['mode']);detail=take('government-xl-beverly-k-after-tuen-mun-basic-finite-paths-v1-20261025',mode['mode']+'.json.gz')
  proof=verify_mode(t,p,raw,detail);bound=finite_bound(x['position'],g['position']);assert bound['ordinaryClearanceBoundProved'];rows.append(dict(mode=mode['mode'],sourceWorldSHA256=detail['sourceWorldSHA256'],supportWorldSHA256=detail['supportWorldSHA256'],**proof));clearance.append(dict(mode=mode['mode'],**bound))
 assert {r['mode']for r in rows}=={'original','literal','leftF32','balancedF32'}
 evidence=dict(uids=[source['uid']],supportUid=basic['supportUid'],sourceSHA256=source['sourceSHA256'],rows=rows,sourceSupportClearance=clearance,separateFiniteSupportEvidence=True,completeFourWorldCanonicalRetainedBasicSupport=False,completeFourWorldFiniteRetainedBasicSupport=True,physicalSupportAccepted=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Canonical strict support remains false. All40unresolved underside witnesses have replayed finite original-facet paths to actual exposed vertical source-wall/currentBASICroof intersections, at0.349998474m embedding within unchanged0.5m/1mm limits. This is a separate evidence profile; source/native role review, current support lifetime, actual fallback/browser checks and publication approval remain mandatory.')
 save(out/'finite-basic-evidence.json',evidence)
 binding=dict(uid=source['uid'],supportUid=basic['supportUid'],supportCSUID=form['buildingCSUID'],dependencyMode='retained-current-basic-podium',currentBasicForm=form,currentBasicFormSHA256=digest(jobs.encode(form).encode()),completeIndexedBasicGeometrySHA256=digest(jobs.encode(g).encode()),supportEvidence=dict(path=str((out/'finite-basic-evidence.json').relative_to(ROOT)),sha256=digest((out/'finite-basic-evidence.json').read_bytes())),sourceSHA256=source['sourceSHA256'],mustRemainBasicAndUnsuppressed=True,futureReplacementRequiresDependentRevalidation=True)
 save(out/'support-bindings.json',[binding]);save(out/'summary.json',evidence)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[runtime][str(manifest.relative_to(ROOT))];refs.append(manifest);refs.append(HERE/'finite_height_clearance_bound_v1_20261023.py')
 module('beverly_finite_basic_evidence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'separate-four-world-shallow-embedded-original-basic-support-evidence',list(dict.fromkeys(refs)),evidence)
if __name__=='__main__':main()
