"""New exact original surface-contact graph diagnosis; no old proof mutation."""
import json,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from exact_original_wall_contact_paths_20261009 import contact_paths
DOC=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-118230-exact-wall-graph'
CONTEXT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-118230-wall-context/diagnostic.json.gz'
GEOMETRY=HERE/'local/government-xl-two-harbourfront-terrain-continuation-v3-20261005/runtime-geometry.json.gz'
LEASE=HERE/'local/xl-terrain-recovery-20261009-118230-exact-wall-graph/reservation.json'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();lease=read(LEASE);assert reservations.heartbeat(lease)['ok'];d=read(CONTEXT);g=read(GEOMETRY)['rows'][0]
 tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 assert d['wholeSourceFaces']==len(tri)==19438 and d['sourceSHA256']==g['sourceSHA256']
 binding=d['originalOpenExteriorPaths']['sourceAndPhysicalBindings']
 def heartbeat(done,total):assert reservations.heartbeat(lease)['ok'];print(json.dumps({'graphFacesChecked':done,'eligibleFaces':total}),flush=True)
 proof=contact_paths(tri,d['faces'],d['affectedWallFaces'],expected_source_binding=binding,current_source_binding=binding,heartbeat=heartbeat)
 proof.update(uid=g['uid'],sourceSHA256=g['sourceSHA256'],evidenceRefs=[ref(p) for p in [Path(__file__),CONTEXT,GEOMETRY,HERE/'exact_original_wall_contact_paths_20261009.py',HERE/'test_exact_original_wall_contact_paths_20261009.py',HERE/'exact_original_shell_intersections_20261009.py']],historicalGeometryNotCurrentAcceptance=True)
 save(DOC/'diagnostic.json.gz',proof);print(json.dumps({'allAffectedHaveExactContactRoofPaths':proof['allAffectedHaveExactContactRoofPaths'],'additionalContacts':len(proof['additionalExactOriginalContacts']),'unresolvedPaths':[p['sourceFace'] for p in proof['paths'] if not p['hasExactPositiveDimensionPathToClearRoof']]}),flush=True)
if __name__=='__main__':
 import uuid
 claim=reservations.claim('two-harbourfront-exact-source-graph-'+str(uuid.uuid4()),['immutable-source-proof:xl-terrain-recovery-20261009-118230-exact-wall-graph'],batch=DOC.name,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 try:main()
 finally:assert reservations.release(read(LEASE))['ok']
