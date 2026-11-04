"""Source-specific physical interpretation; raw diagnostics and publication gates retained."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-victoria-mall-physical-interpretation-v1-20261020';DOC=BASE/BATCH
NAMES=['original-assembly-foundations-v2','render-mode-foundations-v1','render-support-v1','finite-segment-verification-v1','complete-join-review-v1','tower-support-v1','basic-fallback-browser-v1','protected-surface-equivalence-v1','neighbours-v5']
def folder(n):return BASE/('government-xl-victoria-mall-'+n+'-20261020')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];receipts={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in NAMES:
   p=folder(n)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p);receipts[n]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(n,name):
  p=folder(n)/name;assert digest(p.read_bytes())==receipts[n][str(p.relative_to(ROOT))],str(p);refs.append(p);return read(p)
 original=take('original-assembly-foundations-v2','summary.json');assert len(original['rows'])==3
 for row in original['rows']:
  f=row['foundation'];assert f['triangles']==f['completeTerrainTriangles'] and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
 render=take('render-mode-foundations-v1','summary.json');assert len(render['rows'])==12
 for row in render['rows']:assert row['passed']and row['buried']==row['upwardBuried']==0
 strict=take('render-support-v1','summary.json');assert len(strict['rows'])==9
 for row in strict['rows']:assert row['unresolved']=={'landsd/251609:0':5,'landsd/251614:0':0,'landsd/251615:0':4}[row['uid']]
 paths=take('finite-segment-verification-v1','summary.json');assert len(paths['rows'])==4
 for row in paths['rows']:assert row['targets']==row['finiteSameFaceSegments']==9 and row['maximumEndpointResidualM']<1e-10 and row['maximumAbsoluteNormalY']<.006
 joins=take('complete-join-review-v1','review.json');assert joins['allNineOriginalPairsCaptured']and len(joins['imagesActuallyInspected'])==9
 for image in joins['imagesActuallyInspected']:p=ROOT/image['path'];assert ref(p)['sha256']==image['sha256'];refs.append(p)
 basics=take('tower-support-v1','summary.json');assert len(basics['rows'])==3
 for row in basics['rows']:
  f=row['foundation'];assert f['triangles']==f['completeTerrainTriangles']and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
 fallback_path=folder('basic-fallback-browser-v1')/'ROOT-IMAGE-REVIEW.json';fallback=read(fallback_path);assert fallback['visualFallbackCheckPassed']and len(fallback['imagesActuallyViewed'])==4;refs.append(fallback_path)
 for im in fallback['imagesActuallyViewed']:p=ROOT/im['path'];assert ref(p)==im;refs.append(p)
 eq=take('protected-surface-equivalence-v1','equivalence.json');assert eq['allProtectedSurfacesIdentical']and len(eq['rows'])==19
 neighbours=take('neighbours-v5','summary.json');assert neighbours['neighbourForms']==43 and len(neighbours['nativeChecks'])==2
 for row in neighbours['nativeChecks']:assert row['passed']and row['terrain']['newlyWhollyBuried']==row['terrain']['newlyUpwardWhollyBuried']==0
 assert {r['uid']for r in neighbours['flagged']}=={'landsd/251609:0','landsd/251614:0','landsd/251615:0'}
 f=neighbours['foundation'];assert f['triangles']==f['completeTerrainTriangles']==21310 and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
 sourcepath=BASE/'government-xl-victoria-three-original-checked-20261009/support-inputs.json';sources=read(sourcepath)['sources'];refs.append(sourcepath)
 for row in sources:p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256'];refs.append(p)
 review=dict(reviewer='Codex ROOT',uids=sorted(r['uid']for r in sources),sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in sources},physicalInterpretationAccepted=True,rawStrictFailuresRetained=True,rawStrictRuntimeAccounts=strict['rows'],sourceContactAccounts=paths['rows'],basicFallbackDiagnostics=basics['rows'],neighbourFlagsRetained=neighbours['flagged'],sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,publication=False,remainingGates=['Complete full-frame original visual review','Guarded publication plan and current-input fences','Live installed verification and Neon installed evidence'],basis=[
 'Five Tower3 and four Tower1 low-rim witnesses are points on authored near-vertical wall faces that intersect the exact original podium. Independent finite same-face segment evidence reaches positive-dimensional podium contact in all four representations. The nine original-pair closeups were previously inspected and show raised podium edges beside these walls. The strict highest-surface diagnostic remains false; this accepts this exact embedded wall interface only, without a global tolerance change or engineering claim.',
 'All complete original tower foundations and twelve literal/Float32 source-foundation checks contain zero wholly buried faces. The current mall complete foundation also contains zero buried faces. The trimmed patch preserves identical drawn terrain facets beneath all19 original/fallback representations, so these source-bound proofs remain applicable.',
 'The three BASIC fallback towers are coarse bodies with their own floor elevation, not separate government support sources. Their shallow bottom embed and raised-edge warnings remain recorded; complete fallback foundations have zero wholly buried faces, and actual failed-download day/night exports retain all three visible tower bodies. This accepts their existing temporary fallback appearance, not strict equality of their floors to the detailed podium surface.',
 'The three increased terrain-gap warnings measure tower floors against terrain below the mall. Their support is the explicitly SHA/CSUID-bound original mall, not that terrain. The retained Tower3 full native check passes with all1037 low-rim samples over the pinned podium; the other affected native actor also passes with zero newly buried faces. All43 other form checks introduce no unrelated flag.',
 'Only exact unchanged four-source assembly and candidate terrain are covered. Any source, pose, terrain or dependency change requires fresh applicability. Final images and live publication remain separate.' ])
 save(DOC/'review.json',review)
 for p in refs:assert p.exists()
 module('victoria_physical_review',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-exact-original-physical-interpretation',list(dict.fromkeys(refs)),review)
 print('Exact Victoria physical interpretation recorded; publication still separate',flush=True)
if __name__=='__main__':main()
