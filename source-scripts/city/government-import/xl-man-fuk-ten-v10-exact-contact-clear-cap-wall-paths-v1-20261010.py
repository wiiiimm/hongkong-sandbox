"""Replay complete source/literal wall paths through exact original contacts.

The prior edge-only failures stay frozen. Use only already inventoried contacts
within each unchanged actor; the unchanged cap-path kernel independently proves
all positive-dimensional contacts and strictly clear non-wall cap geometry.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_strict_clear_cap_wall_paths_20261009 import verify
from original_bound_facet_wall_context_20261010 import canonical
BASE=ROOT/'docs/astra-city/government-import';PHYSICAL=BASE/'government-xl-man-fuk-ten-original-coupled-physical-v3-20261010';WALL=BASE/'government-xl-man-fuk-ten-v10-complete-finite-wall-contexts-v1-20261010';GRAPH=BASE/'government-xl-man-fuk-ten-v10-complete-original-support-20261010';BATCH='government-xl-man-fuk-ten-v10-exact-contact-clear-cap-wall-paths-v1-20261010';DOC=BASE/BATCH

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);selection=read(PHYSICAL/'selection.json.gz');assert start['sha256']==selection['manifestSHA256']
 for folder in [PHYSICAL,WALL,GRAPH]:
  receipt=read(folder/'result.json')
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 graph=read(GRAPH/'diagnostic.json.gz');wall=read(WALL/'diagnostic.json.gz');runtime_path=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(runtime_path)['rows'];rows=[];assets=[]
 for row in selection['rows']:
  uid=row['uid'];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];assets.append(asset);tri=decode_original_world_triangles(raw)
  g=next(r for r in runtime if r['uid']==uid);actual=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
  actor=next(a for a in graph['actors'] if a['uid']==uid);lo,hi=actor['globalFaceRange'];assert hi-lo==len(tri) and actor['originalWorldTrianglesSHA256']==digest(tri.tobytes())
  contacts=[[i-lo for i in c['globalOriginalFaces']] for c in graph['contactWitnesses'] if all(lo<=i<hi for i in c['globalOriginalFaces'])]
  old=next(r for r in wall['rows'] if r['uid']==uid);modes=[]
  for mode,t in [('completeOriginal',tri),('actualRendered',actual)]:
   ctx=old[mode]['completeCertifiedLowerBoundContexts'];assert len(ctx)==len(t)
   binding=dict(completeOriginalWorldTrianglesSHA256=digest(t.tobytes()),completeCurrentFacetContextsSHA256=canonical(ctx),exactOriginalContactListSHA256=canonical(contacts))
   proof=verify(t,ctx,contacts,expected_binding=binding,current_binding=binding)
   modes.append(dict(representation=mode,binding=binding,completeCertifiedLowerBoundContexts=ctx,completeSourceContactPairs=contacts,strictClearCapWallPaths=proof,rawEdgeOnlyFailuresRetained=old[mode]['unresolvedWallConditions']))
   print(json.dumps(dict(uid=uid,representation=mode,affected=len(proof['affectedOriginalWallFaces']),allAffectedHavePaths=proof['allAffectedHavePaths'],rawExposureFailures=proof['rawExposureFailures'])),flush=True)
  rows.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(tri),sourceAndLiteralActualProofs=modes))
 result=dict(rows=rows,manifestSHA256=start['sha256'],rawPriorFailuresRetained=True,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False)
 save(DOC/'diagnostic.json.gz',result);assert ref(manifest)==start
 refs=[Path(__file__),manifest,PHYSICAL/'result.json',PHYSICAL/'selection.json.gz',WALL/'result.json',WALL/'diagnostic.json.gz',GRAPH/'result.json',GRAPH/'diagnostic.json.gz',runtime_path,HERE/'original_strict_clear_cap_wall_paths_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',*assets]
 s=importlib.util.spec_from_file_location('exact_contact_paths_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-source-and-literal-exact-contact-strict-clear-cap-wall-paths-v1',refs,dict(uids=[r['uid'] for r in rows],allSourceAndLiteralWallPathsPassed=all(p['strictClearCapWallPaths']['allAffectedHavePaths'] and not p['strictClearCapWallPaths']['rawExposureFailures'] for r in rows for p in r['sourceAndLiteralActualProofs']),rawPriorFailuresRetained=True,sourceGeometryChanges=0,fullAcceptance=False))
if __name__=='__main__':main()
