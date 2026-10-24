"""Complete source-only fixed-.1m finite host diagnosis for Langham's 696 faces.

Hosts are original renderable upper bodies with a geometric path to native963;
that seed is explicitly unqualified. No role, root, native or current acceptance.
The whole-facet helper's false negatives stay raw; no threshold expansion.
"""
import importlib.util,json,time,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-disconnected-finite-host-diagnostic-v1';DOC=BASE/BATCH;GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1';VISUAL=BASE/'xl-terrain-recovery-20261011-langham-disconnected-original-context-v1';UID='landsd/79318:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();g=read(GRAPH/'diagnostic.json.gz');visual=read(VISUAL/'diagnostic.json.gz');receipt=read(GRAPH/'result.json')
 with connect()as con:con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 asset=next(ROOT/r['path']for r in visual['evidenceRefs']if r['sha256']==visual['sourceSHA256']);assert digest(asset.read_bytes())==visual['sourceSHA256'];t=decode_original_world_triangles(asset.read_bytes());assert digest(t.tobytes())==visual['completeOriginalWorldSHA256'];ids=visual['completeDisconnectedOriginalFaceIds'];bodies=visual['completeDisconnectedBodyIds'];assert len(ids)==696 and len(bodies)==95
 hosts_ids=sorted(f for i,c in enumerate(g['components'])if c['actorUID']==UID and i not in bodies for f in c['globalOriginalFaces']);hosts=t[hosts_ids];assert len(hosts_ids)+len(ids)+len(g['completeEdgeCensus'][0]['exactNonrenderingOriginalFaces'])==len(t)
 helper=HERE/'exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py';freeze=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py';refs=[ref(p)for p in [Path(__file__),GRAPH/'diagnostic.json.gz',GRAPH/'result.json',VISUAL/'diagnostic.json.gz',asset,helper,freeze,HERE/'exact_original_surface_coordinate_band_20261010.py',HERE/'exact_original_projection_coverage_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']];binding=dict(inputRefs=refs,completeOriginalWorldSHA256=digest(t.tobytes()),completeHostWorldSHA256=digest(hosts.tobytes()),completeHostOriginalFaceIds=hosts_ids,completeSourceOriginalFaceIds=ids)
 progress=HERE/'local'/BATCH/'compute-progress.json.gz';rows=[]
 if progress.exists():
  old=read(progress);assert old['binding']==binding;rows=old['rows'];assert [r['sourceFace']for r in rows]==ids[:len(rows)]
 claim=reservations.claim('langham-source-finite-host-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last_pulse=time.monotonic();last_output=last_pulse
 def pulse(force=False):
  nonlocal last_pulse
  if force or time.monotonic()-last_pulse>=20:assert reservations.heartbeat(lease)['ok'];last_pulse=time.monotonic()
 try:
  pulse(True)
  for f in ids[len(rows):]:
   p=verify(t[f],hosts);rows.append(dict(sourceFace=f,wholeFacetFiniteHostAssociation=p));pulse()
   if len(rows)%16==0 or len(rows)==len(ids):save(progress,dict(binding=binding,rows=rows,completeProof=False,currentAcceptance=False))
   if time.monotonic()-last_output>=20:print(dict(done=len(rows),total=len(ids),wholeFacetAssociations=sum(r['wholeFacetFiniteHostAssociation']['wholeFacetAssociated']for r in rows)),flush=True);last_output=time.monotonic()
  pulse(True);assert all(ref(ROOT/r['path'])==r for r in refs);assert [r['sourceFace']for r in rows]==ids
  by_body=[]
  for body in bodies:
   faces=g['components'][body]['globalOriginalFaces'];part=[r for r in rows if r['sourceFace']in faces];assert len(part)==len(faces);by_body.append(dict(body=body,completeOriginalFaces=faces,completeFacets=len(part),wholeFacetAssociatedFaces=sum(r['wholeFacetFiniteHostAssociation']['wholeFacetAssociated']for r in part),allWholeFacetsAssociated=all(r['wholeFacetFiniteHostAssociation']['wholeFacetAssociated']for r in part)))
  refs.append(ref(progress));result=dict(uids=[UID],binding=binding,completeSourceFaces=len(t),completeDisconnectedFaces=696,completeDisconnectedBodies=95,rows=rows,perBody=by_body,completeAll696FacetInventory=True,hostsConditionallyGeometricallyConnectedOnly=True,strictBandM=.1,rootedHostProved=False,sourceOnly=True,noFreshCurrentCapture=True,visualRoleAccepted=False,rootOrStructuralContactCredit=False,nativeReacceptance=False,currentAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('langham_finite_host_freeze',freeze);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-langham-disconnected-original-facet-fixed-finite-host-band-source-only-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],sourceOnly=True,currentAcceptance=False,completeDisconnectedFaces=696,completeDisconnectedBodies=95,wholeFacetAssociatedFaces=sum(r['wholeFacetFiniteHostAssociation']['wholeFacetAssociated']for r in rows),allFacetAssociatedBodies=sum(p['allWholeFacetsAssociated']for p in by_body),newlyInstalled=0));print(dict(complete=True,wholeFacetAssociatedFaces=sum(r['wholeFacetFiniteHostAssociation']['wholeFacetAssociated']for r in rows),allFacetAssociatedBodies=sum(p['allWholeFacetsAssociated']for p in by_body)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
