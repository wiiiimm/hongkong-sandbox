"""Probe original Lantau meshes against current recorded LandsD heights without editing GLBs."""
import gzip, hashlib, json, shutil, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE_BATCH='government-lantau-final-14-20260921'
BATCH='government-lantau-height-align-20260921'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
STAGE=HERE/'accepted'/BATCH
LOCAL=HERE/'local'/BATCH
UIDS=('landsd/112959:0','landsd/182471:0','landsd/190939:0','landsd/192500:0','landsd/196549:0')
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(v,indent=2,sort_keys=True)+'\n').encode();p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return str(Path(p).relative_to(ROOT))
def main():
 frozen=read(ROOT/'docs/astra-city/government-import'/SOURCE_BATCH/'selection.json.gz')
 sources={r['uid']:r for r in frozen['rows'] if r['uid'] in UIDS}
 assert set(sources)==set(UIDS)
 exact={}
 for p in sorted((ROOT/'docs/astra-city/government-import').glob('government-*/exact-pass-results.json.gz')):
  for r in read(p)['rows']:
   if r['uid'] in UIDS:
    assert r['uid'] not in exact
    exact[r['uid']]=(p,r)
 assert set(exact)==set(UIDS)
 template=read(ROOT/'3d-viewer/city/data/official-models/government-discovery-bay-compute-20260921/catalogue.json')
 rows=[];models=[];forms=[];proof=[]
 for uid in UIDS:
  row=json.loads(json.dumps(sources[uid]));path,evidence=exact[uid];identity=evidence['identity']
  assert identity['exactObjectAndCSUID'] and identity['officialOverlapOfSmallerFootprint']>=.85
  assert identity['officialFootprintCentroidDistanceM']<=1
  assert identity['sourceProjectionInsideTarget']>=.87 and identity['targetCoveredBySourceProjection']>=.74
  entry=row['candidate']['entry'];original=json.loads(json.dumps(entry['worldBounds']))
  offset=entry['recordedTopHeight']-original[1][1]
  shifted=[[point[0],point[1]+offset,point[2]] for point in original]
  base_delta=shifted[0][1]-entry['recordedBaseHeight']
  assert 0<offset<=20 and abs(base_delta)<=1.1
  assert abs(shifted[1][1]-entry['recordedTopHeight'])<=.002
  entry.update(priority='detail',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,
   publicationApproved=False,proceduralWindows=False,retainsBasicForm=True,
   sourceWorldBounds=original,worldBounds=shifted,verticalPlacementOffsetHKPD=offset,
   verticalPlacementBasis='current-recorded-top-height',
   placementReview=(f'Exact government object and Building CSUID with {identity["officialOverlapOfSmallerFootprint"]:.3f} smaller-footprint overlap. '
    f'Unchanged GLB is translated vertically {offset:+.4f} m so its highest roof equals current recorded TopHeight {entry["recordedTopHeight"]:.1f} m HKPD; '
    f'corrected bottom differs from current recorded BaseHeight by {base_delta:+.4f} m. Horizontal geometry and all asset bytes remain unchanged.'))
  src=Path(row['candidate']['path']);dst=STAGE/entry['asset'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
  assert sha(dst)==entry['sha256']
  row['candidate']['path']=str(dst);rows.append(row);models.append(entry)
  form=dict(row['source']['building']);form['tile']=Path(row['source']['tile']).stem;forms.append(form)
  proof.append({'uid':uid,'sourceEvidence':rel(path),'sourceSHA256':entry['sha256'],'identity':identity,
   'sourceWorldBounds':original,'correctedWorldBounds':shifted,'verticalPlacementOffsetHKPD':offset,
   'correctedBottomDeltaFromBaseM':base_delta,'sourceGeometryChanged':False,'horizontalPlacementChanged':False})
 template.update(area='Lantau original government sources aligned to current recorded heights',
  coordinatePolicy='Unchanged source GLB bytes, nodes, vertices, indices, materials and XY placement; bounded vertical translation aligns roof to current LandsD TopHeight',
  loadingPolicy='Candidate only until identity, terrain, runtime and browser checks pass',counts={'packedModels':len(models)},models=models)
 save(STAGE/'catalogue.json',template);save(STAGE/'catalogue-index.json',{'models':len(models),'catalogues':['catalogue.json']})
 save(STAGE/'source-forms.json',forms);save(LOCAL/'source-forms.json',{r['uid']:r['source'] for r in rows})
 save(DOC/'placement-proof.json',{'batch':BATCH,'policy':'bounded-current-landsd-height-alignment-v1','rows':proof,'aiCalls':0,'modelGeometryChanges':0,'placementChanges':len(rows)})
 save(DOC/'selection.json.gz',{'batch':BATCH,'rows':rows,'manifestSHA256':sha(ROOT/'3d-viewer/city/data/manifest.json'),'aiCalls':0})
 save(DOC/'terrain-candidates.json',[])
 for cmd in (["node",str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(STAGE),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')],
  ["node",str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(STAGE),'--source-forms',rel(LOCAL/'source-forms.json'),'--out',rel(DOC/'validation.json')]):
  subprocess.run(cmd,cwd=ROOT,check=True)
 metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json')
 print(json.dumps({'metrics':[{k:r.get(k) for k in ('uid','error','minSurfaceGap','maxSamplerDelta','missingTerrain')} for r in metrics['rows']],
  'validation':[{k:r.get(k) for k in ('uid','outcome','error','concerns')} for r in validation['results']]}))
if __name__=='__main__':main()
