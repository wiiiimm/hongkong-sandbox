import json, subprocess, sys
from pathlib import Path
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city')
sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
from run import read, save, digest, connect
D=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261011-parkview-block16-two-parent-facet-proposal-frontier-partial3D-locus-atomic-boundary-scope-v6'
declared=read(D/'declared-scope.json')
old=read(ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261011-parkview-block16-source-scope-v1/declared-scope.json')
for k in ['historicalManifestAliases','metadataLeafPaths','metadataLeafJsonPointers']:
    assert declared[k]==old[k]
assert declared['unboundExactReferenceVersions']==[] and not declared['currentAcceptance']
for k in ['presentFileBindings','exactReferencedTrackedInputs','auditDeclarationContextRefs']:
    for pin in declared[k]: assert digest((ROOT/pin['path']).read_bytes())==pin['sha256']
out=Path('/tmp/xl-parkview-block16-boundary-root-verified-20261011.json')
subprocess.run([sys.executable,'/tmp/verify-closed-model-checkpoint-pointer-v5-all-input-hashmaps.py',str(D/'declared-scope.json'),str(out)],check=True,cwd=ROOT,stdout=subprocess.DEVNULL)
v=read(out); assert v['verifiedReferenceVersions']==65 and not v['historicalReferences']
rows=read(D/'agent-receipt-readback-verification.json')['rows']; assert len(rows)==6
with connect() as c:
    c.execute('SET TRANSACTION READ ONLY')
    for r in rows:
        receipt=read(ROOT/r['result']['path'])
        assert c.execute('SELECT status,result,owner,token FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',receipt,None,None)
        for pin in receipt['evidenceRefs']:assert digest((ROOT/pin['path']).read_bytes())==pin['sha256']
    reviews=c.execute('SELECT snapshot_id,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY snapshot_id',('landsd/256319:0',)).fetchall()
    assert reviews and all(r[1]!='installed-verified' for r in reviews)
notes=D/'ROOT_REVIEW.md'
notes.write_text('Root independently reran the unchanged exact-reference verifier:65 versions/14,007,640 bytes, all52 explicit file pins,23 exact tracked pins and prior audit pins verified. Independently read back all six complete Neon result objects with no owner/token. Inherited aliases/leaves/pointers are exactly unchanged. Root independently ran exact source-planar20,3D interval16,height-locus13 and atomic-network16 adversarial tests; all pass. Boundary-only producer was fully read before execution. Complete22536 exact edge comparisons add no segments; the174-segment network supplies no cycle enclosing positive-area interior of the two implicated parent domains. This proves only the bounded150/191 inventory obstruction. Original government building/TIN and current terrain bytes remain unchanged; zero installation/current-role credit. Hold evidence and specific next input are preserved; no global impossibility claim.\n')
paths=set(v['paths'])|{str(p.relative_to(ROOT)) for p in D.iterdir() if p.is_file()}
cert=D/'root-closed-scope.json'; paths.add(str(cert.relative_to(ROOT)))
save(cert,{**v,'paths':sorted(paths),'independentlyVerified':True,'sixNeonReceiptsIndependentlyReadBack':True,'inheritedMetadataContractsUnchanged':True,'currentAcceptance':False,'installationApproved':False,'newlyInstalled':0})
save(Path('/tmp/xl-parkview-block16-boundary-final-commit-scope-20261011.json'),{'paths':sorted(paths)})
print(json.dumps({'paths':len(paths),'versions':v['verifiedReferenceVersions'],'bytes':v['bytes'],'neonReadbacks':6,'installedCredit':0}))
