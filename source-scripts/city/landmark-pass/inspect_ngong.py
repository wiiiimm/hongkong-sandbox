"""Read-only component/terrain context for the landmark trial exceptions."""
import json,pathlib,sqlite3,sys,io,struct,zipfile
import numpy as np
from shapely.geometry import Polygon
from audit_existing import triangle_evidence
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(p.read_bytes())
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from prepare_model_sample import model_geometry
terrain=read(HERE/'terrain-ngong-ping.json');g=terrain['meta']['georef'];w=terrain['w'];h=terrain['h'];e=np.array([v if v is not None else max(1.2,terrain['elev'][i]) if terrain['elev'][i]>0 else -4 for i,v in enumerate(terrain['renderedElev'])]).reshape((h,w))
def ground(x,z):
 c=np.clip((x+834500-g['bE'])/g['aE'],0,w-1);r=np.clip((816500-z-g['bN'])/g['aN'],0,h-1);i=np.minimum(w-2,np.floor(c)).astype(int);j=np.minimum(h-2,np.floor(r)).astype(int);u=c-i;v=r-j;a=e[j,i];b=e[j,i+1];d=e[j+1,i];ee=e[j+1,i+1]
 return np.where(u+v<=1,a+(b-a)*u+(d-a)*v,ee+(d-ee)*(1-u)+(b-ee)*(1-v))
