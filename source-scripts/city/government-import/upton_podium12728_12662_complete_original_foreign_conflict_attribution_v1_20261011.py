"""DRAFT exact finite originals versus saved foreign GIS overlap; no credit."""
from pathlib import Path
from collections import Counter
import importlib.util,json,subprocess,sys,uuid
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,cross,sub,dot
from exact_original_component_contacts_20261009 import contact_measure
from science_museum_original_open_sided_contact_topology_attribution_v1_20261011 import relative_interior
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-podium12728-12662-complete-original-foreign-conflict-attribution-v1-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/12728:0','landsd/12662:0'];PROTECTED=UIDS+['landsd/338946:0'];MANIFEST_SHA='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
INPUT=B/'government-xl-upton-podium12728-12662-original-foreign-conflict-proposal-v1-20261011/source-inputs.json';CURRENT=B/'government-xl-upton338946-podium12728-current-unchanged-owned-identity-v1-20261011'
EXPECTED={UIDS[0]:('B321781649302063C0','3217816493P20150615','4f177100defad797c23530d4577676041bcbc6f6ee79de026f2af01c112552d2',1655,'de9d2b8aac972078d0e5855f729db40d76f290bca57f88036a80024eef9be0f0'),UIDS[1]:('B321351649702063C0','3213516497P20060312','de06028267854749aac25761395c83ccdd4b56c4813c23d14bdfd72a8598e5f0',392,'7fe91a56a2d841c4587f58fed96e86bc29c9ce089c590030101c11f4b0024622')}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(PROTECTED,)).fetchall()
def native():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members membership USING(cache_key), LATERAL jsonb_array_elements(r.result->'models')m WHERE membership.run_id=%s AND m->>'modelId'=ANY(%s) ORDER BY m->>'modelId'",(NATIVE_RUN,[v[0]for v in EXPECTED.values()])).fetchall()
def main():
 if '--owned'not in sys.argv:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('upton-original-foreign-attribution-'+str(uuid.uuid4()),['building:'+u for u in PROTECTED],batch=BATCH,ttl=1800);assert claim['ok'],claim;save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  code=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT).returncode;assert code==0,code;return
 assert not DOC.exists();lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);before=state();manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==MANIFEST_SHA
 current=read(CURRENT/'result.json');assert current['jobId']=='e096e5afb8b1c90b82ef689b65f292a9f9609dc33066f7943581d196926af2db'and current['manifestSHA256']==MANIFEST_SHA and not current['physicalAccepted']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(current['jobId'],)).fetchone()==('complete',current)
 for e in current['evidenceRefs']:assert ref(ROOT/e['path'])==e
 prior=next(r for r in current['identityOutcomes']if r['uid']==UIDS[0]);assert not prior['rawStrictPassed']and not prior['ownedPassed']and 'full-source-unrelated-overlap'in prior['rawReasons']
 forms=read(CURRENT/'complete-current-forms.json.gz')['rows'];foreign=[f for f in forms if f['uid']==UIDS[1]];assert len(foreign)==1 and foreign[0]['buildingCSUID']==EXPECTED[UIDS[1]][1];foreign_shape=Polygon(foreign[0]['rings'][0],foreign[0]['rings'][1:]);assert foreign_shape.is_valid and foreign_shape.area>0
 data=read(INPUT);sources={r['uid']:r for r in data['sources']};assert set(sources)==set(UIDS);refs=[ref(p)for p in [Path(__file__),INPUT,CURRENT/'result.json',CURRENT/'complete-current-forms.json.gz',CURRENT/'identities.json',manifest]]+data['evidenceRefs'];native_before=native();assert len(native_before)==2
 tri={};cs={};labels={};projection={}
 for uid,r in sources.items():
  model,csuid,sha,count,world=EXPECTED[uid];assert r['modelId']==model and r['source']['building']['buildingCSUID']==csuid and r['sourceSHA256']==sha
  matches=[x for x in native_before if x[1]['modelId']==model];assert len(matches)==1 and matches[0]==(r['native']['cacheKey'],r['native']['model'],r['native']['sheet'],r['native']['resultSha'])
  p=ROOT/r['candidate']['path'];assert ref(p)['sha256']==sha;refs.append(ref(p));tri[uid]=decode_original_world_triangles(p.read_bytes());assert tri[uid].shape==(count,3,3)and np.isfinite(tri[uid]).all()and digest(tri[uid].astype('<f8').tobytes())==world
  cs[uid]=census(tri[uid],list(range(count)));assert cs[uid]['completeWorldTrianglesSHA256']==world;labels[uid]={f:b for b,fs in enumerate(cs[uid]['sharedEdgeConnectedComponents'])for f in fs};zero=cs[uid]['exactNonrenderingOriginalFaces'];assert len(labels[uid])+len(zero)==count and set(labels[uid])|set(zero)==set(range(count))and not(set(labels[uid])&set(zero))
  projection[uid]=shapely.union_all(shapely.polygons(tri[uid][:,:,[0,2]]));assert projection[uid].is_valid
 a,z=(tri[u]for u in UIDS);al,ah=a.min(1),a.max(1);zl,zh=z.min(1),z.max(1);valid=np.array(sorted(labels[UIDS[1]]),dtype=int);cache={};contacts=[];tested=0;complete=0
 def face(uid,i):
  key=(uid,i)
  if key not in cache:cache[key]=rational_face(tri[uid][i])
  return cache[key]
 for i in sorted(labels[UIDS[0]]):
  complete+=len(valid);js=valid[np.all(zh[valid]>=al[i],axis=1)&np.all(ah[i]>=zl[valid],axis=1)]
  for j0 in js:
   j=int(j0);tested+=1;assert tested<=250000,'Resource bound; incomplete inventory cannot qualify';x,y=face(UIDS[0],i),face(UIDS[1],j);points=sorted(intersection_points(x,y))
   if not points:continue
   measure=contact_measure(points);nx=cross(sub(x[1],x[0]),sub(x[2],x[0]));ny=cross(sub(y[1],y[0]),sub(y[2],y[0]));cop=not any(cross(nx,ny))and all(dot(nx,sub(v,x[0]))==0 for v in y);mid=tuple(sum(v[k]for v in points)/len(points)for k in range(3))
   contacts.append(dict(original12728Face=i,original12662Face=j,body12728=labels[UIDS[0]][i],body12662=labels[UIDS[1]][j],coplanar=cop,bothRelativeInteriorCrossing=not cop and measure['dimension']>0 and relative_interior(x,mid)and relative_interior(y,mid),exactContactYRange=[str(min(v[1]for v in points)),str(max(v[1]for v in points))],**measure))
  if i%128==0:assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(sourceFace=i,exactPairs=tested,contacts=len(contacts))),flush=True)
 assert complete==len(labels[UIDS[0]])*len(labels[UIDS[1]])
 descriptive=[]
 for i,t in enumerate(a):
  polygon=Polygon(t[:,[0,2]])
  if polygon.is_valid and polygon.area>0:
   area=polygon.intersection(foreign_shape).area
   if area>0:descriptive.append(dict(originalFace=i,originalBody=labels[UIDS[0]].get(i),projectedIntersectionAreaM2=area,sourceYRange=[float(t[:,1].min()),float(t[:,1].max())]))
 overlap=projection[UIDS[0]].intersection(foreign_shape);original_overlap=projection[UIDS[0]].intersection(projection[UIDS[1]])
 summary=dict(wholeFacePairDomain=len(a)*len(z),nonzeroFacePairDomain=complete,zeroFacePairExcluded=len(a)*len(z)-complete,completeInclusive3DAABBPairsTested=tested,exactFiniteContactCount=len(contacts),dimensions=dict(Counter(r['dimension']for r in contacts)),properRelativeInteriorCrossings=sum(r['bothRelativeInteriorCrossing']for r in contacts),completeCurrentForeignGISProjectedOverlapM2=overlap.area,completeOriginalForeignProjectedOverlapM2=original_overlap.area,originalForeignProjectionCoversCurrentGISOverlap=projection[UIDS[1]].covers(overlap),currentGISOverlapOutsideOriginalForeignProjectionM2=overlap.difference(projection[UIDS[1]]).area,descriptiveNonadditiveIntersecting12728Facets=len(descriptive))
 spec=importlib.util.spec_from_file_location('reviewed_source_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);paths=set();f.local_imports(Path(__file__),paths);refs +=[ref(p)for p in sorted(paths)]
 for e in refs+current['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert ref(manifest)['sha256']==MANIFEST_SHA and native()==native_before and state()==before and reservations.owns(lease)
 out=dict(sourceOnly=True,identityAccepted=False,physicalAccepted=False,currentAcceptance=False,supportRootCredit=False,sourceGeometryChanges=0,meshCreated=False,manifestSHA256=MANIFEST_SHA,sourceTuples=EXPECTED,completeOriginalCensuses=cs,summary=summary,allExactFiniteOriginalContacts=contacts,completeDescriptiveNonadditive12728FacetGISIntersections=descriptive,projectedOverlapGeometry=shapely.to_geojson(overlap),originalProjectedOverlapGeometry=shapely.to_geojson(original_overlap),rawCurrentIdentityNegative=prior,completeNativeSourceMembershipBeforeAfter=native_before,protectedReviewRowsBeforeAfter=before,evidenceRefs=refs,qualification='Complete unchanged original finite surface attribution, not solid-clearance/ownership/architecture/support or identity acceptance. Per-facet projected areas are nonadditive descriptive context only; point/proper crossings remain unqualified. All737 tower bodies and both raw podium foreign-identity failures retained.')
 save(DOC/'diagnostic.json.gz',out);paths.update(ROOT/e['path']for e in refs);result=f.F.freeze(BATCH,'complete-original-foreign-conflict-attribution-no-identity-or-support-credit',sorted(paths),dict(uids=PROTECTED,sourceOnly=True,identityAccepted=False,physicalAccepted=False,manifestSHA256=MANIFEST_SHA,summary=summary))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert state()==before;print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),summary=summary)),flush=True)
if __name__=='__main__':main()
