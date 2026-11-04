"""Exact Active primary identities/permit relationships; no ownership credit."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import'
OWN=BASE/'government-xl-king-cheung-95691-untouched-original-recovery-v1-20261011'
BATCH='government-xl-king-cheung-95691-primary-relations-v1-20261011';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);selections=[read(OWN/'check-selection.json.gz')];rows=[s['rows'][0]for s in selections];assert {r['uid']for r in rows}=={'landsd/95691:0'}and all(s['manifestSHA256']==start['sha256']for s in selections)
 refs=[Path(__file__),manifest,OWN/'check-selection.json.gz'];csuids=sorted(r['source']['building']['buildingCSUID']for r in rows);assert csuids==['3080039468T20140728']
 for folder in [OWN]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(folder/'result.json')
 DOC.mkdir(parents=True);spec=importlib.util.spec_from_file_location('king_cheung_exact_primary_query',HERE/'xl-man-fuk-man-oi-primary-relations-20261010.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);helper.DOC=DOC
 where='BuildingCSUID IN ('+','.join("'"+s+"'"for s in csuids)+')';primary=helper.query(0,where,'exact-current-one-primary',True);assert len(primary)==1 and sorted(r['attributes']['BuildingCSUID']for r in primary)==csuids and all(r['attributes']['Status']=='Active'for r in primary)
 relations=helper.query(1002,where,'exact-current-one-structure-relations');ids=sorted({r['attributes']['BuildingStructureID']for r in relations});structures=helper.query(1003,'BuildingStructureID IN ('+','.join(map(str,ids))+')','exact-current-structures')if ids else[]
 save(DOC/'diagnostic.json.gz',dict(uids=sorted(r['uid']for r in rows),primary=primary,relations=relations,structures=structures,currentManifest=start,currentForms={r['uid']:r['source']['building']for r in rows},sourceGeometryChanges=0,ownershipClaimed=False,sameNameParentPermitNeverCollisionExemption=True,physicalAccepted=False,currentAcceptance=False,installationApproved=False));assert ref(manifest)==start
 refs.append(HERE/'xl-man-fuk-man-oi-primary-relations-20261010.py');spec=importlib.util.spec_from_file_location('king_cheung_primary_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'exact-one-current-active-provider-permit-relationships-no-ownership-physics-credit',refs,dict(uids=sorted(r['uid']for r in rows),physicalAccepted=False,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(primary=len(primary),relations=len(relations),structures=len(structures))),flush=True)
if __name__=='__main__':main()
