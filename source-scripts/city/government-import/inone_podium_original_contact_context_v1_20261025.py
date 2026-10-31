"""Bound exact original podium contact witnesses to unchanged current source forms."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-inone-podium-original-contact-context-v1-20261025'
CONTACTS='government-xl-inone-five-current-foreign-contacts-v1-20261025'
SCOPE='government-xl-inone-five-full-source-native-scope-v1-20261025'
UID='landsd/277890:0'
def main():
    out=BASE/BATCH;assert not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    summary=take(CONTACTS,BASE/CONTACTS/'summary.json');own=set(summary['uids'])
    forms={r['building']['uid']:r['building']for r in take(SCOPE,BASE/SCOPE/'277890:0-forms.json.gz')}
    rows=[]
    for pair in summary['rows']:
        if pair['uid']!=UID or pair['foreignUid']in own:continue
        other=pair['foreignUid'];modes=[]
        for mode in ['before-basic','original','literal','leftF32','balancedF32']:
            p=BASE/CONTACTS/('277890:0--'+other.split('/')[1]+'--'+mode+'.json.gz')
            proof=take(CONTACTS,p)
            positive=[c for c in proof['contacts']if c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
            measurements=next(r for r in pair['modes']if r['mode']==mode)
            assert len(positive)==measurements['positiveContactPairs']
            b=np.asarray([c['bounds']for c in positive],float).reshape(-1,3) if positive else None
            modes.append(dict(mode=mode,positivePairs=len(positive),sourceFaceIds=sorted({c['sourceFaceA']for c in positive}),foreignFaceIds=sorted({c['sourceFaceB']for c in positive}),contactBounds=[b.min(0).tolist(),b.max(0).tolist()]if b is not None else None))
        if not any(m['positivePairs']for m in modes):continue
        form=forms[other]
        rows.append(dict(uid=UID,foreignUid=other,foreignForm={k:form.get(k)for k in ['uid','objectId','buildingCSUID','name','parent','osmRefs','baseHeightHKPD','topHeightHKPD','rings']},sameRecordedParent=bool(form.get('parent'))and form['parent']==forms[UID].get('parent'),modes=modes,contactRoleAccepted=False))
    assert len(rows)==10
    result=dict(uids=sorted(own),sourceUid=UID,foreignContactActors=len(rows),rows=rows,sourceGeometryChanges=0,physicalAcceptance=False,identityAccepted=False,installationApproved=False,qualification='Exact complete existing contact witnesses and current actor metadata only. Common parent is context, not ownership/physical approval. Co-import peers are separately reviewed; no foreign actor is suppressed or excluded.')
    save(out/'summary.json',result)
    module('inone_contact_context',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'inone-original-podium-complete-finite-contact-role-context',refs,result)
    for r in rows:print(dict(uid=r['foreignUid'],sameParent=r['sameRecordedParent'],bounds=next(m['contactBounds']for m in r['modes']if m['mode']=='original')),flush=True)
if __name__=='__main__':main()
