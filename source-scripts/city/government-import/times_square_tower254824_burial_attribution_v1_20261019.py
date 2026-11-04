"""Attribute compound burial to existing authored podium surfaces, not terrain."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-times-square-tower254824-burial-attribution-v1-20261019';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-times-square-four-mode-foundations-v1-20261019';PAIR=BASE/'government-xl-times-square-original-assembly-v1-20261018';ATTR=BASE/'government-xl-times-square-actual-render-attributes-v1-20261019';UID='landsd/254824:0';POD='landsd/233901:0'
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows={r['uid']:r for r in read(PAIR/'selection.json.gz')['rows']};capture={r['uid']:r for r in read(ATTR/'attributes.json.gz')['rows']};runtime=read(HERE/'local'/PAIR.name/'runtime-geometry.json.gz')['rows'];ground=np.unique(np.concatenate([np.asarray(r['drawnGroundGeometry']).reshape(-1,9)for r in runtime]),axis=0).reshape(-1,3,3);final=module('pacifica_burial_attribution',HERE/'xl-final-script-pass.py');out=[]
 for mode,field in [('original',None),('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  def world(uid):
   if field is None:return decode_original_world_triangles((ROOT/rows[uid]['candidate']['path']).read_bytes())
   r=capture[uid];return np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]
  tri=world(UID);pod=world(POD);prior=read(PRIOR/(UID.split('/')[1]+'-'+mode+'.json'));assert digest(tri.astype('<f8').tobytes())==prior['wholeWorldSHA256'];assert [f['faceId']for f in prior['buriedFaces']]==[1092];b=rows[UID]['source']['building'];f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));assert f['completeTerrainTriangles']==len(tri)and f['fullyBuriedTriangles']==0
  evidence=[]
  for i in [1092]:
   pts=np.concatenate([tri[i],tri[i].mean(0)[None,:]],axis=0);poly=shapely.polygons(pod[:,:,[0,2]]);valid=shapely.area(poly)>1e-10;ids=np.flatnonzero(valid);tree=shapely.STRtree(poly[valid]);hits=[]
   for point in pts:
    ix=tree.query(shapely.Point(point[0],point[2]),predicate='intersects');faces=pod[ids[ix]];samples=final.s.context.shared.samples(point[None,[0,2]],faces,shapely.STRtree(poly[ids[ix]])) if len(ix) else np.array([np.nan]);hits.append(dict(position=point.tolist(),candidatePodiumFaceIds=ids[ix].tolist(),highestPodiumY=float(samples[0])))
   evidence.append(dict(faceId=i,vertices=tri[i].tolist(),pointAttribution=hits))
  item=dict(uid=UID,mode=mode,terrainOnlyFoundation=f,compoundStrictFoundationPassed=False,rawCompoundFoundation=prior['foundation'],exactFaces=evidence,interpretation='The strict compound-burial face is above drawn terrain; the negative compound clearance comes from higher original podium surfaces at its projected coordinates. This attribution alone does not resolve source overlap, visual acceptance or collision requirements.',installationApproved=False);save(DOC/(mode+'.json'),item);out.append(dict(mode=mode,terrainOnlyBuried=0,compoundBuried=1));print(out[-1],flush=True)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py']);module('pacifica_attribution_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-compound-versus-terrain-burial',list(dict.fromkeys(refs)),dict(uids=[UID,POD],rows=out,installationApproved=False))
if __name__=='__main__':main()
