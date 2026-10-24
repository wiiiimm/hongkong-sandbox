"""Fresh complete Miami source and foreign provider outlines, no metadata edits."""
import sys,json,importlib.util,numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from government_georef_cell_identity import geographic_cell
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import BASE,request
BATCH='government-xl-miami-op-complete-family-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
assert not (DOC/'result.json').exists(),'Completed checkpoint immutable'
sel=read(DOC/'selection.json.gz');foreign=read(DOC.parent/'government-xl-miami-op-complete-pair-20261009/current-foreign-overlap-form.json')
csuids=[r['source']['building']['buildingCSUID'] for r in sel['rows']]+[foreign['buildingCSUID']]
params={'f':'json','where':'BuildingCSUID IN ('+','.join("'"+c+"'" for c in csuids)+')','outFields':'*','returnGeometry':'true','outSR':'2326','resultRecordCount':'1000'}
raw,receipt=request(BASE+'/0/query',params);data=json.loads(raw);assert len(data['features'])==9 and not data.get('exceededTransferLimit')
(DOC/'fresh-nine-exact-provider-outlines.json').write_bytes(raw);save(DOC/'fresh-nine-exact-provider-outlines.request.json',receipt)
polys={};records=[]
for f in data['features']:
 c=f['attributes']['BuildingCSUID'];rings=[[(p[0]-834500,816500-p[1]) for p in ring] for ring in f['geometry']['rings']];polys[c]=shapely.symmetric_difference_all([shapely.Polygon(r) for r in rings])
assert set(polys)==set(csuids)
spec=importlib.util.spec_from_file_location('miami_fresh_decode',HERE/'xl-second-pass.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d);d.LOCAL=HERE/'local'/BATCH;tri=[]
for r in sel['rows']:
 b=r['source']['building'];c=b['buildingCSUID'];r['triangles']=r['native']['model']['triangles'];t=d.glb_triangles(r);tri.append(t);p=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));g=polys[c];cell=geographic_cell(r['modelId'],c,b['structureType']);attrs=next(f['attributes'] for f in data['features'] if f['attributes']['BuildingCSUID']==c)
 records.append({'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'currentProviderAttributes':attrs,'viewerObjectId':b['objectId'],'currentProviderWorldGeometry':shapely.to_geojson(g),'sourceCoversWholeCell':bool(p.covers(cell)),'providerCoversWholeCell':bool(g.covers(cell)),'viewerCoversWholeCell':bool(shapely.Polygon(b['rings'][0],b['rings'][1:]).covers(cell)),'providerViewerHausdorffM':g.boundary.hausdorff_distance(shapely.Polygon(b['rings'][0],b['rings'][1:]).boundary)})
t=np.concatenate(tri);p=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));g=shapely.union_all([polys[c] for c in csuids[:-1]]);oldtarget=shapely.union_all([shapely.Polygon(r['source']['building']['rings'][0],r['source']['building']['rings'][1:]) for r in sel['rows']]);fg=polys[csuids[-1]]
out={'rows':records,'foreignCurrentProviderAttributes':next(f['attributes'] for f in data['features'] if f['attributes']['BuildingCSUID']==csuids[-1]),'foreignCurrentProviderWorldGeometry':shapely.to_geojson(fg),'freshCompleteTargetCoverage':p.intersection(g).area/g.area,'freshFullSourceMaximumExtentM':float(shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),g).max()),'freshSourceExcessForeignProviderOverlapM2':p.difference(g).intersection(fg).area,'viewerSourceExcessForeignProviderOverlapM2':p.difference(oldtarget).intersection(fg).area,'viewerSourceExcessForeignViewerOverlapM2':read(DOC/'foreign-podium-every-original-overlap-face.json.gz')['foreignExcessUnionM2'],'identityAccepted':False,'metadataChanges':0,'geometryChanges':0,'qualification':'Fresh outlines are independent revised evidence, not silently substituted into retained viewer checks. Every volatile object ID revision recorded against unique stable CSUID.'}
save(DOC/'fresh-complete-family-current-provider-measures.json.gz',out);print({k:v for k,v in out.items() if k not in ['rows','foreignCurrentProviderAttributes','foreignCurrentProviderWorldGeometry']},flush=True)
