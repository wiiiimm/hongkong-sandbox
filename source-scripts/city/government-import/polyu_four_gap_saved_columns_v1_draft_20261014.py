"""Bounded local saved-input analysis only: no DB, leases, terrain or acceptance."""
from pathlib import Path
from fractions import Fraction as F
import gzip,json,hashlib,struct,sys,subprocess,time
import numpy as np
from upton_saved_guard_source_column_v1_20261012 import assess
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;BASE=ROOT/'docs/astra-city/government-import'
P=BASE/'government-xl-polyu-four-gap-source-compatible-parent-regions-v1-20261014-proposal'
FEAS=BASE/'government-xl-polyu-nine-complete-parent-restoration-feasibility-v1-20261013/complete-nine-parent-restoration-feasibility.json.gz'
GUARD=BASE/'government-xl-polyu-append-source-region-historical-production-v1-20261014/all25-original-production-guard-site-replay.json.gz'
JS=HERE/'polyu_four_gap_saved_boundary_v1_draft_20261014.mjs'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x')as f:json.dump(v,f,sort_keys=True,separators=(',',':'),allow_nan=False);f.write('\n')
def load():
 feasibility=read(FEAS);source_ref=feasibility['exactSourceContext'];source_path=ROOT/source_ref['path'];assert ref(source_path)==source_ref
 source=read(source_path);worlds={}
 for mode,row in source['completeWorldStreams'].items():
  raw=np.asarray(row['completeWorldTriangles'],dtype='<f8');assert raw.shape==(10536,3,3)and np.isfinite(raw).all()
  assert hashlib.sha256(raw.tobytes()).hexdigest()==row['completeWorldTriangleSHA256']
  worlds[mode]=(raw,raw[:,:,[0,2]].min(1),raw[:,:,[0,2]].max(1),row['completeWorldTriangleSHA256'])
 assert len(worlds)==4
 return feasibility,source_ref,source,worlds,read(GUARD)
def main():
 assert '--preview-eight-per-actor-only'in sys.argv or '--analyze-complete-failed-sites-only'in sys.argv
 preview='--preview-eight-per-actor-only'in sys.argv;tag='preview-eight'if preview else'complete-failed';output=P/(tag+'-saved-column-analysis.json');assert not output.exists()
 feasibility,source_ref,source,worlds,guards=load();inputs=[ref(FEAS),ref(GUARD),source_ref,ref(JS),ref(HERE/'upton_saved_guard_source_column_v1_20261012.py'),ref(HERE/'exact_original_triangle_pair_column_gap_20261010.py'),ref(Path(__file__))]
 boundary=P/(tag+'-actual-binary64-guard-boundaries.json');P.mkdir(parents=True,exist_ok=True)
 command=['node',str(JS),str(GUARD),str(boundary)]
 with(P/(tag+'-boundary.log')).open('xb')as log:proc=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 assert proc.returncode==0;bounds=read(boundary);assert bounds['sourceGuardBytesSHA256']==ref(GUARD)['sha256']
 rows=[];cache={};start=time.monotonic()
 for actor in bounds['rows']:
  g=next(r for r in guards['rows']if r['uid']==actor['uid']);threshold=actor['boundary']['minimumAcceptedBinary64HeightM']
  assert struct.pack('>d',threshold).hex()==actor['boundary']['minimumHeightBitsHex']
  ids=actor['failedSampleIDs'];assert len(ids)>0
  # Worst saved after height first, deterministic ties; preview is not completeness.
  if preview:ids=sorted(ids,key=lambda i:(g['rows'][i]['afterHeight'],i))[:8]
  records=[]
  for sample_id in ids:
   sample=g['rows'][sample_id];assert sample['sample']==sample_id and sample['samplerError']is None
   point=np.asarray([sample['x'],sample['z']],dtype='<f8');assert [struct.pack('>d',v).hex()for v in point]==sample['pointBitsHex']
   modes=[]
   for mode,(raw,lo,hi,world_sha)in worlds.items():
    selected=np.flatnonzero(np.all(lo<=point,axis=1)&np.all(hi>=point,axis=1));columns=[]
    for i in selected:
     key=(raw[i].tobytes(),tuple(sample['pointBitsHex']),actor['boundary']['minimumHeightBitsHex'])
     if key not in cache:cache[key]=assess(raw[i],point,threshold)
     proof=cache[key];column=proof['completeClosedSourceColumn']
     if not column['exactClosedHorizontalProjectionsMeet']:continue
     ceiling=None if proof['exactSourceNonrendering']else F(threshold)+F(column['exactMinimumFiniteColumnGapM'])+F(1,2)
     columns.append(dict(sourceFace=int(i),wholeSourceFaceSHA256=hashlib.sha256(raw[i].tobytes()).hexdigest(),proof=proof,
      exactMaximumOrdinaryCompatibleHeightM=None if ceiling is None else str(ceiling),
      savedBeforeHeightOrdinaryConflict=bool(ceiling is not None and F(sample['beforeHeight'])>ceiling)))
    modes.append(dict(arithmetic=mode,wholeSourceWorldSHA256=world_sha,completeSourceFaces=10536,closedAABBCandidates=selected.tolist(),allOtherSourceFacesStrictlyOutsidePoint=True,
      actualClosedSourceColumns=columns,minimumAcceptedGuardHeightOrdinaryConflict=any(c['proof']['ordinaryConflictAtSmallestAcceptedHeight']for c in columns),
      savedBeforeHeightOrdinaryConflict=any(c['savedBeforeHeightOrdinaryConflict']for c in columns)))
   records.append(dict(savedActualSampleVerbatim=sample,worlds=modes))
  rows.append(dict(uid=actor['uid'],exactGuardBoundary=actor['boundary'],completeFailedSites=len(actor['failedSampleIDs']),analyzedSites=len(records),samples=records,
   minimumHeightConflictingSites=[r['savedActualSampleVerbatim']['sample']for r in records if any(m['minimumAcceptedGuardHeightOrdinaryConflict']for m in r['worlds'])],
   savedBeforeHeightConflictingSites=[r['savedActualSampleVerbatim']['sample']for r in records if any(m['savedBeforeHeightOrdinaryConflict']for m in r['worlds'])]))
  print(json.dumps(dict(uid=actor['uid'],analyzed=len(records),minimumHeightConflicts=len(rows[-1]['minimumHeightConflictingSites']),beforeHeightConflicts=len(rows[-1]['savedBeforeHeightConflictingSites']))),flush=True)
 for q in inputs:assert ref(ROOT/q['path'])==q
 save(output,dict(rows=rows,inputRefs=inputs,actualBinary64Boundaries=ref(boundary),mode='bounded-preview'if preview else'complete-saved-failed-sites',
  analyzedSourceWorlds=4,completeOwnedSourceFacesPerWorld=10536,elapsedSeconds=time.monotonic()-start,noDBLeaseOrJob=True,
  noTerrainConstructorOrChangedSource=True,noContinuousRegionCoverageOrCurrentAcceptance=True,sourceEpochHistoricalC00=True,
  completeOwnedNative59527AndBASICQualificationStillRequired=True))
 print(json.dumps(dict(output=ref(output),complete=not preview)),flush=True)
if __name__=='__main__':main()
