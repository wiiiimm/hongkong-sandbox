"""Exact original far-face accounting and independent cartographic correspondence.
This produces a reviewable source role proposal, not identity/physical approval.
"""
import sys,json,importlib.util,uuid
import numpy as np
import shapely
from shapely.geometry import shape,Point,Polygon,box
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest,connect,reservations
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
BATCH='government-xl-two-harbourfront-primary-owner-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PACKET=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-118230-original-components'
INPUT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-118230-current-inputs'
SHA='0e9740f9b9b3061aa4f4bbe26b397db58f870476aa0716745339e505a79c51ff'
MODEL='B378291822401063C0';UID='landsd/118230:0'

def mod(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
 assert not (DOC/'attached-original-road-margin-diagnostic.json.gz').exists()
 selection=read(INPUT/'check-selection.json.gz');row=next(r for r in selection['rows'] if r['uid']==UID);row={**row,'sourceKey':row['native']['cacheKey']+'/'+MODEL}
 primaryURL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
 params={'f':'json','where':"BuildingCSUID='3782918224T20050430'",'outFields':'*','returnGeometry':'true','outSR':2326}
 primaryPath=DOC/'current-unique-primary-record.json'
 if primaryPath.exists():
  raw=primaryPath.read_bytes();receipt=read(DOC/'current-unique-primary-record.request.json');assert receipt['url']==primaryURL and receipt['parameters']==params and digest(raw)==receipt['sha256']
 else:
  raw,receipt=request(primaryURL,params);primaryPath.write_bytes(raw);save(DOC/'current-unique-primary-record.request.json',receipt)
 primary=json.loads(raw);assert len(primary['features'])==1;feature=primary['features'][0];attrs=feature['attributes'];assert attrs['BuildingCSUID']=='3782918224T20050430' and attrs['BuildingID']==1108242698 and attrs['BuildingBlockType']=='Tower' and attrs['Status']=='Active'
 claim=reservations.claim('harbourfront-road-margin-'+str(uuid.uuid4()),['native-model:'+row['sourceKey']],batch=BATCH,ttl=900);assert claim['ok'],claim;lease=claim['reservation']
 try:
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');native=c.execute("SELECT m FROM astra_modelling.native_stage_results,LATERAL jsonb_array_elements(result->'models') m WHERE cache_key=%s AND m->>'modelId'=%s",(row['sourceKey'].split('/')[0],MODEL)).fetchone()[0]
  assert native['asset']['sha256']==SHA
  asset=next(p for p in (HERE/'local').rglob(SHA+'.glb.gz') if p.parent.name=='assets');assert digest(asset.read_bytes())==SHA
  decoder=mod('harbourfront_exact_original_decoder','xl-second-pass.py');decoder.LOCAL=asset.parent.parent;tri=decoder.glb_triangles({'sourceSHA256':SHA,'modelId':MODEL,'triangles':native['triangles'],'native':{'model':native}});assert len(tri)==19438
  packet=read(PACKET/'far-original-source-faces.json');target=packet['completeTargetForm'];currentPath=ROOT/'3d-viewer/city/data/tiles/1_-1.json';current=next(b for b in read(currentPath)['buildings'] if b['uid']==UID);assert current==target
  own=Polygon(current['rings'][0],current['rings'][1:]);dist=shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),own).reshape(-1,3);ids=np.flatnonzero(dist.max(axis=1)>=10).tolist();assert ids==[r['sourceFace'] for r in packet['faces']]
  comps=read(PACKET/'diagnostic.json.gz')['components'];matches=[i for i,c in enumerate(comps) if set(ids)<=set(c['originalFaces'])];assert matches==[22]
  vectors=read(DOC/'decoded-original-local-feature-geometries.json.gz');roadrows=[r for r in vectors['rows'] if r['layer']=='9_CartoTransLine_1K' and r['properties']['_symbol']==10];assert roadrows;road=unary_union([shape(r['geometry']) for r in roadrows]);styles=read(DOC/'basemap-style.json')['layers'];roadstyles=[s for s in styles if s.get('source-layer')=='9_CartoTransLine_1K' and s.get('filter')==['==','_symbol',10]];assert all('/RM, E' in s['id'] for s in roadstyles) and roadstyles
  faces=[]
  for i in ids:
   p=tri[i];faces.append({'sourceFace':i,'originalVertices':p.tolist(),'maximumOriginalTargetExtentM':float(dist[i].max()),'maxVertexRoadMarginDistanceM':max(Point(v[0],v[2]).distance(road) for v in p),'minHKPD':float(p[:,1].min()),'maxHKPD':float(p[:,1].max()),'projectedTriangleAreaM2':float(Polygon(p[:,[0,2]]).area)})
  pts=tri[ids][:,:,[0,2]].reshape(-1,2);lo=pts.min(axis=0)-5;hi=pts.max(axis=0)+5;clip=box(lo[0],lo[1],hi[0],hi[1]);fig,ax=plt.subplots(figsize=(12,9),layout='constrained')
  for r in vectors['rows']:
   if '1K' not in r['layer']:continue
   geom=shape(r['geometry']).intersection(clip);geoms=list(geom.geoms) if hasattr(geom,'geoms') else [geom]
   for g in geoms:
    if g.geom_type=='Polygon':x,y=g.exterior.xy;ax.plot(x,y,color='grey',lw=.7)
    elif g.geom_type=='LineString':x,y=g.xy;ax.plot(x,y,color=('blue' if r in roadrows else 'grey'),lw=(2 if r in roadrows else .7))
  for i in ids:
   v=tri[i][:,[0,2]];ax.plot(*np.vstack([v,v[0]]).T,color='red',lw=1)
  g=own.intersection(clip)
  if not g.is_empty:
   for q in list(g.geoms) if hasattr(g,'geoms') else [g]:
    if q.geom_type=='Polygon':ax.plot(*q.exterior.xy,color='black',lw=2)
  ax.set(xlim=(lo[0],hi[0]),ylim=(hi[1],lo[1]),xlabel='Viewer X = HK80 E − 834500 (m)',ylabel='Viewer Z = 816500 − HK80 N (m)',title='Two Harbourfront: all ten original ≥10 m faces (red), independent road margin (blue)\nCurrent tower footprint boundary (black); no geometry fit or edits')
  ax.set_aspect('equal');ax.grid(alpha=.2);fig.savefig(DOC/'all-original-far-faces-independent-road-margin-2400x1800.png',dpi=200);plt.close(fig)
  save(DOC/'attached-original-road-margin-diagnostic.json.gz',{'uid':UID,'modelId':MODEL,'sourceKey':row['sourceKey'],'sourceSHA256':SHA,'worldTrianglesSHA256':digest(tri.astype('<f8').tobytes()),'nativeSourceMetadata':native,'originalPath':str(asset.relative_to(ROOT)),'completeOriginalFaces':len(tri),'allFarFaceIds':ids,'sourceConnectedMainComponent':22,'completeConnectedComponentFaceIds':comps[22]['originalFaces'],'componentBounds':comps[22]['bounds'],'everyFarFaceBelongsToMainBody':True,'farFaces':faces,'roadMarginStyle':roadstyles,'roadMarginRows':roadrows,'cartographicQuantizationStepM':sorted({r['quantizationStepM'] for r in roadrows}),'maxFarOriginalVertexRoadMarginDistanceM':max(r['maxVertexRoadMarginDistanceM'] for r in faces),'currentPrimaryAttributes':attrs,'currentTargetForm':current,'currentTargetTileSHA256':digest(currentPath.read_bytes()),'primaryURL':primaryURL,'sourceGeometryChanges':0,'identityAccepted':False,'physicalAccepted':False,'installationApproved':False,'qualification':'Every far original face belongs to the exact original connected main body and lies near the independently mapped road-margin line. This is descriptive cartographic correspondence, not a surveyed wall position, property boundary, or foundation/support proof. Source-authored street-front boundary interpretation requires review; full physical/current foreign/runtime checks remain independent. No general 10m extent waiver or geometry omission.'})
  print(json.dumps({'farFaces':len(ids),'allAttachedMainBody':True,'maxIndependentRoadMarginDistanceM':max(r['maxVertexRoadMarginDistanceM'] for r in faces),'identityAccepted':False}),flush=True)
 finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
