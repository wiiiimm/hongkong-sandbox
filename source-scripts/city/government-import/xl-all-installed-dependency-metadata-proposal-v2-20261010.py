"""Freeze a read-only exact installed-dependency proposal; no live writes."""
import importlib.util
import json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from verified_installed_dependency_metadata_20261010 import proposal,verify
BATCH='government-xl-all-installed-dependency-metadata-proposal-v2-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
MANIFEST='3a2f56f7980954ff3493aba5e8a015ca79153f81da55bb580e26bf5b2cdb2ee8'
SNAPSHOT='ee1a41d61d2de0fe'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();mp=ROOT/'3d-viewer/city/data/manifest.json';assert ref(mp)['sha256']==MANIFEST
 catalogues={};entries={};refs=[mp,Path(__file__),HERE/'verified_installed_dependency_metadata_20261010.py',HERE/'xl-all-installed-dependency-metadata-proposal-v1-20261010.py',HERE/'test_verified_installed_dependency_metadata_20261010.py']
 for url in read(mp)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;cat=read(path);catalogues[str(path.relative_to(ROOT))]=cat;refs.append(path)
  for e in cat['models']:assert e['uid'] not in entries;entries[e['uid']]=(e,path)
 wanted={uid for uid,(e,_) in entries.items() if any(isinstance(d,dict) and d.get('state')=='candidate' for d in e.get('supportDependencies',[]))}
 wanted|={d['uid'] for uid in list(wanted) for d in entries[uid][0]['supportDependencies'] if isinstance(d,dict) and d.get('state')=='candidate'}
 forms={};assets={};actors=[]
 for t in read(mp)['tiles']:
  path=ROOT/'3d-viewer'/t['url']
  for b in read(path)['buildings']:
   if b['uid'] in wanted:assert b['uid'] not in forms;forms[b['uid']]=b;refs.append(path)
 assert set(forms)==wanted
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');reviews={u:(s,h) for u,s,h in c.execute('SELECT uid,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s',(SNAPSHOT,)).fetchall()}
 for uid in sorted(wanted):
  e,cat=entries[uid];path=cat.parent/e['asset'];raw=path.read_bytes();assets[uid]=dict(sha256=digest(raw),bytes=len(raw));assert assets[uid]==dict(sha256=e['sha256'],bytes=e['bytes']);refs.append(path)
  actors.append(dict(uid=uid,entry=e,catalogue=ref(cat),asset=ref(path),assetBytes=len(raw),currentViewer=forms[uid],review=dict(state=reviews[uid][0],sourceSHA256=reviews[uid][1])))
 result=proposal(catalogues,reviews,forms,assets);assert verify(catalogues,result['catalogues'],reviews,forms,assets)==result
 assert len(result['retainedRelations'])==27;assert len(result['changes'])==210 and len({c['uid'] for c in result['changes']})==206 and len(actors)==254
 changed=sorted({c['catalogue'] for c in result['changes']});assert len(changed)==28;source_catalogues=sorted({a['catalogue']['path'] for a in actors});assert len(source_catalogues)==30
 save(DOC/'proposal.json.gz',dict(manifestSHA256=MANIFEST,snapshotId=SNAPSHOT,actors=actors,changes=result['changes'],retainedRelations=result['retainedRelations'],beforeCatalogues={p:catalogues[p] for p in source_catalogues},afterCatalogues={p:result['catalogues'][p] for p in source_catalogues},changedCatalogues=changed,priorUnfencedV1Guard='Thirty catalogue files contain all254actors, but only28 contain candidate-state owners; original v1 stopped before creating output on changed-catalogue count guard; no live mutation',newlyInstalled=0,sourceGeometryChanges=0,reviewStateChanges=0,identityAcceptance=False,physicalAcceptance=False,liveChanges=False))
 for i,path in enumerate(changed):save(DOC/('proposed-'+str(i)+'.json'),result['catalogues'][path])
 for uid in wanted:assert assets[uid]['sha256']==digest((entries[uid][1].parent/entries[uid][0]['asset']).read_bytes())
 assert ref(mp)['sha256']==MANIFEST
 for path,cat in catalogues.items():assert read(ROOT/path)==cat
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  end_reviews={u:(s,h) for u,s,h in c.execute('SELECT uid,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(SNAPSHOT,sorted(wanted))).fetchall()};assert end_reviews=={u:reviews[u] for u in wanted}
 spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
 f.freeze(BATCH,'complete-already-installed-exact-support-dependency-metadata-proposal-v1',sorted(set(refs)),dict(uids=sorted(wanted),candidateDependencies=210,affectedOwnEntries=206,exactAlreadyInstalledActors=254,changedCatalogueProposals=28,completeActorCatalogueInventory=30,missingStableCSUIDsAdded=108,existingFallbackOrLegacyRelationsRetained=27,liveCatalogueChanges=0,geometryChanges=0,reviewStateChanges=0,currentAcceptance=False,qualification='Read-only exact metadata proposal. Every candidate relation already references two unique current installed-verified source actors, whose full asset bytes and current UID/CSUID/object ID match. Only candidate state and missing exact CSUID metadata proposed. All fallback/legacy relations, existing source/identity/pose/edge fields and review states retained. Global publication/current capture stabilization, independent tests/runtime/rollback/archive review required before any correction.'))
 print(dict(proposedDependencies=210,actors=254,changedCatalogues=28,actorCatalogues=30,liveChanges=0),flush=True)
if __name__=='__main__':main()
