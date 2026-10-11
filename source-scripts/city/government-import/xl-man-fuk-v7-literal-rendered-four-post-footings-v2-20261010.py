"""Independently replay four ordinary footings on literal rendered source faces.

This immutable support diagnostic grants no current whole-model acceptance.
The actual rendered vertices and complete actual terrain are checked with the
unchanged production support-interface kernel, without coordinate welding.
"""
import importlib.util,json,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE=ROOT/'docs/astra-city/government-import'
PHYSICAL=BASE/'government-xl-man-fuk-complete-retained-original-physical-v7-20261010'
GRAPH=BASE/'government-xl-man-fuk-v7-complete-original-support-20261010'
BATCH='government-xl-man-fuk-v7-literal-rendered-four-post-footings-v2-20261010';DOC=BASE/BATCH
UID='landsd/266062:0';SOURCE='22b458321ca483c53324ee152cb27c382e5ac4dfd745974f169b1c551ac8a6c1'

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def main():
    assert not DOC.exists()
    manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes()
    selection=read(PHYSICAL/'selection.json.gz');assert digest(before)==selection['manifestSHA256']
    for folder in [PHYSICAL,GRAPH]:
        receipt=read(folder/'result.json')
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
        for item in receipt['evidenceRefs']:assert ref(ROOT/item['path'])==item
    graph=read(GRAPH/'diagnostic.json.gz');assert graph['ordinaryGroundRootComponents']==[2,3,4,5]
    row=selection['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE
    asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCE
    original=decode_original_world_triangles(raw)
    runtime_path=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(runtime_path)['rows'][0]
    actual=np.asarray(runtime['position'],float).reshape(-1,3)[np.asarray(runtime['index'],np.uint32).reshape(-1,3)]
    ground=np.asarray(runtime['drawnGroundGeometry'],float).reshape(-1,3,3)
    assert original.shape==actual.shape==(10661,3,3)
    assert digest(original.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256']
    helper=HERE/'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs';results=[];inputs=[]
    for component in [2,3,4,5]:
        c=graph['components'][component];assert c['actorUID']==UID and len(c['globalOriginalFaces'])==16
        faces=c['globalOriginalFaces'];part=actual[faces];bottom=float(part[:,:,1].min())
        assert float(original[faces][:,:,1].min())==39.994998931884766
        # The production source-to-world transform may round by one binary ULP.
        # The literal bottom above is independently tested, not substituted.
        assert float(np.max(np.abs(original-actual)))==graph['originalPackedWorldMaximumNumericalRoundoffM']
        data=dict(uid=UID,sourceSHA256=SOURCE,manifestSHA256=digest(before),component=component,completeLiteralRenderedWorldSHA256=digest(actual.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),part=dict(position=part.reshape(-1).tolist(),index=list(range(part.size//3)),bottomHKPD=bottom,component=component,originalFaceIds=faces),terrain=dict(position=ground.reshape(-1).tolist(),index=list(range(ground.size//3))))
        path=DOC/('component-'+str(component)+'-input.json.gz');save(path,data);inputs.append(path)
        proof=json.loads(subprocess.check_output(['node',str(helper),str(path)],cwd=ROOT,text=True))
        assert proof['passed'] is True
        results.append(dict(component=component,originalFaceIds=faces,completeActualRenderedPartSHA256=digest(part.tobytes()),input=ref(path),result=proof,strictLiteralRenderedCurrentGroundAnchor=True))
    assert manifest.read_bytes()==before
    refs=[ref(p) for p in [Path(__file__),manifest,PHYSICAL/'result.json',PHYSICAL/'selection.json.gz',GRAPH/'result.json',GRAPH/'diagnostic.json.gz',runtime_path,asset,helper,HERE/'support-interface.mjs',*inputs]]
    result=dict(uid=UID,sourceSHA256=SOURCE,manifestSHA256=digest(before),completeOriginalFaces=10661,completeLiteralRenderedWorldSHA256=digest(actual.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),rows=results,strictLiteralRenderedFourPostFootings=True,arithmeticParityCredit=False,sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False,evidenceRefs=refs)
    save(DOC/'diagnostic.json.gz',result)
    s=importlib.util.spec_from_file_location('four_post_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    m.freeze(BATCH,'complete-literal-rendered-original-four-post-footings-v1',[ROOT/r['path'] for r in refs],dict(uids=[UID],strictLiteralRenderedFourPostFootings=True,arithmeticParityCredit=False,sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False))
    print(json.dumps(dict(strictLiteralRenderedFourPostFootings=True,components=[2,3,4,5],sourceGeometryChanges=0)),flush=True)

if __name__=='__main__':main()
