"""Full source and literal wall diagnostics from frozen finite-column proofs.

Every prior negative remains in the input receipt. Schema adapters expose the
same certified bounds and candidate lists to unchanged context kernels; no
geometric, root, identity, current-acceptance or installation credit is granted.
"""
import argparse,importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_bound_facet_wall_context_20261010 import canonical
from original_bound_facet_wall_context_v3_20261010 import contexts
from xl_source_stream_binding_20261009 import source_stream_binding
from unchanged_open_exterior_paths_v2_20261009 import original_open_paths
from original_coplanar_exterior_continuation_20261009 import diagnose

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def analyse(tri,ground,finite,raw,actual=False):
    normalized=[]
    for i,c in enumerate(finite['allFaces']):
        assert c['sourceFace']==i
        prior=c['priorCompletePairedProofVerbatim'];coarse=c['priorCoarseBoundProofVerbatim']
        assert prior['priorCoarseBoundProofVerbatim']==coarse
        key='exactActualRenderedColumnRefinement' if actual else 'exactOriginalColumnRefinement'
        pairedkey='pairedExactActualRenderedFiniteBound' if actual else 'pairedExactOriginalFiniteBound'
        provedkey='completeActualRenderedBoundProved' if actual else 'completeOriginalBoundProved'
        paired=c[key] if c[key] is not None else prior[pairedkey]
        if c[key] is not None:
            paired=dict(paired)
            paired['allProjectedBoundingCandidateOriginalGroundFacets']=paired['rawPriorPairedProofVerbatim']['allProjectedBoundingCandidateOriginalGroundFacets']
        adapted_coarse=coarse if not actual else dict(coarse,completeOriginal=coarse['actualRendered'])
        normalized.append(dict(sourceFace=i,priorCoarseBoundProofVerbatim=adapted_coarse,
            pairedExactOriginalFiniteBound=paired,completeOriginalBoundProved=c[provedkey]))
    binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),completeFiniteFacetProofRowsSHA256=canonical(normalized))
    ctx=contexts(tri,ground,normalized,expected_binding=binding,current_binding=binding)
    affected=[i for i,c in enumerate(ctx) if c['minimum']['minimumGapM']<-.5]
    path_binding={**source_stream_binding(raw),**binding,'decodedWorldTrianglesSHA256':digest(tri.tobytes()),'drawnGroundSHA256':digest(ground.tobytes())}
    paths=original_open_paths(tri,ctx,affected,range(len(tri)),expected_binding=path_binding,current_binding=path_binding)
    below=[r['sourceFace'] for r in paths['faces'] if r['reasons']==['no-exposed-wall-witness']]
    continuation=diagnose(tri,ctx,below) if below else dict(rows=[],wholeOriginalFacesAccounted=len(tri),diagnosticOnly=True)
    n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(n,axis=1)
    ratio=np.divide(n[:,1],length,out=np.zeros(len(tri)),where=length>0)
    positive={r['sourceFace'] for r in continuation['rows'] if r['hasActualAboveGroundExteriorContinuation']}
    unresolved=[r for r in paths['faces'] if r['reasons'] and not(r['reasons']==['no-exposed-wall-witness'] and r['sourceFace'] in positive)]
    return dict(binding=binding,completeCertifiedLowerBoundContexts=ctx,normalizedFiniteProofRows=normalized,
        affectedFaces=affected,buriedUpwardFaces=[i for i in affected if ratio[i]>.25],wallPaths=paths,
        exactCoplanarContinuation=continuation,unexposedIndividualWallFaces=below,unresolvedWallConditions=unresolved,
        roleAccepted=False,rootOrContactCredit=False,installationApproved=False)

def main():
    p=argparse.ArgumentParser();p.add_argument('--physical',required=True);p.add_argument('--finite',required=True);p.add_argument('--batch',required=True);a=p.parse_args()
    assert Path(a.batch).name==a.batch
    physical=(ROOT/a.physical).resolve();finite=(ROOT/a.finite).resolve();assert physical.is_relative_to(ROOT) and finite.is_relative_to(ROOT)
    doc=ROOT/'docs/astra-city/government-import'/a.batch;assert not doc.exists()
    receipt=read(finite/'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
    selected=read(physical/'selection.json.gz')['rows'];prior=read(finite/'diagnostic.json.gz')['rows']
    runtime_path=HERE/'local'/physical.name/'runtime-geometry.json.gz';runtime=read(runtime_path)['rows']
    assert len(selected)==len(prior)==len(runtime) and [r['uid'] for r in selected]==[r['uid'] for r in prior]
    rows=[];assets=[];summaries=[]
    for row,cached in zip(selected,prior):
        asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assets.append(asset)
        assert digest(raw)==row['sourceSHA256']==cached['sourceSHA256']
        tri=decode_original_world_triangles(raw);g=next(r for r in runtime if r['uid']==row['uid'])
        world=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index'],np.uint32).reshape(-1,3)]
        ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3)
        assert digest(tri.tobytes())==cached['completeOriginalWorldSHA256'] and digest(world.tobytes())==cached['completeActualRenderedWorldSHA256'] and digest(ground.tobytes())==cached['completeGroundSHA256']
        assert len(tri)==len(world)==len(cached['allFaces'])
        result=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(tri),
            rawFiniteRowsSHA256=canonical(cached['allFaces']),completeOriginal=analyse(tri,ground,cached,raw),
            actualRendered=analyse(world,ground,cached,raw,True))
        rows.append(result)
        summary=dict(uid=row['uid'],completeOriginalFaces=len(tri),**{k:dict(affected=len(result[k]['affectedFaces']),buriedUpward=result[k]['buriedUpwardFaces'],unresolved=result[k]['unresolvedWallConditions']) for k in ['completeOriginal','actualRendered']})
        summaries.append(summary);print(json.dumps(summary),flush=True)
    refs=[Path(__file__),finite/'diagnostic.json.gz',finite/'result.json',physical/'selection.json.gz',physical/'result.json',runtime_path,*assets]
    refs.extend(HERE/n for n in ['original_bound_facet_wall_context_20261010.py','original_bound_facet_wall_context_v2_20261010.py','original_bound_facet_wall_context_v3_20261010.py','test_original_bound_facet_wall_context_20261010.py','test_original_bound_facet_wall_context_v2_20261010.py','test_original_bound_facet_wall_context_v3_20261010.py','unchanged_open_exterior_paths_v2_20261009.py','original_coplanar_exterior_continuation_20261009.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_paired_finite_clearance_v2_20261010.py','xl_source_stream_binding_20261009.py'])
    save(doc/'diagnostic.json.gz',dict(rows=rows,rawPriorFailuresRetained=True,sourceGeometryChanges=0,roleAccepted=False,rootOrContactCredit=False,currentAcceptancePassed=False,installationApproved=False))
    spec=importlib.util.spec_from_file_location('finite_wall_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.freeze(a.batch,'complete-multiple-source-and-literal-finite-wall-contexts-v1',refs,dict(uids=[r['uid'] for r in rows],summaries=summaries,rawPriorFailuresRetained=True,sourceGeometryChanges=0,roleAccepted=False,rootOrContactCredit=False,fullAcceptance=False,humanStatus='held-for-compute',humanDecisionRequired=False,aiGeometryModellingRequired=False))

if __name__=='__main__':main()
