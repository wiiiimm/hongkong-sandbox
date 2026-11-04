"""Exact original Hoi Shing + actual underlying original podium interfaces."""
from pathlib import Path
import importlib.util,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
from exact_original_shared_edge_component_census_v2_20261011 import census,exact_nonrendering
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-underlying-original-pair-interfaces-v1';DOC=BASE/BATCH;OWN=BASE/'xl-terrain-recovery-20261011-hoi-shing-installed-market-original-interfaces-v1';PODIUM=BASE/'xl-terrain-recovery-20261011-hoi-shing-underlying-podium-original-recovery-v1';UIDS=['landsd/318801:0','landsd/318830:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [OWN,PODIUM]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(ref(folder/'result.json'))
 prior=read(OWN/'diagnostic.json.gz')['completeOriginalSources'][0];podium=read(PODIUM/'selection.json.gz')['rows'][0];assert prior['uid']==UIDS[0]and podium['uid']==UIDS[1];assets=[ROOT/prior['source']['path'],ROOT/podium['candidate']['path']];worlds=[decode_original_world_triangles(p.read_bytes())for p in assets];assert[digest(p.read_bytes())for p in assets]==[prior['completeSourceSHA256'],podium['sourceSHA256']];assert[len(w)for w in worlds]==[13841,5533];parts=[]
 for uid,w,p in zip(UIDS,worlds,assets):
  zero=[i for i,f in enumerate(w)if exact_nonrendering(f)];render=sorted(set(range(len(w)))-set(zero));parts.append(dict(uid=uid,source=ref(p),completeWorldSHA256=digest(w.tobytes()),completeOriginalFaces=len(w),exactNonrenderingFacesRetained=zero,completeRenderableFaceIds=render,completeNonzeroSharedEdgeCensus=census(w,render)))
 claim=reservations.claim('hoi-shing-underlying-original-pair-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  contact=exact_component_contacts(worlds[0],parts[0]['completeRenderableFaceIds'],worlds[1],parts[1]['completeRenderableFaceIds']);assert contact['allPairsExamined']and reservations.heartbeat(lease)['ok'];refs.extend(ref(p)for p in [*assets,OWN/'diagnostic.json.gz',PODIUM/'selection.json.gz',PODIUM/'historical-current-manifest.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py']);assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uids=UIDS,completeOriginalSources=parts,completeEveryRenderableSourcePairContactInventory=contact,positiveOriginalContacts=sum(p['dimension']>0 for p in contact['contacts']),pointOnlyOriginalContacts=sum(p['dimension']==0 for p in contact['contacts']),priorWrongInstalledCarrierNegativeReceipt=ref(OWN/'diagnostic.json.gz'),frozenRecoveryBaselineManifest=ref(PODIUM/'historical-current-manifest.json'),sourceOnly=True,noFreshCurrentCapture=True,identityGroupingProved=False,structuralRootCredit=False,currentAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out);s=importlib.util.spec_from_file_location('freeze_hoi_shing_pair',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-original-hoi-shing-underlying-podium-exact-source-interface-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,sourceOnly=True,positiveContacts=out['positiveOriginalContacts'],pointOnlyContacts=out['pointOnlyOriginalContacts'],currentAcceptance=False,newlyInstalled=0));print(dict(positiveContacts=out['positiveOriginalContacts'],pointOnlyContacts=out['pointOnlyOriginalContacts']),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
