"""Nominate all installed originals using authenticated complete four-world bounds."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from heritage_saved_native_bounds_binding_v1_20261014 import bind_record,closed_disjoint
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from primrose_compound_foundation_v2_20261015 import module

BATCH='government-xl-science-history-native-parent-scope-v1-20261016'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH

def main():
    assert not DOC.exists()
    prior=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v6-20261015'
    declarations=read(prior/'input.json.gz');inventory=read(prior/'inventory.json.gz')
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath)
    candidate=BASE/'government-xl-science-history-private-neighbours-v1-20261016/summary.json';domain=read(candidate)['changedParentExtent']
    models={};assets={};roots={};refs=[Path(__file__),prior/'input.json.gz',prior/'inventory.json.gz',manifestpath,candidate]
    for url in manifest['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;cat=read(p);refs.append(p)
        for entry in cat['models']:
            uid=entry['uid'];assert uid not in models;models[uid]=entry;assets[uid]=p.parent/entry['asset'];roots[uid]=cat['rootTranslation']
    forms={};form_pins={}
    for tile in manifest['tiles']:
        p=ROOT/'3d-viewer'/tile['url'];data=read(p)
        for b in data['buildings']:
            if b['uid']in models:
                forms[b['uid']]=b
                key=str(p.relative_to(ROOT))
                if key not in form_pins:form_pins[key]=digest(p.read_bytes())
    rows={r['uid']:r for r in inventory['rows']};touch=[];bound_rows=[]
    for d in declarations['rows']:
        uid=d['uid'];assert d['currentBuilding']==forms[uid],uid
        assert digest(assets[uid].read_bytes())==d['source']['sha256'],uid
        boxes=bind_record(models[uid],d,rows[uid]);disjoint=closed_disjoint(boxes,domain)
        if not disjoint:touch.append(uid)
        bound_rows.append(dict(uid=uid,sourceSHA256=models[uid]['sha256'],completeFourWorldBounds=boxes,disjoint=disjoint))
    closure=inventory['completeRecursiveProductionModuleClosure']['inputHashes']
    for p,h in closure.items():assert digest((ROOT/p).read_bytes())==h,p
    new=sorted(set(models)-set(rows));assert new==['landsd/323703:0','landsd/335875:0','landsd/4759:0'],new
    DOC.mkdir()
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    selected=[dict(uid=u,entry={**models[u],'rootTranslation':roots[u]},building=forms[u],path=str(assets[u].relative_to(ROOT)))for u in new]
    save(DOC/'input.json.gz',dict(currentManifest=ref(manifestpath),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u)for u in manifest['officialModelCatalogues']],evidenceRefs=[ref(prior/'input.json.gz'),ref(prior/'inventory.json.gz')],rows=selected))
    tool=HERE/'science_history_new_native_attributes_v1_20261016.mjs'
    with(DOC/'capture.log').open('w')as log:subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
    actual=read(DOC/'attributes.json.gz');assert actual['startEndAllInputsVerified']
    for path,h in actual['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
    for u in new:
        r=next(r for r in actual['rows']if r['uid']==u);proof=packed_world_bounds(assets[u].read_bytes());assert proof['sourceSHA256']==r['sourceSHA256']==models[u]['sha256']
        boxes=[proof['originalWholeSourceBounds'],r['completeLiteralWorldBounds'],r['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],r['completeExplicitBalancedFloat32ModelMatrixWorldBounds']]
        disjoint=closed_disjoint(boxes,domain)
        if not disjoint:touch.append(u)
        bound_rows.append(dict(uid=u,sourceSHA256=models[u]['sha256'],completeFourWorldBounds=boxes,disjoint=disjoint,completeOriginalPOSITIONProof=proof))
    assert len(bound_rows)==len(models)==6665
    summary=dict(currentNativeActors=len(models),reusedExactActors=len(rows),freshCapturedActors=new,changedParentExtent=domain,touchingNativeUids=sorted(touch),allCurrentActorsNominated=True,fullMeshRegressionStillRequired=True,fullAcceptance=False)
    save(DOC/'scope.json',summary);save(DOC/'complete-bounds.json.gz',dict(rows=bound_rows,currentFormTileHashes=form_pins))
    refs += list(assets.values())+[ROOT/p for p in form_pins]+[ROOT/p for p in closure]+[tool,HERE/'heritage_saved_native_bounds_binding_v1_20261014.py',HERE/'exact_packed_world_bounds_v3_20261010.py']
    result=module('hotel_all_native_scope_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'all-current-native-four-world-shared-museums-parent-domain-v1',list(dict.fromkeys(refs)),dict(uids=sorted(touch)+new,summary=summary,fullAcceptance=False,newlyInstalled=0))
    print(dict(jobId=result['jobId'],summary=summary),flush=True)

if __name__=='__main__':main()
