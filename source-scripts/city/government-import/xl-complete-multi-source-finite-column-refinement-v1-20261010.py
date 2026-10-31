"""Refine all immutable paired finite failures for complete original actors.

Every coarse and paired negative remains verbatim. Exact finite columns apply
only to unproved faces; unchanged original and literal geometry are independent.
No component, support, current acceptance or installation credit is granted.
"""
import argparse,importlib.util
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_v2_20261010 import refine

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def main():
    p=argparse.ArgumentParser();p.add_argument('--physical',required=True);p.add_argument('--finite',required=True);p.add_argument('--batch',required=True);a=p.parse_args()
    assert Path(a.batch).name==a.batch
    physical=(ROOT/a.physical).resolve();finite=(ROOT/a.finite).resolve()
    assert physical.is_relative_to(ROOT) and finite.is_relative_to(ROOT)
    doc=ROOT/'docs/astra-city/government-import'/a.batch;assert not doc.exists()
    receipt=read(finite/'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
    selected=read(physical/'selection.json.gz')['rows'];prior=read(finite/'diagnostic.json.gz')['rows']
    runtime_path=HERE/'local'/physical.name/'runtime-geometry.json.gz';runtime=read(runtime_path)['rows']
    assert len(selected)==len(prior)==len(runtime) and [r['uid'] for r in selected]==[r['uid'] for r in prior]
    rows=[];assets=[]
    for row,cached in zip(selected,prior):
        asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==cached['sourceSHA256']
        assets.append(asset);original=decode_original_world_triangles(raw)
        g=next(r for r in runtime if r['uid']==row['uid'])
        actual=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index'],np.uint32).reshape(-1,3)]
        ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3)
        assert digest(original.tobytes())==cached['completeOriginalWorldSHA256']
        assert digest(actual.tobytes())==cached['completeActualRenderedWorldSHA256']
        assert digest(ground.tobytes())==cached['completeGroundSHA256']
        assert len(cached['allFaces'])==len(original)==len(actual)
        faces=[]
        for i,c in enumerate(cached['allFaces']):
            assert c['sourceFace']==i
            coarse=c['priorCoarseBoundProofVerbatim']
            assert coarse['completeOriginal']['sourceFaceSHA256']==digest(original[i].tobytes())
            assert coarse['actualRendered']['sourceFaceSHA256']==digest(actual[i].tobytes())
            first=None if c['completeOriginalBoundProved'] else refine(original[i],ground,c['pairedExactOriginalFiniteBound'])
            second=None if c['completeActualRenderedBoundProved'] else refine(actual[i],ground,c['pairedExactActualRenderedFiniteBound'])
            faces.append(dict(sourceFace=i,priorCompletePairedProofVerbatim=c,priorCoarseBoundProofVerbatim=coarse,
                exactOriginalColumnRefinement=first,exactActualRenderedColumnRefinement=second,
                completeOriginalBoundProved=c['completeOriginalBoundProved'] or bool(first and first['existingOrdinaryClearanceBoundProved']),
                completeActualRenderedBoundProved=c['completeActualRenderedBoundProved'] or bool(second and second['existingOrdinaryClearanceBoundProved'])))
        unproved=[r['sourceFace'] for r in faces if not r['completeOriginalBoundProved'] or not r['completeActualRenderedBoundProved']]
        rows.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(original),
            completeOriginalWorldSHA256=digest(original.tobytes()),completeActualRenderedWorldSHA256=digest(actual.tobytes()),
            completeGroundSHA256=digest(ground.tobytes()),allFaces=faces,unprovedFaces=unproved))
        print(dict(uid=row['uid'],completeOriginalFaces=len(original),remainingFiniteFaces=len(unproved)),flush=True)
    refs=[Path(__file__),finite/'result.json',finite/'diagnostic.json.gz',physical/'selection.json.gz',physical/'result.json',runtime_path,*assets]
    refs.extend(HERE/n for n in ['exact_original_paired_finite_clearance_v2_20261010.py','exact_original_paired_finite_clearance_20261010.py',
        'exact_original_triangle_pair_column_gap_20261010.py','test_exact_original_triangle_pair_column_gap_20261010.py',
        'exact_original_projection_coverage_v2_20261010.py','exact_packed_world_geometry_20261009.py'])
    result=dict(rows=rows,completeOriginalFaces=sum(r['completeOriginalFaces'] for r in rows),
        unprovedFaces={r['uid']:r['unprovedFaces'] for r in rows},rawPriorFailuresRetained=True,sourceGeometryChanges=0,
        rootOrContactCredit=False,currentAcceptancePassed=False,fullAcceptance=False,publication=False)
    save(doc/'diagnostic.json.gz',result)
    spec=importlib.util.spec_from_file_location('multi_finite_column_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.freeze(a.batch,'complete-multiple-original-and-literal-finite-column-refinement-v1',refs,
        {k:v for k,v in dict(**result,uids=[r['uid'] for r in rows],humanStatus='held-for-compute',humanDecisionRequired=False,aiGeometryModellingRequired=False).items() if k!='rows'})

if __name__=='__main__':main()