c=sqlite3.connect('file:'+str(HERE.parent/'building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
bs={b['uid']:dict(b) for b in c.execute('select * from buildings where active=1 and x between -26600 and -25800 and z between 3300 and 3800')}
def poly(b):
 r=json.loads(b['rings_json']);return Polygon(r[0],r[1:])
cats={m['uid']:m for m in read(HERE/'compact/catalogue.json')['models']};val={r['uid']:r for r in read(HERE/'compact/validation-fine.json')['results']};specs={m['id']:(p,m) for p in (HERE/'staged').glob('*/manifest.json') for m in read(p)['models']}
def native(uid):
 p,s=specs[cats[uid]['modelId']];path=p.parent/s['sourceEntry'];v,_=model_geometry(read(path),lambda u:(path.parent/u).read_bytes());return path,v
rows=[]
for uid,r in val.items():
 if not r['concerns'] and uid!='landsd/84455:0':continue
 b=bs[uid];path,v=native(uid);vertices=np.unique(v,axis=0);gv=ground(vertices[:,0],vertices[:,2]);delta=vertices[:,1]-gv;foot=poly(b);neighbours=[]
 for nid,n in bs.items():
  if nid==uid:continue
  shape=poly(n);distance=foot.distance(shape)
  if distance<10:neighbours.append({'uid':nid,'name':n['name'],'structureType':n['structure_type'],'distance':round(distance,3),'targetFootprintCoverage':round(shape.intersection(foot).area/foot.area,6),'sourceBaseTop':[n['source_base'],n['source_top']],'candidateModel':nid in cats})
 row={'uid':uid,'name':b['name'],'structureType':b['structure_type'],'sourceBaseTop':[b['source_base'],b['source_top']],'nativeBaseTop':[float(v[:,1].min()),float(v[:,1].max())],'validation':r,'nearbySourceParts':neighbours,'nativeVertexTerrainContext':{'uniqueVertices':len(vertices),'verticesMoreThan05mBelowRenderedTerrain':int((delta<-.5).sum()),'verticesMoreThan2mBelowRenderedTerrain':int((delta<-2).sum()),'verticesWithin025mTerrain':int((np.abs(delta)<=.25).sum()),'minimumClearanceMetres':float(delta.min()),'maximumClearanceMetres':float(delta.max()),'qualification':'Same diagonal as geo.js terrain sampler; vertex depths show partial intersections, not a complete foundation or roof clearance proof.'}}
 if uid=='landsd/238276:0':
  p,pv=native('landsd/238483:0');ev=triangle_evidence(p,pv,foot,b['source_base'],b['base'],b['height']);bottom=float(v[:,1].min());rays=ev['rays'];diff=[min(abs(y-bottom) for y in ray['surfaceHeightsHKPD']) for ray in rays if ray['surfaceHeightsHKPD']];row['podiumSupport']={'uid':'landsd/238483:0','nativeTriangleEvidence':ev,'hallBottomHKPD':bottom,'raysWithSurfaceWithin025mOfHallBottom':sum(d<=.25 for d in diff),'raysWithSurfaceWithin1mOfHallBottom':sum(d<=1 for d in diff),'raysWithPodiumSurface':len(diff),'closestSurfaceDifferenceRange':[min(diff),max(diff)]};row['interpretation']='Hall has source podium underneath, so its gap to bare terrain is expected. Inspect actual podium triangle support and perimeter contact; do not move tower down to bare ground.'
 elif uid=='landsd/211847:0':row['interpretation']='No neighbouring footprint within10m supports this pagoda. Native bottom462.416 exceeds surveyed base459 by3.416m and final terrain byabout3.2m. Genuine unsupported model base remains unresolved; hold or preserve fallback, do not shift source model silently.'
 elif uid=='landsd/84455:0':row['interpretation']='Model extends3.558m below surveyed base but has no terrain-validation flags. Native source may include lower steps/storey on slope; review image and local vertex depths rather than automatic rejection solely on global bottom.'
 else:row['interpretation']='Partial terrain intersection flag: compare local native-vertex depths and source component context. Global terrain maximum versus model minimum conflates opposite sides of slopes; does not by itself prove model misplacement.'
 rows.append(row)
# The Grand Hall is another tower on the same separately modelled podium.
grand=read(HERE/'compact-grandhall/catalogue.json')['models'][0];gb=bs[grand['uid']];gp,gv=native('landsd/238483:0');gfoot=poly(gb);gev=triangle_evidence(gp,gv,gfoot,gb['source_base'],gb['base'],gb['height']);gbottom=grand['worldBounds'][0][1];gd=[min(abs(y-gbottom) for y in ray['surfaceHeightsHKPD']) for ray in gev['rays'] if ray['surfaceHeightsHKPD']]
grand_support={'uid':grand['uid'],'name':gb['name'],'podiumUID':'landsd/238483:0','nativeBottomHKPD':gbottom,'surveyedBaseHKPD':gb['source_base'],'nativeTriangleEvidence':gev,'sampledRaysWithPodium':len(gd),'raysWithin025mOfNativeBottom':sum(d<=.25 for d in gd),'raysWithin1mOfNativeBottom':sum(d<=1 for d in gd),'closestSurfaceDifferenceRange':[min(gd),max(gd)] if gd else None,'interpretation':'Review source podium surface elevations beneath the tower before attributing a bare-ground gap to floating geometry; model heights remain unshifted.'}
# Count every explicitly requested source part, including the added Grand Hall.
targets=[dict(r,landmark=g['id']) for g in read(HERE.parent/'building-batch/tourist-trial.json')['landmarks'] for r in g['records']];targets.append({'uid':grand['uid'],'csuid':grand['buildingCSUID'],'name':grand['label'],'landmark':'po-lin','objectId':grand['objectId']})
assert len({t['uid'] for t in targets})==87
available={r['uid'] for r in read(HERE/'existing-audit.json')['rows'] if r['currentDetailed']}
for folder in ['compact','compact-existing','compact-grandhall']:available.update(m['uid'] for m in read(HERE/folder/'catalogue.json')['models'])
refs={t['csuid'][:10] for t in targets};entries={ref:[] for ref in refs};directories=[]
for path in sorted((HERE/'sources').glob('*/zip-directory.bin')):
 raw=path.read_bytes();end=raw.rfind(b'PK\x05\x06');eo=struct.unpack('<4s4H2LH',raw[end:end+22]);assert eo[1]==eo[2]==0 and eo[3]==eo[4];buf=bytearray(eo[6]+len(raw));buf[eo[6]:]=raw
 with zipfile.ZipFile(io.BytesIO(buf)) as z:names=z.namelist()
 assert len(names)==eo[4];directories.append({'path':str(path.relative_to(ROOT)),'completeEntries':len(names)})
 for name in names:
  if name.endswith('.gltf'):
   for ref in refs:
    if ref in name:entries[ref].append({'sheet':path.parent.name,'entry':name})
old={r['uid']:r for r in read(HERE/'existing-audit.json')['rows']};unmatched=[]
for t in targets:
 if t['uid'] in available:continue
 b=dict(c.execute('select * from buildings where uid=? and active=1',(t['uid'],)).fetchone());oldrow=old.get(t['uid']);entry=entries[t['csuid'][:10]] or (oldrow['sourceEntries'] if oldrow else [])
 unmatched.append({'uid':t['uid'],'objectId':t['objectId'],'csuid':t['csuid'],'landmark':t['landmark'],'name':b['name'],'structureType':b['structure_type'],'sourceBaseTop':[b['source_base'],b['source_top']],'exactSourceEntriesInCheckedDirectories':entry,'disposition':'exact-source-candidate-requires-review' if entry else 'no-separate-exact-reference-model-in-checked-source-revision','componentEvidence':oldrow.get('relatedModelOverlaps',[]) if oldrow else [],'qualification':'A missing standalone model entry does not remove this basic footprint or prove the entire landmark is absent.'})
ledger={'targets':len(targets),'sourceMatchedDetailedOrStaged':len({t['uid'] for t in targets}&available),'withoutStandaloneMatchedModel':len(unmatched),'unmatched':unmatched,'checkedNgongDirectories':directories,'qualification':'Source availability ledger; staged candidates include held placement exceptions, so68matched does not mean68published or reviewed.'}
report={'scope':'Ten Ngong Ping staged candidates held for contextual review','rows':rows,'grandHallPodiumSupport':grand_support,'sourceAccountedLedger':ledger,'omittedLandmark':{'uid':'landsd/238482:0','name':'Grand Hall of Ten Thousand Buddhas','csuid':'0857512995T20141029','reason':'Distinct name omitted from initial explicit Po Lin UID list. Basic source form exists; source acquisition was never requested.','exactSource':'9-SE-21B/BUILDING/B085751299501063C0/B085751299501063C0.gltf','nowStaged':'source-scripts/city/landmark-pass/compact-grandhall/catalogue.json','sourceMatch':'Exact identity, overlap1.0, centroid0.0519m','priority':'Include in this landmark pass; essential to recognisable monastery architecture.'},'visualReferences':['docs/astra-city/landmark-pass/candidate-browser/after/ngong-ping-landsd-238276-0-day.png','docs/astra-city/landmark-pass/candidate-browser/after/ngong-ping-landsd-211847-0-day.png'],'limits':['Read-only context, no published approval.','No altered model vertices, source heights, fallback suppression or terrain flattening.']};(HERE/'ngong-context.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([{k:r[k] for k in ['uid','nativeVertexTerrainContext']} for r in rows],indent=2));print(json.dumps({k:v for k,v in next(r for r in rows if r['uid']=='landsd/238276:0')['podiumSupport'].items() if k!='nativeTriangleEvidence'},indent=2))
