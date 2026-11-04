"""Durable version-specific Vancor hold; no permanent rejection or live review write."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-vancor-complete-source-pair-current-hold-disposition-v1-20261011';DOC=BASE/BATCH
FOLDERS=['government-xl-vancor-two-original-crossing-classification-v1-20261011','government-xl-vancor-90824-current-original-identity-v1-20261011','government-xl-vancor-90824-current-basic-complete-collision-diagnostic-v1-20261011','government-xl-vancor-two-original-primary-relations-v1-20261011','government-xl-vancor-two-complete-original-interfaces-v1-20261011']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest)
 assert start['sha256']=='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
 for folder in FOLDERS:
  r=read(BASE/folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.extend(p for p in (BASE/folder).rglob('*')if p.is_file())
 crossing=read(BASE/FOLDERS[0]/'diagnostic.json.gz');assert crossing['classificationCounts']['proper-noncoplanar-triangle-relative-interior-crossing']==409
 identity=read(BASE/FOLDERS[1]/'indexed-diagnostic.json')['identity'];assert not identity['passed']
 actors=crossing['actors'];assert [a['uid']for a in actors]==['landsd/147956:0','landsd/90824:0']
 holds=[]
 for a in actors:
  p=ROOT/a['source']['path'];assert ref(p)==a['source'];refs.append(p)
  holds.append(dict(uid=a['uid'],sourceSHA256=a['sourceSHA256'],modelId=a['modelId'],completeFaces=a['completeFaces'],disposition='held-source-version-revisit',
   reasons=['complete-unchanged-pair-has409-proper-noncoplanar-triangle-interior-crossings',
    'sole-90824-basic-placeholder-has54-exact-surface-contacts-and20-strict-centroid-interior-witnesses-per-stream'if a['uid']=='landsd/147956:0'else
    'ordinary-source-identity-unrelated90825-foreign-excess3.0155348228139767-square-metres'],
   unresolvedGate='Complete original pair physical/collision interpretation and independent Woo Sung90825 foreign-source identity/geometry evidence',
   mayRevisitWith=['A newly pinned official revised source version that independently resolves the exact original source/source and current foreign conflicts',
    'Source-bound exact complete joint/interface evidence establishing a defensible physical role, without dropping faces or waiving any unrelated collision/terrain/support gate'],
   modelPermanentlyRejected=False,sourceCorruptClaim=False,sourceGeometryChanges=0,installationApproved=False))
 out=dict(uids=[a['uid']for a in actors],sourceDispositions=holds,currentManifest=start,
  preservedPositiveEvidence='669 original four-stream finite/support, ordinary foundation/runtime, two retained Pak sources and full6642-native separation passed. These do not clear the actual90824BASIC collision or409 original/original facet crossings.',
  classificationCounts=crossing['classificationCounts'],properSurfaceCrossingNotClosedSolidVolumetricProof=True,
  independentForeignIdentity=identity['freshCurrentIdentity'],sharedProviderStructureContextOnly='K314/66 Tower structure161072; not ownership/support/collision exemption',
  sourceOnly=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0,
  sourceGeometryChanges=0,modelReviewWrites=0,fullTINComputeDeferredAfterChangedEvidence=True,
  nextWork='Move to a separately actionable source identity lead; no unchanged pair/TIN rerun or permanent building rejection.')
 save(DOC/'disposition.json',out);assert ref(manifest)==start;refs.append(manifest)
 s=importlib.util.spec_from_file_location('vancor_exact_hold_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'complete-source-version-current-hold-disposition-no-review-write-no-permanent-rejection',refs,dict(uids=out['uids'],sourceDispositions=holds,sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(heldSources=2,newlyInstalled=0,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
