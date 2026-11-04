"""Freeze source/literal role and hermetic bindings; never current promotion."""
from pathlib import Path
import importlib.util,json,subprocess,sys
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from lippo_current_bound_six_roof_identity_v1_20261010 import DOC as INPUT,literal_measurements
from lippo_original_six_roof_current_scope_proposal_v2_20261010 import source_proof,OWN,FOREIGN
BATCH='government-xl-lippo-twelve-current-actor-source-literal-role-diagnostic-v1-20261010';DOC=INPUT.parent/BATCH
FIXTURE=DOC.parent/'government-xl-lippo-current-binding-hermetic-fixtures-v1-20261010'
def main():
 assert not DOC.exists();rows={r['uid']:r for r in read(INPUT/'selection.json.gz')['rows']};raws={u:(ROOT/r['candidate']['path']).read_bytes() for u,r in rows.items()}
 for u,r in rows.items():assert digest(raws[u])==r['sourceSHA256']
 originals={u:decode_original_world_triangles(raw) for u,raw in raws.items()};capture=read(INPUT/'current-inputs.json.gz');primary=read(INPUT/'exact-current-primary.json')['features']
 named=source_proof(raws[OWN],raws[FOREIGN],capture['forms'],primary);literal=literal_measurements(originals,capture['forms'],primary,read(INPUT/'literal-production-geometry.json.gz'),read(INPUT/'literal-complete-geometry-bindings.json.gz'))
 save(DOC/'diagnostic.json.gz',dict(sourceOnlyProposal=named,completeLiteralRoleChecks=literal,completeCurrentHistoricalForms=capture['forms'],historicalManifestSHA256=capture['manifestSHA256'],currentIdentityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Complete source/literal role evidence against the frozen current12actor scope. Historical input capture only; no current catalogue rebind or real full-cell production acceptance is claimed.'))
 log=DOC/'test-result.txt';DOC.mkdir(parents=True,exist_ok=True)
 with log.open('w') as f:subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_lippo_current_bound_six_roof_identity_v1_20261010.py'],cwd=ROOT,check=True,stdout=f,stderr=subprocess.STDOUT)
 refs=[Path(__file__),INPUT/'result.json',FIXTURE/'manifest-and-catalogue-bytes.json.gz',HERE/'lippo_current_bound_six_roof_identity_v1_20261010.py',HERE/'test_lippo_current_bound_six_roof_identity_v1_20261010.py',HERE/'lippo_original_six_roof_current_scope_proposal_v2_20261010.py',HERE/'lippo_three_original_current_inventory_20261010.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'xl-lippo-current-literal-production-geometry-v1-20261010.mjs',HERE/'xl-lippo-current-bound-six-roof-inputs-v1-20261010.py']
 refs += [p for p in INPUT.iterdir() if p.is_file()]+[ROOT/r['candidate']['path'] for r in rows.values()]
 s=importlib.util.spec_from_file_location('lippo_source_role_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 result=m.freeze(BATCH,'lippo-complete-twelve-actor-source-and-literal-exact-six-roof-role-diagnostic-v1',refs,dict(uids=sorted(rows),sourceOnlyRoleProposalSupported=True,identityAccepted=False,physicalAccepted=False,completeCurrentHistoricalForms=12,completeSourceLiteralRoleCombinations=4,testsPassed=29,rawFailuresPreserved=True,sourceGeometryChanges=0,qualification='Exact original/literal role proof only. Complete source/provider/current body95%/10m/1m2 numeric guards and all additional actors retained. Recovered Silvercord remains foreign/basic at runtime; no common ownership, support, collision, terrain or installation credit. Full fresh current-bound production replay remains required.'))
 print(json.dumps(dict(jobId=result['jobId'],sourceOnly=True,tests=29)),flush=True)
if __name__=='__main__':main()
