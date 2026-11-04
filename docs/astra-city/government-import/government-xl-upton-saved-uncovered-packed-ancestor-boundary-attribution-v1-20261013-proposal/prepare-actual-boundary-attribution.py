from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import sys,json,subprocess
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_saved_uncovered_packed_ancestor_boundary_attribution_draft_v1_20261013 as a
P=Path(__file__).parent
pins=a.read(P/'draft-pins.json');refs=pins['codeRefs']+pins['inputRefs']+[a.ref(P/'draft-pins.json'),a.ref(Path(__file__))]
for q in refs:a.check(q)
commands=[]
def run(cmd,name):
 path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout)
 commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,r.returncode,path)
run([sys.executable,'-c',"import sys;sys.path.insert(0,'source-scripts/city/government-import');import upton_saved_uncovered_packed_ancestor_boundary_attribution_draft_v1_20261013;print('import PASS; no worker/lease')"],'actual-import.log')
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-schema-only.log')
_,receipt,attribution,nomination,raw,provenance,source,current,drawn,transform=a.load()
types=Counter();origins=Counter();tail_rows=0;seen=set()
for p in provenance:
 kind=p['kind'];assert kind in ['originalTIN','capturedCurrentRing','computedVerticalRuledJoin'];origins[kind]+=1
 exact=p.get('exactOriginalPlanePoints')
 if exact is not None:
  assert isinstance(exact,list)and len(exact)==3 and all(isinstance(v,list)and len(v)==3 and all(isinstance(x,str)for x in v)for v in exact)
  for v in exact:
   for x in v:F(x)
 if kind in ['originalTIN','capturedCurrentRing']:
  array=source if kind=='originalTIN'else current;inventory=nomination['wholeSourceOriginalFaceInventory']if kind=='originalTIN'else nomination['wholeCurrentFaceInventory'];i=p['originalFace']
  assert type(i)is int and 0<=i<len(array)and inventory[i]['originalFace']==i and inventory[i]['originalFaceSHA256']==a.prior.prior.sha(array[i])
  if p['computedFragment']:assert exact is not None
  if kind=='capturedCurrentRing':assert isinstance(p['completeCurrentSourceAttribution'],dict)and p['completeCurrentSourceAttribution']['globalCurrentFace']==i
 else:
  i=p['currentSurfaceFace'];assert type(i)is int and 0<=i<len(current)
  assert exact is not None and isinstance(p['origins'],list)and p['origins']
  assert isinstance(p['exactParameterInterval'],list)and len(p['exactParameterInterval'])==2
  for x in p['exactParameterInterval']:assert isinstance(x,str);F(x)
  for q in p['origins']:
   i=q['originalSourceFace'];assert type(i)is int and 0<=i<len(source)
   assert isinstance(q['exactCutEdge'],list)and len(q['exactCutEdge'])==2 and isinstance(q['cutCauses'],list)
   for v in q['exactCutEdge']:
    assert isinstance(v,list)and len(v)==3 and all(isinstance(x,str)for x in v)
    for x in v:F(x)
for r in attribution['rows']:
 key=(r['uid'],r['mode'],r['sourceFace']);assert key not in seen;seen.add(key)
 assert r['uid']in ['landsd/12728:0','landsd/79883:0']and r['rawCoverageFailureRetained']and r['entireSourceProjectionInsideCapturedDomain']
 if r['uid']=='landsd/79883:0':assert r['mode']=='capturedConstructorFloat32World'and r['sourceFace']==17
 else:assert r['mode']in ['original','literal','explicitLeftF32','explicitBalancedF32']
 assert a.prior.prior.sha(a.np.asarray(r['unchangedSourceXYZ'],dtype='<f8'))==r['sourceFaceSHA256']
 cov=r['exactSavedCoverageVerbatim'];kind=cov['method'];types[kind]+=1
 assert not cov['exactProjectionCovered']and cov['sourceFaceSHA256']==r['sourceFaceSHA256']and cov['completeGroundSHA256']==r['savedFiniteRecordVerbatim']['completeGroundSHA256']
 if kind=='closed-facet-interval-union':
  assert isinstance(cov['exactCoveredParameterThrough'],str)and isinstance(cov['firstExactParameterGaps'],list)
  reach=F(cov['exactCoveredParameterThrough']);assert 0<=reach<=1
  for lo,hi in cov['firstExactParameterGaps']:
   assert isinstance(lo,str)and isinstance(hi,str)and 0<=F(lo)<F(hi)<=1 and F(lo)==reach
  if not cov['firstExactParameterGaps']:assert reach<1;tail_rows+=1
 elif kind=='closed-facet-area-union':
  assert isinstance(cov['exactUncoveredAreaM2'],str)and isinstance(cov['exactSourceProjectedAreaM2'],str)
  assert 0<F(cov['exactUncoveredAreaM2'])<=F(cov['exactSourceProjectedAreaM2'])and type(cov['remainingPositiveAreaPieces'])is int and cov['remainingPositiveAreaPieces']>0
 else:raise AssertionError('Unexpected saved coverage kind')
 for g in r['selectedGroundProvenance']:
  assert a.prior.prior.sha(a.np.asarray(g['actualDrawTriplet'],dtype='<f8'))==g['actualDrawTripletSHA256']
  assert g['allExactCandidateFaceOrigins']and not g['candidateOriginAmbiguous']and not g['unmatchedCandidateOriginRemainsExplicit']
  for m in g['allExactCandidateFaceOrigins']:
   i=m['provenance']['candidateFace'];assert type(i)is int and 0<=i<11575 and m['provenance']==provenance[i]and a.prior.prior.sha(drawn[i])==g['actualDrawTripletSHA256']
assert len(seen)==357 and types=={'closed-facet-interval-union':104,'closed-facet-area-union':253}
proof=dict(passed=True,completeSavedNegativeRows=357,completeProvenanceRows=11575,allRealAncestorBoundsAndOriginalTripletHashesMatched=True,coverageKinds=dict(types),explicitTailGapRows=tail_rows,provenanceKinds=dict(origins),allGapTypesAndNeededSourceCurrentJoinKeysValidated=True,noCoverageUnionActorOrProofReplay=True)
proof_path=P/'actual-complete-real-schema-validation.json';assert not proof_path.exists();a.save(proof_path,proof)
for q in refs:a.check(q)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.prior.CURRENT
summary=dict(passed=True,caller=a.ref(Path(a.__file__)),driver=a.ref(Path(__file__)),commands=commands,realSchema=a.ref(proof_path),declaredCodePins=len(pins['codeRefs']),declaredInputPins=len(pins['inputRefs']),allPinsVerifiedBeforeAndEnd=True,currentManifestSHA256=a.prior.CURRENT,noWorkerLeaseOrDB=True)
path=P/'actual-readonly-preparation.json';assert not path.exists();a.save(path,summary);print(json.dumps(summary,sort_keys=True))
