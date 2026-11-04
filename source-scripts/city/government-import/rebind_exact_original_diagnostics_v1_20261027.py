"""Bind saved numeric diagnostics only when complete captured inputs are identical.

Never transfers physical, source-role, visual, support or installation acceptance.
"""
import argparse,json
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','prior-runtime','runtime','prior-attributes','attributes']:p.add_argument('--'+key,required=True)
    p.add_argument('--proof',action='append',required=True);a=p.parse_args()
    names=[a.prior_runtime,a.runtime,a.prior_attributes,a.attributes,*a.proof]
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,*names])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[HERE/'rebind_exact_original_diagnostics_v1_20261027.py'];pins={};receipts={}
    for name in names:
        receipt,bound=authenticate(base/name);receipts[name]=receipt;pins[name]=bound;refs.append(base/name/'result.json')
    def take(name,path):
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    old=take(a.prior_runtime,HERE/'local'/a.prior_runtime/'runtime-geometry.json.gz')['rows'];new=take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']
    attrs_old=take(a.prior_attributes,base/a.prior_attributes/'attributes.json.gz');attrs_new=take(a.attributes,base/a.attributes/'attributes.json.gz')
    assert attrs_old['startEndAllInputsVerified'] and attrs_new['startEndAllInputsVerified']
    assert canonical(old)==canonical(new),'Complete captured geometry, pose or drawn ground differs'
    assert canonical(attrs_old['rows'])==canonical(attrs_new['rows']),'Complete four-world source arrays differ'
    selection=take(a.runtime,base/a.runtime/'selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']}
    assert set(sources)=={r['uid']for r in new}=={r['uid']for r in attrs_new['rows']}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    for row in selection['rows']:
        path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256'];refs.append(path)
    proofs=[]
    for name in a.proof:
        r=receipts[name];assert set(r['uids'])<=set(sources)
        if 'sourceSHA256'in r:assert r['sourceSHA256']==sources[r['uids'][0]]
        # Rehash every recorded computation input, not only its summary.
        for path,sha in pins[name].items():
            f=ROOT/path;assert digest(f.read_bytes())==sha;refs.append(f)
        proofs.append(dict(batch=name,jobId=r['jobId'],uids=r['uids'],resultSHA256=digest((base/name/'result.json').read_bytes()),numericFactsRevalidated=True,approvalTransferred=False))
    result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,completeSourceAndDrawnGroundRowsSHA256=digest(canonical(new)),completeFourWorldAttributeRowsSHA256=digest(canonical(attrs_new['rows'])),completeCapturedRowsExact=True,completeFourWorldAttributeRowsExact=True,proofs=proofs,sourceGeometryChanges=0,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,qualification='Byte-exact canonical complete captured source/pose/drawn-ground rows and complete four-world attribute rows match. All saved computation inputs and immutable source bytes are rehashed. Numeric diagnostics only are rebound to current runtime; every existing raw failure and source-role/visual/support/publication obligation remains.')
    save(out/'summary.json',result)
    module('exact_original_numeric_rebind_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-input-revalidation-of-saved-original-numeric-diagnostics',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
