"""Locate complete identity projection discrepancies; no approval or geometry changes."""
from pathlib import Path
import shapely
from shapely.geometry import Polygon,box,mapping
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-verdant-authoritative-identity-v1-20261018';BATCH='government-xl-wave-verdant-identity-residuals-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 sources={}
 for name,file,key in [('government-xl-wave-all-original-support-distance-v1-20261017','support-inputs.json','sources'),('government-xl-wave-verdant-podium-support-v1-20261017','support-inputs.json','sources'),('government-xl-wave-verdant-block2-original-recovery-v1-20261017','selection.json.gz','rows'),('government-xl-wave-verdant-194544-original-recovery-v1-20261017','selection.json.gz','rows')]:
  p=BASE/name/file;refs.append(p);sources.update({x['uid']:x for x in read(p)[key]})
 final=module('wave_identity_residual_geometry',HERE/'xl-final-script-pass.py');summaries=read(PRIOR/'summary.json')['rows'];uids=[r['uid']for r in summaries];projections={}
 for uid in uids:
  row=sources[uid];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];projections[uid]=final.projection(decode_original_world_triangles(raw))
 results=[]
 for record in summaries:
  if record['proof']['passed']:continue
  uid=record['uid'];row=sources[uid];b=row['source']['building'];target=Polygon(b['rings'][0],b['rings'][1:]);source=projections[uid];missing=target.difference(source);excess=source.difference(target);parts=list(source.geoms)if source.geom_type=='MultiPolygon'else[source];holes=unary_union([Polygon(h)for p in parts for h in p.interiors]);insideholes=missing.intersection(holes);boundarymissing=missing.difference(holes)
  cell=box(*record['proof']['geographicCell']['worldXZBounds']);other=unary_union([p for u,p in projections.items()if u!=uid]);detail=dict(uid=uid,sourceSHA256=row['sourceSHA256'],rawReasons=record['proof']['reasons'],targetAreaM2=target.area,sourceAreaM2=source.area,missingAreaM2=missing.area,missingInsideSourceHolesM2=insideholes.area,missingBoundaryAreaM2=boundarymissing.area,missingCoveredByOtherAssemblyOriginalsM2=missing.intersection(other).area,excessAreaM2=excess.area,excessCoveredByOtherAssemblyOriginalsM2=excess.intersection(other).area,cellAreaM2=cell.area,cellCoveredBySourceM2=cell.intersection(source).area,cellCoveredByTargetM2=cell.intersection(target).area)
  assert abs(insideholes.area+boundarymissing.area-missing.area)<1e-7
  geo=dict(type='FeatureCollection',features=[dict(type='Feature',properties=dict(kind=k,uid=uid),geometry=mapping(g))for k,g in [('target',target),('source',source),('missing',missing),('excess',excess),('georefCell',cell)]])
  save(DOC/(uid.replace('/','-').replace(':','-')+'.geojson'),geo);results.append(detail);print(detail,flush=True)
 save(DOC/'summary.json',dict(rows=results,fullAcceptance=False,qualification='Exact planar geometry only. Overlap with another assembly original does not prove common identity or grant placement acceptance. Complete residual polygons retained for source-specific review.'))
 refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py',*[ROOT/p for p in pins]])
 out=module('wave_residual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'nine-original-identity-residual-accounting-v1',list(set(refs)),dict(uids=[x['uid']for x in results],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
