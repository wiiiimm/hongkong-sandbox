"""Read all unfinished fixed XL sources by exact cache/model key; no queue writes."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','installed','inventory']:p.add_argument('--'+k,required=True)
 a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 report=take(a.installed,base/a.installed/'full-xl-current-count.json');inventory=take(a.inventory,base/a.inventory/'summary.json');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==report['manifestSHA256']==inventory['currentManifestSHA256'];refs.append(manifest)
 allrows=report['rows'];assert len(allrows)==len({r['sourceKey']for r in allrows})==521;pending={r['sourceKey']:r for r in allrows if not r['installedVerified']};forms={}
 for tile in read(manifest)['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];assert digest(path.read_bytes())==pins[a.inventory][str(path.relative_to(ROOT))];refs.append(path)
  for f in read(path)['buildings']:forms[f['uid']]=f
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  rows=db.execute("SELECT cache_key||'/'||model_id,viewer_uid,triangles,sheet,source_state,source_hold_reason,building_csuid,source_result_sha FROM astra_modelling.native_model_sizes WHERE run_id=%s AND cache_key||'/'||model_id=ANY(%s)",(NATIVE_RUN,list(pending))).fetchall()
 assert len(rows)==len(pending)and len({r[0]for r in rows})==len(pending)
 result=[]
 for key,nativeuid,n,sheet,state,hold,csuid,sha in rows:
  old=pending[key];uid=old['uid'];f=forms.get(uid,{})
  result.append(dict(sourceKey=key,uid=uid,nativeViewerUid=nativeuid,name=f.get('name'),triangles=n,sheet=sheet,originalNativeState=state,originalNativeHoldReason=hold,buildingCSUID=csuid,nativeResultSHA256=sha,indexedSourceSHA256=old['indexedSourceSHA256'],currentInstalled=False,installationApproved=False,permanentRejection=False))
 result.sort(key=lambda r:(r['triangles'],r['sourceKey']));summary=dict(uids=sorted({r['uid']for r in result if r['uid']}),fixedXLTotal=521,installed=sum(r['installedVerified']for r in allrows),unfinished=len(result),unmatchedViewerUIDs=sum(r['uid']is None for r in result),nativeRun=NATIVE_RUN,currentManifestSHA256=report['manifestSHA256'],currentNativeActors=inventory['currentNativeActors'],rows=result,installationApproved=False,qualification='All unfinished fixed-scope source keys joined exactly to repository-pinned native metadata. A shared, absent or changed viewer UID never substitutes for cacheKey/modelId. Original native acquisition states are historical source metadata, not current installation eligibility or permanent rejection. Diagnostics, temporary holds, approvals and publication remain separate. No optimisation or production queues written.')
 assert summary['installed']+summary['unfinished']==521;save(out/'summary.json',summary);module('unfinished_xl_inventory_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-current-fixed-xl-unfinished-exact-source-key-inventory',refs,summary);print({k:summary[k]for k in ['fixedXLTotal','installed','unfinished','unmatchedViewerUIDs']},flush=True)
if __name__=='__main__':main()
