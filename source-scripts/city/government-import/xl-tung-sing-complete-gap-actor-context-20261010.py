"""Complete raw domain-gap intersections with every original and current actor."""
import importlib.util,numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-tung-sing-complete-gap-actor-context-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-tung-sing-interior-domain-source-invariance-20261010/diagnostic.json.gz';SELECT=DOC.parent/'government-xl-tung-sing-nested-current-identity-inputs-20261010/selection.json.gz'
def polygon(rings):
 out=shapely.GeometryCollection()
 for r in rings:out=out.symmetric_difference(shapely.Polygon(r))
 return out
def main():
 assert not DOC.exists();x=read(INPUT);gaps=shapely.from_wkb(x['rawChildRectangleMissingProjectionWKB']);selection=read(SELECT);manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());rows=[];hashes={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [INPUT,SELECT,manifest,__import__('pathlib').Path(__file__)]}
 sources={r['uid']:ROOT/r['candidate']['path'] for r in selection['rows']};retained={'landsd/12851:0','landsd/12852:0','landsd/12854:0','landsd/163705:0'}
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid'] in retained:
    a=p.parent/e['asset'];assert digest(a.read_bytes())==e['sha256'];sources[e['uid']]=a;hashes[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 assert set(sources)==retained|{r['uid'] for r in selection['rows']}
 for uid,p in sources.items():
  a=decode_original_world_triangles(p.read_bytes());projection=shapely.union_all(shapely.polygons(a[:,:,[0,2]]));hit=gaps.intersection(projection);rows.append({'uid':uid,'completeOriginalFaces':len(a),'completeOriginalWorldSHA256':digest(a.astype('<f8').tobytes()),'rawGapIntersectsWholeOriginalProjection':gaps.intersects(projection),'rawGapIntersectionAreaM2':hit.area,'rawGapIntersectionLengthM':hit.length,'rawGapIntersectionWKB':shapely.to_wkb(hit,hex=True)});hashes[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 s=importlib.util.spec_from_file_location('tung_gap_actual_forms',HERE/'xl-final-script-pass.py');final=importlib.util.module_from_spec(s);s.loader.exec_module(final);forms=final.load_forms(list(gaps.bounds));current=[]
 for b,_,url in forms:
  poly=polygon(b['rings']);hit=gaps.intersection(poly)
  if not hit.is_empty:current.append({'uid':b['uid'],'completeCurrentForm':b,'rawGapIntersectionAreaM2':hit.area,'rawGapIntersectionLengthM':hit.length,'rawGapIntersectionWKB':shapely.to_wkb(hit,hex=True)})
  hashes['3d-viewer/'+url]=digest((ROOT/'3d-viewer'/url).read_bytes())
 assert digest(manifest.read_bytes())==msha
 save(DOC/'diagnostic.json.gz',{'currentManifestSHA256':msha,'completeRawGapPieces':len(shapely.get_parts(gaps)),'completeRawGapAreaM2':gaps.area,'allSixCompleteOriginalActors':rows,'completeCurrentActorFormsCount':len(forms),'allIntersectingCurrentForms':current,'inputHashes':hashes,'physicalAccepted':False,'qualification':'Every original face of both new actors and allfour installed original parent actors is retained and projected. All current forms over the complete rawgap bounds are checked. Floating polygon gap intersections are raw witnesses, not exact finite coverage approval or permission to hide actors/fill terrain.'});print({'originalHits':[(r['uid'],r['rawGapIntersectionAreaM2']) for r in rows],'currentHits':len(current)},flush=True)
if __name__=='__main__':main()
