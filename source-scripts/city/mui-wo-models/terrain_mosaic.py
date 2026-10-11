"""Join source grid nodes before blending only the outer union into the archival DTM.
No invented terrain fill: null source samples retain the underlying DTM.
"""
import hashlib,json,pathlib
import numpy as np

def blend_sources(fine,E,N,paths,root):
 values=np.zeros(fine.shape);valid=np.zeros(fine.shape,dtype=bool);sources=[];grid_bounds=[]
 for path in paths:
  detail=json.loads(path.read_text());g=detail['meta']['georef'];dc=round((g['bE']-E)/5);dr=round((N-g['bN'])/5)
  assert g['aE']==5 and g['aN']==-5 and abs(E+dc*5-g['bE'])<.001 and abs(N-dr*5-g['bN'])<.001,path
  assert dc>=0 and dr>=0 and dc+detail['w']<=fine.shape[1] and dr+detail['h']<=fine.shape[0],path
  array=np.array([float('nan') if x is None else x for x in detail['elev']]).reshape(detail['h'],detail['w']);mask=np.isfinite(array)
  dest=values[dr:dr+detail['h'],dc:dc+detail['w']];prior=valid[dr:dr+detail['h'],dc:dc+detail['w']]
  assert not np.any(prior&mask),'Overlapping source grid ownership must be reviewed'
  dest[mask]=array[mask];prior|=mask
  grid_bounds.append((dr,dc,detail['h'],detail['w'],detail['source']['tile']))
  sources.append({'file':str(path.relative_to(root)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source':detail['source'],'policy':'Actual official 3D tile terrain sampled onto the shared 5 m grid; adjacent sources form one union. Only the exterior/holes have a 15 m blend into the archival DTM. Original source grids and model elevations remain unchanged; existing DTM nonpositive water nodes are retained.'})
 source_water_nodes=int((valid&(fine<=0)).sum())
 # The visualisation TIN also includes flat positive-HKPD water surfaces.
 # It has no land/water semantics; retain the existing official DTM water mask.
 valid&=fine>0
 # A boundary source node has alpha=0, next two rows 1/3,2/3, then 1.
 # Joining grids before erosion avoids artificial DTM grooves on internal seams.
 interior=valid.copy();weight=np.zeros(fine.shape)
 for _ in range(3):
  padded=np.pad(interior,1,constant_values=False)
  interior=interior&padded[:-2,1:-1]&padded[2:,1:-1]&padded[1:-1,:-2]&padded[1:-1,2:]
  weight+=interior/3
 fine[:]=np.where(valid,fine*(1-weight)+values*weight,fine)
 seams=[]
 for ar,ac,ah,aw,at in grid_bounds:
  for br,bc,bh,bw,bt in grid_bounds:
   if ac+aw==bc:
    lo=max(ar,br);hi=min(ar+ah,br+bh)
    if hi>lo:
     differences=np.abs(values[lo:hi,ac+aw-1]-values[lo:hi,bc]);seams.append({'tiles':[at,bt],'orientation':'east-west','samples':hi-lo,'medianAdjacent5mDifference':float(np.median(differences)),'maxAdjacent5mDifference':float(differences.max())})
   if ar+ah==br:
    lo=max(ac,bc);hi=min(ac+aw,bc+bw)
    if hi>lo:
     differences=np.abs(values[ar+ah-1,lo:hi]-values[br,lo:hi]);seams.append({'tiles':[at,bt],'orientation':'north-south','samples':hi-lo,'medianAdjacent5mDifference':float(np.median(differences)),'maxAdjacent5mDifference':float(differences.max())})
 return sources,{'sourceNodes':int(valid.sum()),'sourceNodesExcludedByExistingWaterMask':source_water_nodes,'fullSourceNodes':int((weight==1).sum()),'blendedSourceNodes':int((valid&(weight>0)&(weight<1)).sum()),'edgeDTMNodes':int((valid&(weight==0)).sum()),'seams':seams,'note':'Adjacent-grid height differences include real slope over 5 m and are not a measurement of same-position seam discontinuity.'}
