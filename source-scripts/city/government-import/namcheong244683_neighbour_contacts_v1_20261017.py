"""Exact finite current surface contacts; no containment or publication claim."""
from pathlib import Path
import uuid,numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-namcheong244683-neighbour-contacts-v1-20261017';DOC=BASE/BATCH;CAP=BASE/'government-xl-namcheong244683-current-capture-v1-20261017';FOREIGN=BASE/'government-xl-namcheong244683-neighbour-geometry-v1-20261017/geometry.json.gz';RT=HERE/'local'/CAP.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists();g=read(RT);foreign=read(FOREIGN);pins=dict(g['inputHashes'])
 for p,h in foreign['inputHashes'].items():assert p not in pins or pins[p]==h;pins[p]=h
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/244683:0'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  own=g['rows'][0];tri=np.asarray(own['position']).reshape(-1,3)[np.asarray(own['index']).reshape(-1,3)];assert len(tri)==20645;rows=[]
  for f in foreign['rows']:
   assert not f.get('native');other=np.asarray(f['position']).reshape(-1,3)[np.asarray(f['index']).reshape(-1,3)];contacts=exact_finite_contacts(tri,list(range(len(tri))),other,list(range(len(other))));assert contacts['allPairsExamined'];row=dict(uid=f['uid'],sourceFaces=len(tri),foreignFaces=len(other),contacts=contacts);rows.append(row);save(DOC/(f['uid'].replace('/','-').replace(':','-')+'.json.gz'),row);print(f['uid'],len(contacts['contacts']),flush=True)
  save(DOC/'summary.json',dict(uid=own['uid'],sourceSHA256=own['sourceSHA256'],rows=[dict(uid=r['uid'],contacts=len(r['contacts']['contacts']))for r in rows],fullAcceptance=False,qualification='Complete captured runtime-source versus current fallback surfaces. Contacts require interpretation; absence is not containment proof.'))
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
  assert reservations.owns(lease)
  result=module('yoho_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'namcheong244683-current-four-neighbour-finite-contact-context-v1',[Path(__file__),FOREIGN,RT,CAP/'result.json',HERE/'namcheong244683_neighbour_geometry_v1_20261017.mjs',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',*[ROOT/p for p in pins]],dict(uids=[own['uid']],fullAcceptance=False,newlyInstalled=0));print(result['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
