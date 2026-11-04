"""Bounded named original facade placement proposal; no current approval."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from heya_aqua_58_original_terminal_visual_placement_20261011 import verify,UID,IMAGES
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011'
CONTEXT=BASE/'government-xl-heya-aqua-terminal-parts-orthographic-context-v2-20261011'
VALIDATION=BASE/'government-xl-heya-aqua-58-source-role-validation-v1-20261011'
ARCHIVE=BASE/'government-xl-heya-aqua-source-census-v1-freeze-serialization-failure-archive-20261011'
BATCH='government-xl-heya-aqua-58-original-terminal-visual-placement-proposal-v1-20261011';DOC=BASE/BATCH
def main():
    assert not DOC.exists();validation=read(VALIDATION/'validation.json')
    assert validation['testsRun']==14 and validation['allPassed'] and validation['sourceOnly']
    expected_codes=[Path(__file__),HERE/'heya_aqua_58_original_terminal_visual_placement_20261011.py',HERE/'test_heya_aqua_58_original_terminal_visual_placement_20261011.py']
    assert validation['codeHashes']=={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in expected_codes}
    for ref in validation['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    prior=read(INPUT/'result.json')
    with connect()as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
    for ref in prior['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    sources=read(BASE/'government-xl-georef-sparkle-heya-original-supports-20261008/support-inputs.json')['sources']
    rows=[r for r in sources if r['uid']==UID];assert len(rows)==1
    world=decode_original_world_triangles((ROOT/rows[0]['candidate']['path']).read_bytes())
    context=read(CONTEXT/'context.json')
    for name,sha in IMAGES:assert digest((CONTEXT/name).read_bytes())==sha
    proof=verify(census=read(INPUT/'diagnostic.json.gz'),world=world,context=context,image_refs=IMAGES)
    out=dict(**proof,sourceGeometryChanges=0,terrainGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,
        aiGeometryModelling=False,qualification='Named unchanged terminal facade visual-placement interpretation only. No mount/function/engineering/root or propagation credit. Both old rim failures remain; actual current four-world source/pose/finite/foreign/runtime and genuine mainbody-to-podium grade paths remain separate mandatory gates.')
    save(DOC/'proposal.json.gz',out)
    refs=[Path(__file__),INPUT/'result.json',INPUT/'diagnostic.json.gz',
        HERE/'heya_aqua_58_original_terminal_visual_placement_20261011.py',
        HERE/'test_heya_aqua_58_original_terminal_visual_placement_20261011.py',
        HERE/'xl-heya-aqua-source-census-v1-exact-completed-receipt-recovery-20261011.py',
        HERE/'xl-heya-aqua-completed-original-terminal-parts-context-v1-20261011.py',
        HERE/'xl-heya-aqua-terminal-parts-orthographic-context-v2-20261011.py']
    refs.extend(ROOT/r['path']for r in prior['evidenceRefs'])
    refs.extend(p for folder in [CONTEXT,VALIDATION,ARCHIVE]for p in folder.rglob('*')if p.is_file())
    refs.extend(p for p in (BASE/'government-xl-heya-aqua-completed-original-terminal-parts-context-v1-20261011').rglob('*')if p.is_file())
    spec=importlib.util.spec_from_file_location('heya58_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    # Exact serializer representation prevents the already diagnosed int-key/
    # tuple mismatch; source/geometry/numeric content remains completely equal.
    result=m.freeze(BATCH,'heya58-original-terminal-facade-visual-placement-source-only',refs,json.loads(json.dumps(out)))
    print(json.dumps(dict(jobId=result['jobId'],completeNamedParts=58,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
