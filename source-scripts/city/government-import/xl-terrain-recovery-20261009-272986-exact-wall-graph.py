"""New exact original surface-contact graph diagnosis; no old proof mutation."""
import json,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from exact_original_wall_contact_paths_20261009 import contact_paths
DOC=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-272986-exact-wall-graph'
CONTEXT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-272986-wall-context/diagnostic.json.gz'
GEOMETRY=HERE/'local/government-xl-fourteen-positive-cell-sequence-20261008-272986-0/runtime-geometry.json.gz'
LEASE='/tmp/xl-terrain-recovery-20261009-272986-graph-lease.json'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();lease=read(LEASE);assert reservations.heartbeat(lease)['ok'];d=read(CONTEXT);g=read(GEOMETRY)['rows'][0]
 tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 assert d['wholeSourceFaces']==len(tri)==12314 and d['sourceSHA256']==g['sourceSHA256']
 binding=d['originalOpenExteriorPaths']['sourceAndPhysicalBindings']
 def heartbeat(done,total):assert reservations.heartbeat(lease)['ok'];print(json.dumps({'graphFacesChecked':done,'eligibleFaces':total}),flush=True)
 proof=contact_paths(tri,d['faces'],d['affectedWallFaces'],expected_source_binding=binding,current_source_binding=binding,heartbeat=heartbeat)
 proof.update(uid=g['uid'],sourceSHA256=g['sourceSHA256'],evidenceRefs=[ref(p) for p in [Path(__file__),CONTEXT,GEOMETRY,HERE/'exact_original_wall_contact_paths_20261009.py',HERE/'test_exact_original_wall_contact_paths_20261009.py',HERE/'exact_original_shell_intersections_20261009.py']],historicalGeometryNotCurrentAcceptance=True)
 save(DOC/'diagnostic.json.gz',proof);print(json.dumps({'allAffectedHaveExactContactRoofPaths':proof['allAffectedHaveExactContactRoofPaths'],'additionalContacts':len(proof['additionalExactOriginalContacts']),'paths':proof['paths']}),flush=True)
if __name__=='__main__':main()
