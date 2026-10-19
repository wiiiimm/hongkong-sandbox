"""Side views of exact flagged original source faces; no source edits."""
from pathlib import Path
import subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sheung-shui-isolated-groups-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-sheung-shui-whole-components-v1-20261020'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 selection=BASE/'government-xl-next-twenty-current-terrain-v2-20261020/selection.json.gz';assert str(selection.relative_to(ROOT))in pins
 row=next(r for r in read(selection)['rows']if r['uid']=='landsd/56054:0');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
 tri=decode_original_world_triangles(asset.read_bytes());context=read(BASE/'government-xl-sheung-shui-original-grade-context-v1-20261020/56054:0-original.json.gz');ids=context['continuousNegativeFaceIds'];flagged=tri[ids].tolist()
 groundpath=HERE/'local/government-xl-sheung-shui-adjoining-ground-v1-20261020/56054:0-ground.json.gz';assert str(groundpath.relative_to(ROOT))in pins
 ground=np.asarray(read(groundpath)['completeAdjoiningTerrain'],float);flag=np.asarray(flagged);lo=flag.min((0,1));hi=flag.max((0,1));lo-=np.array([8,2,8]);hi+=np.array([8,4,8])
 selected=ground[(ground[:,:,0].max(1)>=lo[0])&(ground[:,:,0].min(1)<=hi[0])&(ground[:,:,2].max(1)>=lo[2])&(ground[:,:,2].min(1)<=hi[2])];assert len(selected)>0
 save(DOC/'close-context.json',dict(flaggedSourceFaceIds=ids,reviewFrame=[lo.tolist(),hi.tolist()],originalTerrainFaces=len(selected),sourceOnly=True,installationApproved=False))
 models=[];groups=read(SRC/'groups.json')['groups'];assert sum(len(g['flaggedSourceFaceIds'])for g in groups)==68
 for index,g in enumerate(groups):
  part=tri[g['sourceFaceIds']];lo=part.min((0,1))-np.array([1.5,1,1.5]);hi=part.max((0,1))+np.array([1.5,1,1.5])
  selected=ground[(ground[:,:,0].max(1)>=lo[0])&(ground[:,:,0].min(1)<=hi[0])&(ground[:,:,2].max(1)>=lo[2])&(ground[:,:,2].min(1)<=hi[2])]
  view=dict(sourceUid=row['uid'],assetPath=str(asset.relative_to(ROOT)),sourceSHA256=row['sourceSHA256'],worldBounds=row['candidate']['entry']['worldBounds'],triangles=len(tri),forms=[],reviewFrame=[lo.tolist(),hi.tolist()],viewDirection=[-1,.8,.7],failedSamples=[],isolatedTriangles=part.tolist(),flaggedTriangles=tri[g['flaggedSourceFaceIds']].tolist())
  for terrain in [True]:models.append(dict(view,uid='review/group-'+str(index+1)+('-terrain'if terrain else'-source'),originalTerrain=selected.tolist()if terrain else[]))
 save(DOC/'input.json',dict(models=models,inputHashes=pins));tool=HERE/'sheung_shui_isolated_groups_v1_20261020.mjs';subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);report=read(DOC/'render.json');assert len(report['views'])==10 and not report['errors'];refs=[Path(__file__),tool,SRC/'result.json']
 for p,h in {**pins,**report['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('library_grade_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'harbourfront-exact-original-source-crossing-views',list(dict.fromkeys(refs)),dict(uids=['landsd/56054:0'],views=10,installationApproved=False))
if __name__=='__main__':main()
