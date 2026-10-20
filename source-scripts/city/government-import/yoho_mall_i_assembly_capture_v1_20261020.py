"""Actual production renderer capture for eight unchanged mall assembly originals."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-assembly-capture-v1-20261020';DOC=BASE/BATCH
REC=BASE/'government-xl-yoho-mall-i-tower-recovery-v1-20261020';CAP=BASE/'government-xl-yoho-mall-i-private-runtime-v3-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [REC,CAP]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];refs.append(p);used[k]=pins[d][k];return read(p)
 mall=take(CAP,CAP/'selection.json.gz')['rows'][0];rows=take(REC,REC/'recovery.json')['rows'];mp=ROOT/'3d-viewer/city/data/manifest.json';manifest=take(CAP,mp);forms={};uids={r['uid']for r in rows}|{mall['uid']}
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for b in read(p)['buildings']:
   if b['uid']in uids:forms[b['uid']]=dict(building=b,tile=tile['url'],tileSHA256=digest(p.read_bytes()));refs.append(p)
 assert set(forms)==uids and forms[mall['uid']]==mall['source'];selected=[mall]
 for row in rows:
  source=forms[row['uid']];b=source['building'];native=row['native']['model'];matches=[c for c in native['matching']['officialCandidates']if c.get('objectId')==b['objectId']and c.get('buildingCSUID')==b['buildingCSUID']];assert len(matches)==1
  entry=dict(matches[0],**native['asset'],uid=row['uid'],modelId=row['modelId'],worldBounds=native['worldBounds'],triangles=row['triangles'],rootTranslation=[-834500,0,816500],recordedBaseHeight=b.get('baseHeightHKPD'),recordedTopHeight=b.get('topHeightHKPD'),placementReviewed=False,publicationApproved=False)
  p=ROOT/row['assetPath'];assert digest(p.read_bytes())==row['sourceSHA256']==entry['sha256'];refs.append(p);selected.append(dict(row,source=source,candidate=dict(path=row['assetPath'],entry=entry)))
 ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 save(DOC/'selection.json.gz',dict(rows=selected,manifestSHA256=digest(mp.read_bytes())))
 save(DOC/'input.json.gz',dict(rows=[dict(uid=r['uid'],entry=r['candidate']['entry'],building=r['source']['building'],path=r['candidate']['path'])for r in selected],currentManifest=ref(mp),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u)for u in manifest['officialModelCatalogues']],evidenceRefs=[ref(p)for p in refs]))
 tool=HERE/'yoho_mall_i_assembly_attributes_v1_20261020.mjs';subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 capture=read(DOC/'attributes.json.gz');assert capture['startEndAllInputsVerified']
 for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(tool);result=dict(uids=sorted(uids),loaded=len(capture['rows']),rejected=capture['rejected'],installationApproved=False,geometryChanges=0);save(DOC/'summary.json',result);module('yoho_assembly_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-original-actual-renderer-coordinate-capture',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
