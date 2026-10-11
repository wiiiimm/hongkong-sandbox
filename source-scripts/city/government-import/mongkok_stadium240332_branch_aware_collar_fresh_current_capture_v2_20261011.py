"""DRAFT fresh real production terrain capture; no old-current relabel or candidate."""
import argparse,json,subprocess
import numpy as np
from fractions import Fraction as F
from run import ROOT,HERE,read,save,connect
from exact_resumable_projected_inventory_v1_20261011 import decoded
from mongkok_stadium240332_branch_aware_full_source_edge_collar_feasibility_v2_20261011 import ref,validation_gate,B,P,OLD,CAP,CAPNAME
JS=HERE/'mongkok_stadium240332_branch_aware_collar_fresh_current_ground_v2_20261011.mjs';POINTER=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
def state(uids):
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(sorted(uids),)).fetchall()
def outward(q,lower):
 v=float(q)
 if lower and F(v)>q or not lower and F(v)<q:v=float(np.nextafter(v,-np.inf if lower else np.inf))
 assert F(v)<=q if lower else F(v)>=q
 return v
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--expected-manifest',required=True);ap.add_argument('--expected-native-count',required=True,type=int);a=ap.parse_args();assert not(CAP/'diagnostic.json.gz').exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';mr=ref(manifest);assert mr['sha256']==a.expected_manifest;refs=validation_gate()+[mr,ref(POINTER),ref(JS),ref(OLD/'exact-source-bound-domain.json.gz'),ref(OLD/'diagnostic.json.gz')];d=decoded(read(OLD/'exact-source-bound-domain.json.gz'));old=decoded(read(OLD/'diagnostic.json.gz'));assert len(d['computeBandPolygons'])==2666 and len(d['completeOuterBoundarySegments'])==520 and d['explicitWidthM']==10;uids=old['allProtectedReviewUIDs'];before=state(uids);entries=[]
 for cat in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/cat;refs.append(ref(p))
  for e in read(p)['models']:entries.append(dict(catalogue=ref(p),entry=e))
 assert len(entries)==a.expected_native_count and len({e['entry']['uid']for e in entries})==len(entries)
 for src,name in [(manifest,'actual-current-manifest.json'),(POINTER,'actual-current-source-review-pointer.json')]:
  dst=CAP/name;assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes());assert ref(dst)['sha256']==ref(src)['sha256'];refs.append(ref(dst))
 def fence():assert all(ref(ROOT/e['path'])==e for e in refs)and state(uids)==before
 fence();bounds=[outward(q,i<2)for i,q in enumerate(d['exactWholeDomainXZBounds'])];inp=CAP/'current-inputs.json.gz';out=CAP/'complete-current-ground-and-parent-routing.json.gz';assert not inp.exists()and not out.exists();save(inp,dict(uid='landsd/240332:0',currentManifest=mr,completeOutwardRoundedDomainXZBounds=bounds,evidenceRefs=refs));subprocess.run(['node',str(JS),str(inp.relative_to(ROOT)),str(out.relative_to(ROOT))],cwd=ROOT,check=True);g=read(out);assert g['currentManifest']==mr and g['startEndAllInputsVerified']and g['restoredParentCapturedByRemovingOnlyProtectedTerrainLayer'];historical_ground=read(OLD/'complete-current-ground-and-parent-routing.json.gz');runtime_modules={p:h for p,h in historical_ground['inputHashes'].items()if p.startswith('3d-viewer/')and p.endswith(('.js','.mjs'))};assert runtime_modules and all(g['inputHashes'].get(p)==h for p,h in runtime_modules.items()),'Production source/terrain/height-index runtime changed; unchanged kernel rebind unqualified';assert all(ref(ROOT/p)['sha256']==h for p,h in g['inputHashes'].items());refs.extend([ref(inp),ref(out)]+[dict(path=p,sha256=h)for p,h in g['inputHashes'].items()]);fence();save(CAP/'diagnostic.json.gz',dict(sourceOnly=True,currentAcceptance=False,noCandidate=True,noMeshOutput=True,sourceGeometryChanges=0,liveTerrainChanges=0,currentManifest=mr,allProtectedReviewUIDs=uids,protectedReviewStateUnchanged=True,exactHistoricalProductionModulesUnchanged=runtime_modules,completeCurrentNativeCatalogueEntries=entries,completeCurrentNativeCount=len(entries),completeActualTerrainMeshes=g['completeGlobalActualMeshes'],completeGlobalActualFacetsTraversed=g['completeGlobalActualFacetsTraversed'],completeClosedRoutingMaskGroundFacets=len(g['completeClosedDomainAABBActualGroundFacets']),actualGroundCapture=ref(out),exactFrozenDomain=ref(OLD/'exact-source-bound-domain.json.gz'),sourceOnlyHistoricalOldReceipt=ref(OLD/'result.json'),qualification='Honest fresh production terrain/world/module/catalogue capture against ROOT stable manifest; old df35 domain/receipt historical only. Full scene terrain drawn attributes traversed; all current native catalogue entries rebound as inventory, not whole native geometry clearance. No candidate/acceptance/source or terrain change.',evidenceRefs=refs));print(json.dumps(dict(nativeCount=len(entries),capturedFacets=len(g['completeClosedDomainAABBActualGroundFacets']),currentAcceptance=False)))
if __name__=='__main__':main()
