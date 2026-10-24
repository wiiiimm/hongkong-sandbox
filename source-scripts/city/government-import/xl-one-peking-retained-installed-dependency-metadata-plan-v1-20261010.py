"""Read-only root-owned proposal; no live catalogue or source mutation."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from retained_installed_dependency_metadata_plan_20261010 import EXPECTED,corrected,verify
BATCH='government-xl-one-peking-retained-installed-dependency-metadata-plan-v1-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
MANIFEST='3a2f56f7980954ff3493aba5e8a015ca79153f81da55bb580e26bf5b2cdb2ee8'
SNAPSHOT='ee1a41d61d2de0fe'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==MANIFEST;m=read(manifest)
 wanted=set(EXPECTED)|{d[0] for d in EXPECTED.values()};entries={};refs=[manifest,Path(__file__),HERE/'retained_installed_dependency_metadata_plan_20261010.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl_source_stream_binding_20261009.py'];catalogues={}
 for u in m['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/u;cat=read(path)
  for e in cat['models']:
   if e['uid'] not in wanted:continue
   assert e['uid'] not in entries;entries[e['uid']]=(e,path);catalogues[path]=cat;refs.append(path)
 assert set(entries)==wanted;forms={}
 for tile in m['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  for b in read(path)['buildings']:
   if b['uid'] not in wanted:continue
   assert b['uid'] not in forms;forms[b['uid']]=dict(building=b,tile=ref(path));refs.append(path)
 assert set(forms)==wanted;actors=[]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for uid in sorted(wanted):
   entry,cat=entries[uid];asset=cat.parent/entry['asset'];raw=asset.read_bytes();assert digest(raw)==entry['sha256'] and len(raw)==entry['bytes'];refs.append(asset)
   b=forms[uid]['building'];assert b['buildingCSUID']==entry['buildingCSUID'] and b['uid']==entry['uid'] and b['structureType']==entry['structureType'] and str(b['objectId'])==str(entry['objectId'])
   neon=c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(SNAPSHOT,uid)).fetchone();assert neon==('installed-verified',entry['sha256'])
   world=decode_original_world_triangles(raw);assert len(world)==entry['triangles']
   actors.append(dict(uid=uid,entry=entry,catalogue=ref(cat),asset=ref(asset),currentViewer=forms[uid],completeSourceStreams=source_stream_binding(raw),completeOriginalFaces=len(world),originalWorldSHA256=digest(world.tobytes()),neon=dict(snapshotId=SNAPSHOT,reviewState=neon[0],sourceSHA256=neon[1])))
 corrections=[]
 for uid,(target,_) in EXPECTED.items():
  before,cat=entries[uid];support=entries[target][0];after=corrected(before,support);assert verify(before,after,support)
  corrections.append(dict(uid=uid,supportUID=target,catalogue=ref(cat),before=before,after=after,allowedChanges=['supportDependencies/0/state:candidate→installed']+(['supportDependencies/0/csuid:add exact current stable identifier'] if 'csuid' not in before['supportDependencies'][0] else [])))
 proposal=dict(manifestSHA256=MANIFEST,snapshotId=SNAPSHOT,actors=actors,corrections=corrections,sourceGeometryChanges=0,liveCatalogueChanges=0,publication=False,metadataCorrectionApplied=False,physicalAccepted=False,qualification='Root-owned metadata-only correction proposal. All four actors already uniquely installed and source-hash verified in current Neon snapshot. Only explicit dependency state changes and one missing exact CSUID addition permitted; every other field/source/edge remains exact. Independent root review/reservations/publication and fresh One Peking inputs required.')
 save(DOC/'proposal.json.gz',proposal)
 for p in sorted(catalogues):
  proposed=json.loads(json.dumps(catalogues[p]))
  for e in proposed['models']:
   if e['uid'] in EXPECTED:e.update(corrected(e,entries[EXPECTED[e['uid']][0]][0]))
  destination=DOC/('proposed-'+str(len(list(DOC.glob('proposed-*.json'))))+'.json');save(destination,proposed)
 assert digest(manifest.read_bytes())==MANIFEST
 for p in refs:
  if p in catalogues:assert read(p)==catalogues[p]
 s=importlib.util.spec_from_file_location('retained_metadata_proposal_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
 f.freeze(BATCH,'two-exact-retained-current-installed-dependency-metadata-proposal-v1',sorted(set(refs)),dict(uids=sorted(wanted),manifestSHA256=MANIFEST,snapshotId=SNAPSHOT,correctionEntries=2,exactCurrentInstalledActors=4,sourceGeometryChanges=0,liveCatalogueChanges=0,metadataCorrectionApplied=False,physicalAccepted=False,publication=False))
 print(dict(corrections=2,installedActors=4,liveChanges=0),flush=True)
if __name__=='__main__':main()
