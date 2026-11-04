"""DRAFT bounded original face/boundary roles + primary/current2D context only."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import importlib.util,json,subprocess,sys,uuid,urllib.request,urllib.parse,datetime
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,cross,sub
from exact_shared_3d_segment_intervals_v1_20261011 import overlap,covered
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-podium-boundary23-exact-roles-official-context-v1-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
SOURCE=B/'government-xl-upton-podium12728-12662-original-foreign-conflict-proposal-v1-20261011/source-inputs.json';RAW=B/'government-xl-upton-podium12728-12662-complete-original-foreign-conflict-attribution-v1-20261011/diagnostic.json.gz';RECOVERY=B/'government-xl-upton-podium12728-12662-frozen-json-key-readback-recovery-v1-20261011/result.json';CURRENT=B/'government-xl-upton338946-podium12728-current-unchanged-owned-identity-v1-20261011'
UIDS=['landsd/12728:0','landsd/12662:0','landsd/338946:0'];MANIFEST_SHA='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6';LIMIT=8*1024*1024
PRIMARY={'tpb-site-plan':'https://www.tpb.gov.hk/sc/plan_application/Attachment/20220610/s17s16_A_H3_444_0_gist.pdf','emperor-upton-launch':'https://www.emperorgroup.com/en/media_centre/latest_news/2014-12-03/'}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(UIDS,)).fetchall()
def native(sources):
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');rows=c.execute("SELECT r.cache_key,m,i.sheet,r.result_sha,i.source_sha,i.input_json FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members membership USING(cache_key), LATERAL jsonb_array_elements(r.result->'models')m WHERE membership.run_id=%s AND m->>'modelId'=ANY(%s) ORDER BY m->>'modelId'",(NATIVE_RUN,[r['modelId']for r in sources])).fetchall()
 assert len(rows)==2
 for r in sources:
  match=[x for x in rows if x[1]['modelId']==r['modelId']];assert len(match)==1 and match[0][:4]==(r['native']['cacheKey'],r['native']['model'],r['native']['sheet'],r['native']['resultSha'])
 return rows

def fetch(url,parameters=None):
 full=url+('?' +urllib.parse.urlencode(parameters)if parameters else '');started=datetime.datetime.now(datetime.timezone.utc).isoformat();req=urllib.request.Request(full,headers={'User-Agent':'HongKongSandbox-Astra/bounded-source-boundary-context'})
 with urllib.request.urlopen(req,timeout=45)as response:
  raw=response.read(LIMIT+1);assert len(raw)<=LIMIT,'Bounded8MBresponse exceeded';headers=dict(response.headers.items());status=response.status
 return raw,dict(url=url,parameters=parameters or{},startedAtUTC=started,retrievedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=digest(raw),bytes=len(raw),status=status,responseHeaders=headers,TLSVerificationUnchanged=True)
def main():
 if '--owned'not in sys.argv:
  assert not (DOC/'diagnostic.json.gz').exists()and not LOCAL.exists();claim=reservations.claim('upton-boundary-source-context-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=1800);assert claim['ok'],claim;save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));code=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT).returncode;assert code==0,code;return
 assert not (DOC/'diagnostic.json.gz').exists();lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);before=state();manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==MANIFEST_SHA
 receipt=read(RECOVERY);current=read(CURRENT/'result.json')
 for r in [receipt,current]:
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 d=read(RAW);sources=read(SOURCE)['sources'];native_before=native(sources);contacts=d['allExactFiniteOriginalContacts'];assert len(contacts)==23 and all(x['bothRelativeInteriorCrossing']for x in contacts);tri={};boundaries={};edge_counts={};source_refs=[];code_pins=[ref(p)for p in [Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_shared_3d_segment_intervals_v1_20261011.py',HERE.parent/'landsd-territory/source.py',HERE.parent/'mui-wo-buildings/build.py',HERE.parent/'build_city.py']]
 for s in sources:
  uid=s['uid'];p=ROOT/s['candidate']['path'];assert ref(p)['sha256']==s['sourceSHA256'];source_refs.append(ref(p));tri[uid]=decode_original_world_triangles(p.read_bytes());assert digest(tri[uid].astype('<f8').tobytes())==d['sourceTuples'][uid][4]
  edges=Counter()
  for face in d['completeOriginalCensuses'][uid]['sharedEdgeConnectedComponents'][0]:
   t=rational_face(tri[uid][face]);edges.update(tuple(sorted((t[i],t[(i+1)%3])))for i in range(3))
  boundaries[uid]=[e for e,n in edges.items()if n==1];edge_counts[uid]=dict(completeMainBodyFaces=len(d['completeOriginalCensuses'][uid]['sharedEdgeConnectedComponents'][0]),wholeEdgeIncidenceHistogram={str(k):v for k,v in Counter(edges.values()).items()},wholeIndexedBoundaryEdges=len(boundaries[uid]),TjunctionConformityNotEstablished=True)
 rows=[]
 for record in contacts:
  points=[tuple(F(v)for v in p)for p in record['exactPoints']];a,b=points[0],points[-1];assert a!=b;roles=[]
  for uid,key in [('landsd/12728:0','original12728Face'),('landsd/12662:0','original12662Face')]:
   i=record[key];t=rational_face(tri[uid][i]);n=cross(sub(t[1],t[0]),sub(t[2],t[0]));assert any(n);role=('horizontal-up'if n[1]>0 else'horizontal-down')if n[0]==n[2]==0 else'vertical'if n[1]==0 else'oblique'
   incident=[overlap(a,b,t[k],t[(k+1)%3])for k in range(3)];boundary=[dict(edge=[[str(v)for v in p]for p in e],exactInterval=[str(x)for x in interval])for e in boundaries[uid]if(interval:=overlap(a,b,*e))is not None];intervals=[tuple(F(v)for v in x['exactInterval'])for x in boundary]
   roles.append(dict(uid=uid,originalFace=i,exactOrientedNormal=[str(v)for v in n],geometricPlaneRoleOnly=role,originalTriangle=[[str(v)for v in p]for p in t],wholeContactOnIncidentTriangleEdge=covered([x for x in incident if x]),wholeContactOnMainBodyIndexedBoundary=covered(intervals),positiveExactMainBodyBoundaryIntervals=boundary))
  rows.append(dict(originalContact=record,sourceFaceRoles=roles,authoredBoundarySeamQualified=False))
 # Two exact-CSUID official lookups, two actual readers each; no old-object identity transfer.
 sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import BASE
 outline=module('reviewed_official_outline_parser',HERE.parent/'mui-wo-buildings/build.py');forms=read(CURRENT/'complete-current-forms.json.gz')['rows'];official=[];errors=[]
 for s in sources:
  uid=s['uid'];csuid=s['source']['building']['buildingCSUID'];label=uid.split('/')[1].replace(':','-');reads=[]
  try:
   for reader in [1,2]:
    raw,meta=fetch(BASE+'/0/query',dict(f='json',where="BuildingCSUID='"+csuid+"'",outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='100'));obj=json.loads(raw);assert not obj.get('error')and isinstance(obj.get('features'),list)and not obj.get('exceededTransferLimit');reads.append(obj);p=DOC/(label+'-official-reader'+str(reader)+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);save(p.with_suffix('.request.json'),meta)
   assert reads[0]==reads[1],'Official outline changed between readers';records=[x for x in reads[0]['features']if x['attributes'].get('BuildingCSUID')==csuid];assert len(records)==1,'No unique exact stableCSUID official record';geo,repaired=outline.official_geometry(records[0]);assert not repaired and geo.is_valid and geo.area>0;old=next(f for f in forms if f['uid']==uid);old_shape=Polygon(old['rings'][0],old['rings'][1:]);official.append(dict(uid=uid,stableCSUID=csuid,activeAttributes=records[0]['attributes'],historicalViewerObjectID=old['objectId'],unroundedWorldGeometry=geo.__geo_interface__,currentViewerSymmetricDifferenceM2=geo.symmetric_difference(old_shape).area,sourceProjectionPoseChanged=False))
  except Exception as e:errors.append(dict(scope=uid,type=type(e).__name__,error=str(e),absenceOrIdentityNotEstablished=True))
  assert reservations.heartbeat(lease)['ok']
 primary=[]
 for label,url in PRIMARY.items():
  try:
   raws=[]
   for reader in [1,2]:
    raw,meta=fetch(url);raws.append(raw);p=DOC/(label+'-reader'+str(reader)+('.pdf'if label=='tpb-site-plan'else'.html'));p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);save(Path(str(p)+'.request.json'),meta)
   assert raws[0]==raws[1],'Primary resource changed between readers';record=dict(label=label,url=url,actualTwoReadersByteEqual=True,sourceOnly=True,architecturalUIDOrJointIntentNotEstablished=True)
   if label=='tpb-site-plan':
    import fitz
    pdf=fitz.open(stream=raws[0],filetype='pdf');assert len(pdf)==5;page=pdf[4];text=page.get_text();assert '11-SW-7A'in text and '30.5.2022'in text;png=DOC/'tpb-2022-page5-site-plan-original.png';pix=page.get_pixmap(matrix=fitz.Matrix(3,3));pix.save(str(png));record.update(page=5,unwarpedExport=ref(png),dimensions=[pix.width,pix.height],literalPageText=text,scope='Another application A/H3/444 identification-only site map; no measured sharedjoint/sourceUID/HKPDproof.')
   primary.append(record)
  except Exception as e:errors.append(dict(scope=label,type=type(e).__name__,error=str(e),absenceOrIdentityNotEstablished=True))
  assert reservations.heartbeat(lease)['ok']
 paths={Path(__file__),SOURCE,RAW,RECOVERY,CURRENT/'result.json',CURRENT/'complete-current-forms.json.gz',manifest,HERE.parent/'landsd-territory/source.py',HERE.parent/'mui-wo-buildings/build.py',HERE.parent/'build_city.py'}|{ROOT/e['path']for e in source_refs};f=module('reviewed_source_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');f.local_imports(Path(__file__),paths);input_refs=[ref(p)for p in sorted(paths)]
 for r in [receipt,current]:
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 for e in code_pins+source_refs:assert ref(ROOT/e['path'])==e
 assert ref(manifest)['sha256']==MANIFEST_SHA and state()==before and reservations.owns(lease)and native(sources)==native_before
 out=dict(sourceOnly=True,identityAccepted=False,physicalAccepted=False,originalContactMathReplayed=False,complete23ContactsRetained=rows,completeMainBodyWholeEdgeContext=edge_counts,completeNativeInputsBeforeAfter=native_before,sourceVersionDateInterpretationLiteralOnly=True,officialStableCSUIDContexts=official,primaryContexts=primary,errors=errors,priorGIS1_910445M2AndOriginal0_054498M2NegativesPreserved=True,sourcePoseAndHeightsUnchanged=True,evidenceRefs=input_refs,qualification='Exact incident-face geometric orientations and complete original-mainbody indexed-edge context only; no architecturalfunction/ownership/legal/engineeringjoint or foreign waiver. Nonedge propercrossings remain real. Official2D currentepoch/renumbering and independent primary identification-onlyplan are context, not full original source identity/support/runtime approval.')
 save(DOC/'diagnostic.json.gz',out);result=f.F.freeze(BATCH,'source-face-boundary-and-official-context-no-identity-or-seam-credit',sorted(paths),dict(uids=UIDS,sourceOnly=True,identityAccepted=False,physicalAccepted=False,completeOriginalContactsPreserved=23,officialContexts=len(official),primaryContexts=len(primary),errors=errors,manifestSHA256=MANIFEST_SHA))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert state()==before;print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),officialContexts=len(official),primaryContexts=len(primary),errors=errors)),flush=True)
if __name__=='__main__':main()
