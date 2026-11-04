"""Compare every failed original-library face with authentic government terrain."""
from pathlib import Path
import numpy as np,shapely,subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from exact_projection_coverage_fallback_context_20261009 import apply_exact_coverage
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-library-original-grade-comparison-v1-20261019';DOC=BASE/BATCH
GRADE=BASE/'government-xl-central-library-full-grade-context-v1-20261019';SRC=BASE/'government-xl-next-three-adjoining-ground-v1-20261019';CAP=BASE/'government-xl-central-library-private-ground-v1-20261019';ATTR=BASE/'government-xl-central-library-actual-render-attributes-v2-20261019';VIEWS=BASE/'government-xl-central-library-loader-identity-v1-20261019';UID='landsd/232240:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [GRADE,SRC,ATTR,VIEWS]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(CAP/'selection.json.gz')['rows'][0];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];worlds={'original':decode_original_world_triangles(raw)};a=read(ATTR/'attributes.json.gz')['rows'][0]
 for mode,field in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(a[field],dtype='<f8').reshape(-1,3)[np.asarray(a['completeOriginalIndex']).reshape(-1,3)]
 sourcepath=HERE/'local'/SRC.name/'232240:0-ground.json.gz';original=np.asarray(read(sourcepath)['completeAdjoiningTerrain']);lo,hi=worlds['original'].min((0,1)),worlds['original'].max((0,1));keep=(original[:,:,0].max(1)>=lo[0]-1)&(original[:,:,0].min(1)<=hi[0]+1)&(original[:,:,2].max(1)>=lo[2]-1)&(original[:,:,2].min(1)<=hi[2]+1);ground=original[keep];polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;ground,polygons=ground[valid],polygons[valid];tree=shapely.STRtree(polygons);summaries=[]
 for mode,tri in worlds.items():
  g=read(GRADE/('232240:0-'+mode+'.json.gz'));assert digest(tri.tobytes())==g['completeWorldSHA256'];details=[]
  for i in g['continuousNegativeFaceIds']:
   t=tri[i];normal=np.cross(t[1]-t[0],t[2]-t[0]);length=np.linalg.norm(normal);context=face_ground_context(t,ground,polygons,tree)if length else degenerate_ground_context(t,ground,polygons,tree);context=apply_exact_coverage(context,t,ground);candidate=g['faces'][i];details.append(dict(faceId=i,triangle=t.tolist(),normalYRatio=float(normal[1]/length)if length else None,originalTerrain=context,candidateTerrain=candidate,minimumGapDifferenceM=candidate['minimum']['minimumGapM']-context['minimum']['minimumGapM']))
  out=dict(uid=UID,mode=mode,sourceSHA256=row['sourceSHA256'],wholeWorldSHA256=g['completeWorldSHA256'],wholeSourceFaces=len(tri),failedFaces=len(details),allVertical=all(d['normalYRatio']==0 for d in details),allOriginalCovered=all(d['originalTerrain']['groundProjectionCovered']for d in details),allOriginalHaveExposedWitness=all(d['originalTerrain']['maximumObservedGapM']>0 for d in details),maximumMinimumGapDifferenceM=max(abs(d['minimumGapDifferenceM'])for d in details),originalMinimumGapM=min(d['originalTerrain']['minimum']['minimumGapM']for d in details),details=details,installationApproved=False)
  save(DOC/(mode+'.json.gz'),out);summaries.append({k:v for k,v in out.items()if k!='details'});print(summaries[-1],flush=True)
 save(DOC/'summary.json',dict(rows=summaries,installationApproved=False))
 originalGrade=read(GRADE/'232240:0-original.json.gz');ids=originalGrade['continuousNegativeFaceIds'];tri=worlds['original'];bad=tri[ids];lo,hi=bad.min((0,1)),bad.max((0,1));view=read(VIEWS/'input.json')['models'][0];models=[]
 for name,frame,direction in [('podium-grade',None,[-.7,.8,-1]),('grade-close',[list(lo-np.array([3,1,3])),list(hi+np.array([3,1,3]))],[-.7,.8,-1])]:models.append(dict(view,uid='review/'+name,originalComponents=[],reviewFrame=frame,viewDirection=direction,failedSamples=[dict(position=originalGrade['faces'][i]['minimum']['position'])for i in ids]))
 tool=HERE/'central_library_identity_views_v1_20261019.mjs';save(DOC/'input.json',dict(models=models,inputHashes={row['candidate']['path']:row['sourceSHA256']}));subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);report=read(DOC/'render.json');assert len(report['views'])==2 and not report['errors']
 for p,h in {**pins,**report['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([sourcepath,tool,HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_face_ground_crossing_v2_20261009.py',HERE/'original_degenerate_ground_context_20261009.py',HERE/'exact_projection_coverage_fallback_context_20261009.py'])
 module('library_grade_comparison_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'central-library-original-source-grade-comparison',list(dict.fromkeys(refs)),dict(uids=[UID],rows=summaries,installationApproved=False))
if __name__=='__main__':main()
