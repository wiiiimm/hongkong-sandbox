"""Whole retained-native inventory and strictly exposed original carrier caps.

All native negatives persist; only131/root144 bridges ownedB. No native approval.
"""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from original_bound_facet_wall_context_v3_20261010 import contexts
from original_bound_facet_wall_context_20261010 import canonical,sha
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PAIRED=BASE/'xl-terrain-recovery-20261010-hkdi-complete-native-and-original-paired-finite-v1'
BATCH='government-xl-terrain-recovery-hkdi-block-b-current-exposed-native-cap-paths-v2-20261010';DOC=BASE/BATCH
spec=importlib.util.spec_from_file_location('hkdi_cap_paths_v1',HERE/'xl-terrain-recovery-20261010-hkdi-block-b-current-exposed-native-cap-paths-v1.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def current_rows(rows,actual):
 if not actual:return rows
 out=[]
 for row in rows:
  c=row['priorCoarseBoundProofVerbatim'];out.append(dict(sourceFace=row['sourceFace'],priorCoarseBoundProofVerbatim=dict(sourceFace=c['sourceFace'],completeOriginal=c['actualRendered']),pairedExactOriginalFiniteBound=row['pairedExactActualRenderedFiniteBound'],completeOriginalBoundProved=row['completeActualRenderedBoundProved']))
 return out

def recheck():
 result=prior.recheck();prior.receipt(PAIRED);pair=read(PAIRED/'diagnostic.json.gz');row=next(r for r in pair['rows']if r['uid']=='landsd/22089:0')
 s=next(r for r in read(prior.PHYS/'selection.json.gz')['rows']if r['uid']==row['uid']);asset=ROOT/s['candidate']['path'];assert digest(asset.read_bytes())==s['sourceSHA256']==row['sourceSHA256']
 tri=decode_original_world_triangles(asset.read_bytes());rt=next(r for r in read(HERE/'local'/prior.PHYS.name/'runtime-geometry.json.gz')['rows']if r['uid']==row['uid']);actual=np.asarray(rt['position']).reshape(-1,3)[np.asarray(rt['index']).reshape(-1,3)];ground=np.asarray(rt['drawnGroundGeometry']).reshape(-1,3,3)
 assert len(tri)==3965 and sha(tri)==row['completeOriginalWorldSHA256'] and sha(actual)==row['completeActualRenderedWorldSHA256'] and sha(ground)==row['completeGroundSHA256']
 contexts_by_mode=[]
 for name,world in [('completeOriginal',tri),('actualRendered',actual)]:
  rows=current_rows(row['allFaces'],name=='actualRendered');binding=dict(completeOriginalWorldTrianglesSHA256=sha(world),completeDrawnGroundSHA256=sha(ground),completeFiniteFacetProofRowsSHA256=canonical(rows))
  print('full retained-native contexts '+name,flush=True);contexts_by_mode.append(contexts(world,ground,rows,expected_binding=binding,current_binding=binding))
 bad=result['retainedNativeUnprovedOriginalFacesPreserved'];assert len(bad)==61
 components=read(prior.GRAPH/'diagnostic.json.gz')['components'];membership={f:i for i,c in enumerate(components[:157])for f in c['globalOriginalFaces']};assert set(membership)==set(range(3965))
 inventory=[]
 for i in bad:
  record=dict(sourceFace=i,completeOriginalComponent=membership[i],priorCoarseFaceProof=row['allFaces'][i]['priorCoarseBoundProofVerbatim'],completePairedFiniteProof=row['allFaces'][i],completeOriginalVertices=tri[i].tolist(),actualRenderedVertices=actual[i].tolist())
  for name,world,ctx in zip(['completeOriginal','actualRendered'],[tri,actual],contexts_by_mode):
   n=np.cross(world[i,1]-world[i,0],world[i,2]-world[i,0]);length=float(np.linalg.norm(n));ratio=float(n[1]/length)if length else None
   record[name]=dict(normal=n.tolist(),normalYRatio=ratio,sourceGeometryClass='upward'if ratio is not None and ratio>.15 else 'downward'if ratio is not None and ratio<-.15 else 'wall'if ratio is not None else 'exact-degenerate',completeFiniteContext=ctx[i],clearanceBoundProved=row['allFaces'][i]['completeOriginalBoundProved'if name=='completeOriginal'else'completeActualRenderedBoundProved'])
  inventory.append(record)
 for i in result['completeQualifiedCarrierCapFaces']:
  assert i not in bad
  for ctx in contexts_by_mode:assert F(ctx[i]['exactCertifiedLowerClearanceM'])>0 and ctx[i]['groundProjectionCovered']is True,'Credited cap is not strictly above all finite terrain'
 result.update(contract='hkdi-ownedB-complete-source-literal-strictly-exposed-current-native-cap-path-diagnostic-v2',all3965RetainedNativeFacesAccounted=True,completeRaw61AffectedNativeFaceInventory=inventory,pairedRemainingOriginalFailures=row['unprovedOriginalFaces'],pairedRemainingActualFailures=row['unprovedActualRenderedFaces'],creditedCapsStrictlyAboveCompleteCurrentGround=True,completeCarrierCapsSourceContexts=[contexts_by_mode[0][i]for i in result['completeQualifiedCarrierCapFaces']],completeCarrierCapsActualContexts=[contexts_by_mode[1][i]for i in result['completeQualifiedCarrierCapFaces']])
 result['evidenceRefs']+=[ref(p)for p in [Path(__file__),PAIRED/'result.json',PAIRED/'diagnostic.json.gz',HERE/'original_bound_facet_wall_context_v3_20261010.py',HERE/'original_bound_facet_wall_context_v2_20261010.py',HERE/'original_bound_facet_wall_context_20261010.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py']]
 return result

def main():
 assert not DOC.exists();r=recheck();save(DOC/'diagnostic.json.gz',r)
 spec=importlib.util.spec_from_file_location('hkdi_cap_v2_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'complete-current-native-61-face-inventory-and-strict-positive-source-literal-carrier-caps-v2',[ROOT/x['path']for x in r['evidenceRefs']],dict(uids=prior.UIDS,completeOwnedBParts=345,allOwnedBPartsQualified=True,completeNativeFaces=3965,completeRawAffectedNativeFaces=61,creditedCapsStrictlyAboveCompleteCurrentGround=True,nativeReacceptance=False,fullAcceptance=False,diagnosticOnly=True))
 print(json.dumps(dict(all345OwnedBPartsQualified=True,raw61NativeFacesAccounted=True,capsStrictlyExposed=True,remainingNativeFailures=r['pairedRemainingOriginalFailures'])),flush=True)
if __name__=='__main__':main()
