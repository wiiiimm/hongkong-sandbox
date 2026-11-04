"""Entire existing original back facets in the fixed visual host band; diagnosis."""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_orthogonal_finite_facade_band_20261010 import verify as surface_band
BATCH='xl-terrain-recovery-20261010-mei-yat-whole-facet-orthogonal-facade-leads-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH;assert not DOC.exists()
PHYS=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-mei-yat-original-physical-v3-20261010';SUP=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-mei-yat-complete-original-support-v1';g=read(SUP/'diagnostic.json.gz');r=read(PHYS/'selection.json.gz')['rows'][0];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];t=decode_original_world_triangles(asset.read_bytes());assert digest(t.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256'];rooted=set(g['resolvedOriginalComponents']);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n2=np.sum(norm*norm,axis=1);hosts=sorted(i for k in rooted for i in g['components'][k]['globalOriginalFaces'] if n2[i]>0 and norm[i,1]**2<=n2[i]/16);results=[]
for k in [76,77,722]:
 assert k not in rooted;ids=g['components'][k]['globalOriginalFaces'];rows=[]
 for i in ids:
  if n2[i]==0 or norm[i,1]**2>n2[i]/16:continue
  q=surface_band(t[i],t[hosts]);rows.append(dict(originalFace=i,completeSourceFacet=t[i].tolist(),wholeFiniteFacetBand=q,completeRootedOriginalHostFaceIndexMap=hosts));print(json.dumps(dict(component=k,face=i,associated=q['verifiedWholeOriginalFacetFiniteFacadeBand'])),flush=True)
 results.append(dict(component=k,completeOriginalFaces=ids,allOriginalVerticalFacetResults=rows,wholeOriginalVerticalFacetsInFixedHostBand=[q['originalFace'] for q in rows if q['wholeFiniteFacetBand']['verifiedWholeOriginalFacetFiniteFacadeBand']],visualMountAccepted=False,structuralRootCredit=False));save(DOC/'partial-diagnostic.json.gz',dict(uids=[r['uid']],complete=False,results=results))
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
refs=[ref(p) for p in [Path(__file__),asset,SUP/'diagnostic.json.gz',SUP/'result.json',PHYS/'selection.json.gz',HERE/'exact_original_facet_orthogonal_finite_facade_band_20261010.py',HERE/'test_exact_original_facet_orthogonal_finite_facade_band_20261010.py',HERE/'exact_packed_world_geometry_20261009.py']]
save(DOC/'diagnostic.json.gz',dict(uids=[r['uid']],completeOriginalWorldSHA256=digest(t.tobytes()),sourceSHA256=r['sourceSHA256'],results=results,sourceGeometryChanges=0,visualRoleAccepted=False,structuralRootCredit=False,evidenceRefs=refs,qualification='Diagnostic only. Whole original facet perpendicular distances use the fixed0.1m Euclidean band, with exact Fraction orthogonal feet covered by a finite closed union of actual coplanar rooted host facets. No tolerance or buffer. No exact-zero contact, fabricated back facet, structural root or role accepted.'))
spec=importlib.util.spec_from_file_location('back_facets_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'whole-original-facet-orthogonal-finite-host-band-diagnostic-v1',[ROOT/p['path'] for p in refs],dict(uids=[r['uid']],sourceGeometryChanges=0,visualRoleAccepted=False,structuralRootCredit=False))
