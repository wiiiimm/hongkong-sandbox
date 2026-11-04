"""Diagnostic ranking of the fixed 190-source identity cohort; no queue or acceptance."""
import importlib.util, json, math, uuid
import shapely
from shapely.geometry import Polygon, GeometryCollection, box
from run import ROOT, HERE, read, save, digest, connect, reservations
from government_georef_cell_identity import geographic_cell

BATCH='government-xl-identity-primary-spatial-ranking-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=ROOT/'docs/astra-city/government-import'

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj

def parity(rings):
 result=GeometryCollection()
 for ring in rings: result=result.symmetric_difference(Polygon(ring))
 assert result.is_valid
 return result

def main():
 assert not (DOC/'ranking.json.gz').exists()
 inp=BASE/'government-xl-identity-search-20261009/actionable-dispositions.json.gz'
 rows=read(inp)['rows'];assert len(rows)==190
 opfile=BASE/'government-xl-identity-search-op-structures-20261009/official-op-relationship-research.json.gz'
 op={r['uid']:r for r in read(opfile)['rows']}
 manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());man=read(manifest)
 installed=set();pins={str(inp.relative_to(ROOT)):digest(inp.read_bytes()),str(opfile.relative_to(ROOT)):digest(opfile.read_bytes()),str(manifest.relative_to(ROOT)):mh}
 for url in man['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;pins[str(p.relative_to(ROOT))]=digest(p.read_bytes())
  for m in read(p)['models']:
   if m.get('placementReviewed') is True:installed.add((m['uid'],m['modelId']))
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  native={k+'/'+m['modelId']:m for k,m in c.execute("SELECT cache_key,m FROM astra_modelling.native_stage_results,LATERAL jsonb_array_elements(result->'models') m WHERE cache_key=ANY(%s) AND m->>'modelId'=ANY(%s)",(list({r['sourceKey'].split('/')[0] for r in rows}),[r['modelId'] for r in rows])).fetchall()}
 save(DOC/'native-source-metadata.json.gz',{'rows':native,'readOnly':True})
 cache={p.name[:-7]:p for p in (HERE/'local').rglob('*.glb.gz') if p.parent.name=='assets'}
 decoder=module('rank_original_decode','xl-second-pass.py');formsmod=module('rank_current_forms','xl-final-script-pass.py');out=[];tileCache={}
 def local_forms(bounds):
  query=box(*bounds);result=[]
  for tile in man['tiles']:
   if not box(*tile['bounds']).intersects(query):continue
   url=tile['url']
   if url not in tileCache:
    p=ROOT/'3d-viewer'/url;pins[str(p.relative_to(ROOT))]=digest(p.read_bytes());tileCache[url]=[(b,formsmod.form_polygon(b),url) for b in read(p)['buildings'] if b.get('rings')]
   result.extend((b,g,u) for b,g,u in tileCache[url] if g.intersects(query))
  return result
 for r in rows:
  item={k:r[k] for k in ['uid','modelId','sourceKey','sourceSHA256','name','expectedType']}
  item.update(installedInCurrentCatalogue=(r['uid'],r['modelId']) in installed,primaryLookupState=r['officialLookupState'],historicalIdentityState=r['identityState'],installationApproved=False,queueCreated=False)
  ownership=op.get(r['uid'],{});item.update(officialStructureIds=ownership.get('structureIds',[]),explicitStructureRelatedUids=[b['uid'] for b in ownership.get('currentGroupForms',[])],officialPrimaryCandidates=len(r['officialCandidates']))
  candidates=[a for a in r['officialCandidates'] if a.get('sourceCurrentExactCSUIDMatches') and a.get('sourceTypeMatches')]
  if len(candidates)!=1:
   item.update(measurementState='no-unique-exact-primary-candidate',ordinaryNumericBoundsPass=None);out.append(item);continue
  claim=reservations.claim('xl-identity-rank-'+str(uuid.uuid4()),['native-model:'+r['sourceKey']],batch=BATCH,ttl=600)
  if not claim['ok']:
   item.update(measurementState='active-source-reservation',ordinaryNumericBoundsPass=None);out.append(item);continue
  lease=claim['reservation']
  try:
   m=native[r['sourceKey']];sha=r['sourceSHA256'];p=cache[sha];assert digest(p.read_bytes())==sha==m['asset']['sha256']
   decoder.LOCAL=p.parent.parent;tri=decoder.glb_triangles({'sourceSHA256':sha,'modelId':r['modelId'],'triangles':m['triangles'],'native':{'model':m}})
   projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));fresh=candidates[0];official=parity(fresh['officialRings']);lo,hi=m['worldBounds']
   bounds=[lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2];forms=local_forms(bounds)
   if len(out)<3:assert {b['uid'] for b,_,_ in forms}=={b['uid'] for b,_,_ in formsmod.load_forms(bounds)},'Cached complete current form membership differs'
   own=next(b for b,_,_ in forms if b['uid']==r['uid']);current=parity(own['rings']);extra=projection.difference(official);intersections=[]
   for b,_,url in forms:
    pins[str((ROOT/'3d-viewer'/url).relative_to(ROOT))]=digest((ROOT/'3d-viewer'/url).read_bytes())
    if b['uid']==r['uid']:continue
    area=float(extra.intersection(parity(b['rings'])).area)
    if area>0:intersections.append({'uid':b['uid'],'name':b.get('name'),'CSUID':b.get('buildingCSUID'),'type':b.get('structureType'),'areaM2':area,'parent':b.get('parent')})
   other=shapely.union_all([parity(b['rings']) for b,_,_ in forms if b['uid']!=r['uid']]);coverage=float(official.intersection(projection).area/official.area);extent=float(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),official).max());foreign=float(extra.intersection(other).area)
   cell=geographic_cell(r['modelId'],own['buildingCSUID'],own['structureType'])
   measures={'targetCoverage':coverage,'maximumSourceExtentM':extent,'unrelatedExcessOverlapM2':foreign,'unrelatedActorCount':len(intersections),'currentTargetCoverage':float(current.intersection(projection).area/current.area),'currentPrimarySymmetricDifferenceM2':float(current.symmetric_difference(official).area),'sourceWholeCell':bool(projection.covers(cell)),'primaryWholeCell':bool(official.covers(cell))}
   item.update(measurementState='complete-original-current-local-forms-captured-primary',measures=measures,ordinaryNumericBoundsPass=coverage>=.95 and extent<=10 and foreign<=1,foreignActors=sorted(intersections,key=lambda x:(-x['areaM2'],x['uid'])),sourcePath=str(p.relative_to(ROOT)),sourceTrianglesSHA256=digest(tri.astype('<f8').tobytes()),sourceTriangles=len(tri),sourceBounds=m['worldBounds'],primaryAttributes=fresh['attributes'],sourceSHA256Verified=True)
   pins[str(p.relative_to(ROOT))]=sha
  except Exception as e:
   item.update(measurementState='diagnostic-input-or-decoder-unresolved',error=type(e).__name__+': '+str(e),ordinaryNumericBoundsPass=None)
  finally: assert reservations.release(lease)['ok']
  out.append(item);save(DOC/'progress.json',{'checked':len(out),'total':190});print(json.dumps({'uid':r['uid'],'numericPass':item['ordinaryNumericBoundsPass'],'state':item['measurementState'],'measures':item.get('measures')}),flush=True)
 assert digest(manifest.read_bytes())==mh
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h
 def key(r):
  x=r.get('measures',{});c=x.get('targetCoverage');e=x.get('maximumSourceExtentM');f=x.get('unrelatedExcessOverlapM2');a=x.get('unrelatedActorCount')
  return (r['installedInCurrentCatalogue'],r['ordinaryNumericBoundsPass'] is not True,c is None or e is None or f is None, c is not None and c<.95,e is not None and e>10, f if f is not None else math.inf,a if a is not None else math.inf,e if e is not None else math.inf,-c if c is not None else math.inf,str(r.get('uid') or r['sourceKey']))
 save(DOC/'unsorted-complete-measurements.json.gz',{'rows':out,'inputHashes':pins,'manifestSHA256':mh})
 out.sort(key=key)
 for i,r in enumerate(out,1):r['diagnosticRank']=i
 save(DOC/'ranking.json.gz',{'rows':out,'inputHashes':pins,'manifestSHA256':mh,'qualification':'Deterministic research ranking, no queue, identity approval, or physical acceptance. Complete original faces/vertices versus exact uniquely mapped captured primary outlines and all current local actors; original bytes/poses unchanged. Captured primary records are not asserted to be a new provider revision. Every foreign actor retained, explicit OP relationship is descriptive only. Unknown and active-reserved inputs stay unresolved. Whole-cell and all physical/runtime/browser gates remain independent.'})

if __name__=='__main__':main()
