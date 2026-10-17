"""Stage a bounded Pui O/Mui Wo terrain-overlap correction and unchanged substation source."""
import gzip,hashlib,json,shutil,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BATCH='government-lantau-pui-o-bounded-probe-20260921';STAGE=HERE/'local'/BATCH;DOC=ROOT/'docs/astra-city/government-import'/BATCH
UID='landsd/195308:0';A=ROOT/'3d-viewer/city/data/terrain-mui-wo.json';B=ROOT/'3d-viewer/city/data/terrain-pui-o.json'
def read(p):
 p=Path(p);raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def save(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(v,separators=(',',':'))+'\n' if p.name.startswith('terrain-') else json.dumps(v,indent=2,sort_keys=True)+'\n').encode();p.write_bytes(gzip.compress(raw,mtime=0) if p.suffix=='.gz' else raw)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return str(Path(p).relative_to(ROOT))
def main():
 mui,pui=read(A),read(B);gm, gp=mui['meta']['georef'],pui['meta']['georef']
 assert gm['aE']==gp['aE']==5 and gm['aN']==gp['aN']==-5
 dc=int((gm['bE']-gp['bE'])//5);dr=int((gm['bN']-gp['bN'])//5)
 assert (dc,dr)==(182,854) and mui['h']==869 and pui['w']==379
 assert not mui.get('patches') or all(not (p['coarseCells'][1]<869 and p['coarseCells'][3]>854 and p['coarseCells'][0]<197 and p['coarseCells'][2]>0) for p in mui['patches'])
 assert not pui.get('patchExclusions')
 prior=list(pui['renderedElev']);corrected=list(prior)
 # The unchanged source occupies Pui O cells c=250..258, r=4..11. Only
 # a 125 m x 100 m local display-height envelope is changed; raw DTM stays.
 # Mui Wo owns the duplicated source cells, and Pui O joins its boundary.
 left,inner_left,inner_right,right,last=245,249,260,264,18
 def mui_y(c,r):
  v=mui['renderedElev'][(r+dr)*mui['w']+(c-dc)] if mui.get('renderedElev') else mui['elev'][(r+dr)*mui['w']+(c-dc)]
  return max(1.2,v) if v>0 else -4
 changed=0;max_delta=0
 for r in range(0,last+1):
  for c in range(left,right+1):
   i=r*pui['w']+c;old=prior[i] if prior[i] is not None else pui['elev'][i]
   if r<=14:desired=mui_y(c,r)
   else:
    anchor=mui_y(c,14)-(prior[14*pui['w']+c] if prior[14*pui['w']+c] is not None else pui['elev'][14*pui['w']+c])
    desired=old+anchor*(last-r)/(last-14)
   alpha=min(1,max(0,(c-left)/(inner_left-left)),max(0,(right-c)/(right-inner_right)))
   new=round(old+(desired-old)*alpha,6)
   if new!=old:changed+=1;max_delta=max(max_delta,abs(new-old))
   corrected[i]=new
 pui['renderedElev']=corrected;pui['patchExclusions']=[[inner_left,0,inner_right,14]]
 pui['meta']['renderedTransition']={**pui['meta'].get('renderedTransition',{}),'regionalOverlapCorrection':{'policy':'Bounded local overlap: Mui Wo source grid owns duplicate cells c=249..259, r=0..13. Pui O rendered heights join its edge within a 95m x 90m envelope; raw DTM unchanged.','muiWoSHA256':sha(A),'puiOOriginalSHA256':sha(B),'excludedCells':pui['patchExclusions'],'changedRenderedVertices':changed,'maxRenderedHeightAdjustmentM':max_delta}}
 terrain=STAGE/'terrain-pui-o-overlap-corrected.json';save(terrain,pui)
 proof={'uid':UID,'policy':'bounded-deduplicate-aligned-official-regional-terrain-v1','muiWoSHA256':sha(A),'puiOOriginalSHA256':sha(B),'correctedSHA256':sha(terrain),'rawElevationUnchanged':pui['elev']==read(B)['elev'],'sourceGeometryChanged':False,'excludedCells':pui['patchExclusions'],'changedRenderedVertices':changed,'maxRenderedHeightAdjustmentM':max_delta,'aiCalls':0}
 save(DOC/'terrain-proof.json',proof)
 source=read(ROOT/'docs/astra-city/government-import/government-lantau-final-14-20260921/selection.json.gz')
 row=next(r for r in source['rows'] if r['uid']==UID);row=json.loads(json.dumps(row));entry=row['candidate']['entry']
 entry.update(priority='detail',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,publicationApproved=False,proceduralWindows=False,retainsBasicForm=True,placementReview='Exact government object and Building CSUID, unchanged mesh; duplicated Mui Wo/Pui O terrain cells removed from the later patch and rendered seam blended. Script validation only.')
 asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['candidate']['path'],asset);assert sha(asset)==entry['sha256'];row['candidate']['path']=str(asset)
 template=read(ROOT/'3d-viewer/city/data/official-models/government-discovery-bay-compute-20260921/catalogue.json');template.update(area='Pui O Substation terrain overlap probe',counts={'packedModels':1},models=[entry]);save(STAGE/'catalogue.json',template);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
 save(DOC/'source-forms.json',{UID:row['source']});save(DOC/'selection.json.gz',{'batch':BATCH,'rows':[row],'manifestSHA256':sha(ROOT/'3d-viewer/city/data/manifest.json'),'aiCalls':0})
 save(DOC/'terrain-candidates.json',[{'path':rel(terrain),'sha256':sha(terrain),'replaces':{'url':'city/data/terrain-pui-o.json','sha256':sha(B)}}])
 subprocess.run(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(STAGE),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')],cwd=ROOT,check=True)
 subprocess.run(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(STAGE),'--source-forms',rel(DOC/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],cwd=ROOT,check=True)
 m=read(DOC/'metrics.json')['rows'][0];v=read(DOC/'validation.json')['results'][0]
 print(json.dumps({'terrain':proof,'metric':{k:m.get(k) for k in ('error','minSurfaceGap','minLowGap','maxLowGap','maxSamplerDelta','missingTerrain')},'validation':{k:v.get(k) for k in ('outcome','concerns','error')}}))
if __name__=='__main__':main()
