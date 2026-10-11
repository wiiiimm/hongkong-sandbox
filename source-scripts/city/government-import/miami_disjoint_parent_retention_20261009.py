"""Bounded exact parent preservation for eight whole-source-disjoint forms."""
import json,importlib.util,numpy as np,shapely
from run import ROOT,HERE,read,digest
UIDS={'landsd/6522:0','landsd/6523:0','landsd/200383:0','landsd/202031:0','landsd/203406:0','landsd/203417:0','landsd/203844:0','landsd/204219:0'}
CAUSE=ROOT/'docs/astra-city/government-import/government-xl-miami-neighbour-source-overlap-20261009/whole-source-neighbour-cause-and-elevated-census.json.gz'
INPUT=ROOT/'docs/astra-city/government-import/government-xl-miami-nine-original-contact-20261009/all-original-source-contact-inputs.json.gz'

def preserve(patch,bounds,sampler,projection,current_forms,patches):
 """Retain whole current footprints only after complete original disjointness."""
 cause=read(CAUSE);source=read(INPUT);polygons=[]
 selection=read(ROOT/'docs/astra-city/government-import/government-xl-miami-nine-independent-original-diagnostic-20261009/selection.json.gz')
 spec=importlib.util.spec_from_file_location('miami_retention_original_decode',HERE/'xl-second-pass.py');decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder);decoder.LOCAL=HERE/'local/government-xl-miami-nine-original-source-foundation-20261009'
 for r in source['rows']:
  original=next(x for x in selection['rows'] if x['uid']==r['uid']);assert digest((ROOT/original['candidate']['path']).read_bytes())==r['sourceSHA256']==original['sourceSHA256'];original['triangles']=original['native']['model']['triangles'];t=decoder.glb_triangles(original);assert digest(t.astype('<f8').tobytes())==r['worldTriangleSHA256'];assert np.array_equal(t,np.asarray(r['position'],float).reshape(-1,3,3));polygons.append(shapely.union_all(shapely.polygons(t[:,:,[0,2]])))
 nine=shapely.union_all(polygons);current={b['uid']:b for b,_,_ in current_forms};rows=[];protected=[]
 for uid in sorted(UIDS):
  old=next(r for r in cause['rows'] if r['uid']==uid);assert old['wholeFiveSourceOverlapM2']==old['wholeNineSourceOverlapM2']==0 and old['wholeFiveSourceDistanceM']>0;assert current[uid]==old['currentForm'];b=current[uid];shape=shapely.Polygon(b['rings'][0],b['rings'][1:]);full=shape.buffer(.01,join_style='mitre');assert full.intersection(nine).area==0 and full.distance(nine)>0 and full.intersection(projection).area==0;protected.append(full);rows.append({'uid':uid,'wholeCurrentForm':b,'protectedRegionGeoJSON':json.loads(shapely.to_geojson(full)),'wholeNineSourceOverlapM2':0,'wholeNineSourceDistanceM':float(full.distance(nine))})
 region=shapely.union_all(protected);proof=patches.preserve_parent_under_projection(patch,bounds,region,sampler);proof.update(rows=rows,sourceProjectionIntersectionM2=0,allNineSourceProjectionIntersectionM2=0,allCurrentFormsRetained=True,sourceGeometryChanges=0,inputHashes={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [CAUSE,INPUT]});return proof
