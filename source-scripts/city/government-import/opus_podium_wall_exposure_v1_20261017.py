"""Refine exposure using all equal-height original vertices, preserving prior proof."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from original_bound_facet_wall_context_v2_20261010 import exposure_at_vertex
from original_coplanar_exterior_continuation_20261009 import diagnose
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-opus-podium-finite-walls-v1-20261017';WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017';GROUND=BASE/'government-xl-opus-preserved-neighbours-v1-20261016';BATCH='government-xl-opus-podium-wall-exposure-v1-20261017';DOC=BASE/BATCH;UID='landsd/248432:0'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={x['path']:x['sha256'] for x in r['evidenceRefs']};refs=[Path(__file__),PRIOR/'result.json']
 def consume(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 worlds=consume(WORLD/'world-triangles.json.gz');tri=np.array(worlds['original'][UID]);assert all(np.array_equal(tri,w[UID]) for w in worlds.values());d=consume(PRIOR/'original.json.gz');ctx=d['contexts'];gpath=HERE/'local'/GROUND.name/'runtime-geometry.json.gz';ground=np.concatenate([np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3) for g in consume(gpath)['rows']]);refinements=[]
 for c in ctx:
  if not c['groundProjectionCovered'] or c['minimum']['minimumGapM']>=-.5 or c['maximumObservedGapM']>0:continue
  t=tri[c['sourceFace']];ids=np.flatnonzero(t[:,1]==t[:,1].max());proofs=[dict(vertexIndex=int(i),proof=exposure_at_vertex(t[i],ground)) for i in ids];best=max(proofs,key=lambda x:x['proof']['maximumObservedGapM']);assert best['proof']['maximumObservedGapM']>=c['maximumObservedGapM'];refinements.append(dict(sourceFace=c['sourceFace'],priorExposure=c['maximumObservedGapM'],equalHighestVertexProofs=proofs,selectedVertex=best['vertexIndex']));c['priorExposureVerbatim']=dict(maximumObservedGapM=c['maximumObservedGapM'],exactVertexExposure=c['exactVertexExposure']);c.update(maximumObservedGapM=best['proof']['maximumObservedGapM'],exactVertexExposure=best['proof'])
 normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1);ratio=np.divide(normals[:,1],length,out=np.zeros_like(length),where=length>0);failed=[c['sourceFace'] for c in ctx if c['minimum']['minimumGapM']<-.5];steep=[i for i in failed if length[i]>0 and abs(ratio[i])<=.25];below=[i for i in steep if ctx[i]['maximumObservedGapM']<=0];continuation=diagnose(tri,ctx,below)
 summary=dict(ordinaryFailedFaces=len(failed),steepFailedFaces=len(steep),nonWallFailedFaces=[dict(faceIndex=i,normalY=float(ratio[i]),minimumGapM=ctx[i]['minimum']['minimumGapM']) for i in failed if i not in steep],unexposedWallFaces=below,continuation=continuation,fullAcceptance=False,newlyInstalled=0)
 DOC.mkdir();save(DOC/'contexts.json.gz',dict(contexts=ctx,refinements=refinements,qualification='Finite minimum certificates unchanged. Positive exposure is proved at an actual original highest vertex against every covering finite terrain facet. All tied highest vertices tested; no terrain/geometry modification.',**summary));save(DOC/'summary.json',summary)
 refs += [HERE/'original_bound_facet_wall_context_v2_20261010.py',HERE/'original_coplanar_exterior_continuation_20261009.py'];out=module('opus_exposure_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-equal-highest-vertex-wall-exposure-v1',refs,dict(uids=[UID],**summary));print(dict(jobId=out['jobId'],**summary),flush=True)
if __name__=='__main__':main()
