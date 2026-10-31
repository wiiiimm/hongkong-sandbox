"""Exact all-face contact checks of actual placed originals against corrected canopy."""
from pathlib import Path
import subprocess,uuid,numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_original_component_contacts_20261009 import exact_component_contacts
B=ROOT/'docs/astra-city/government-import';NAME='government-xl-villa-five-placed-canopy-collision-v1-20261015';DOC=B/NAME
UIDS=['landsd/89917:0','landsd/58497:0','landsd/63823:0','landsd/121309:0','landsd/148052:0']
def main():
 assert not DOC.exists();claim=reservations.claim('villa-placed-'+str(uuid.uuid4()),['source-context:'+NAME],batch=NAME,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();tool=HERE/'villa_five_placed_capture_v1_20261015.mjs';out=DOC/'placed.json.gz';subprocess.check_call(['node',str(tool),str(out.relative_to(ROOT))],cwd=ROOT);capture=read(out);assert set(r['uid'] for r in capture['rows'])==set(UIDS)
  old=B/'government-xl-villa-private-canopy-collision-v2-20261015';receipt=read(old/'result.json');pins={r['path']:r['sha256'] for r in receipt['evidenceRefs']};rendered=old/'rendered.json';assert digest(rendered.read_bytes())==pins[str(rendered.relative_to(ROOT))]
  canopy=np.concatenate([np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)] for r in read(rendered)['rows'] if r['mode']=='privateCandidate']);assert len(canopy)==148
  results=[]
  for row in capture['rows']:
   for mode in ['literal','leftAssociatedPerMultiplyAddFloat32WorldPosition','balancedPerMultiplyAddFloat32WorldPosition']:
    tri=np.concatenate([np.asarray(m[mode]).reshape(-1,3)[np.asarray(m['index']).reshape(-1,3)] for m in row['meshes']]);assert len(tri)==row['completeFaces'];contacts=exact_component_contacts(tri,list(range(len(tri))),canopy,list(range(len(canopy))));results.append(dict(uid=row['uid'],mode=mode,completeFaces=len(tri),contacts=contacts));print(row['uid'],mode,len(contacts['contacts']),flush=True)
  save(DOC/'contacts.json.gz',dict(rows=results));summary=dict(uids=UIDS,rows=[dict(uid=r['uid'],mode=r['mode'],completeFaces=r['completeFaces'],contacts=len(r['contacts']['contacts']))for r in results],fullAcceptance=False,sourceGeometryChanges=0,qualification='All drawn faces in literal and two declared Float32 matrix orders; surface contacts only, not universal GPU or containment approval.')
  save(DOC/'summary.json',summary)
  for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
  paths=[Path(__file__),tool,rendered,old/'result.json']+[ROOT/p for p in capture['inputHashes']]
  module('villa_placed_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(NAME,'complete-placed-original-canopy-surfaces',paths,summary)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
