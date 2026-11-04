"""Queue omitted native support candidates by source footprint adjacency, never approve support."""
import json,pathlib,hashlib,collections
from shapely.geometry import Polygon,box
from shapely.strtree import STRtree
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residential-support-review'
read=lambda p:json.loads(p.read_bytes())
def main():
 preflight=read(ROOT/'docs/astra-city/landmark-preflight/report.json');support=read(ROOT/'docs/astra-city/assembly-support-review/decisions-terrain-variant.json');held={r['uid'] for r in support['rows'] if not r['placementApproved']};parts=[p for p in preflight['parts'] if p['uid'] in held and p.get('candidate') and p['candidate']['worldBounds'][0][1]>2]
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');available={p['uid']for p in preflight['parts']if p.get('candidate')}
 for url in manifest['officialModelCatalogues']:available.update(m['uid']for m in read(ROOT/'3d-viewer'/url)['models'])
 boxes=[box(p['candidate']['worldBounds'][0][0]-1,p['candidate']['worldBounds'][0][2]-1,p['candidate']['worldBounds'][1][0]+1,p['candidate']['worldBounds'][1][2]+1) for p in parts];tree=STRtree(boxes);candidates={};hashes={}
 for tile in manifest['tiles']:
  if not any(box(*tile['bounds']).intersects(b) for b in boxes):continue
  path=ROOT/'3d-viewer'/tile['url'];hashes[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
  for b in read(path)['buildings']:
   if b['uid'] in available or not b.get('buildingCSUID') or b.get('baseSource')!='landsd' or b.get('heightSource')!='landsd':continue
   poly=Polygon(b['rings'][0],b['rings'][1:]);poly=poly if poly.is_valid else poly.buffer(0)
   if poly.is_empty:continue
   for i in tree.query(poly,predicate='intersects'):
    target=parts[int(i)];minimum=target['candidate']['worldBounds'][0][1]
    if b['base']>=minimum-2 or b['base']+b['height']<minimum-30:continue
    # Broad source envelopes nominate work only. Actual source triangles must later prove every accepted seam.
    overlap=poly.intersection(boxes[int(i)]).area
    if overlap<1:continue
    c=candidates.setdefault(b['uid'],{'uid':b['uid'],'objectId':b['objectId'],'csuid':b['buildingCSUID'],'name':b['name'],'structureType':b.get('structureType'),'base':b['base'],'top':b['base']+b['height'],'input':str(path.relative_to(ROOT)),'targets':[]})
    c['targets'].append({'uid':target['uid'],'name':target['name'],'nativeMinimumY':minimum,'footprintBoundsOverlapM2':round(overlap,3),'basicRoofToNativeBaseGap':round(minimum-b['base']-b['height'],3)})
 rows=[candidates[u]for u in sorted(candidates)];result={'issue':'HKS-214','version':1,'scope':'Previously omitted exact government support acquisition candidates, not structural support proof or landmark membership approval.','heldSourceParts':len(parts),'newSupportCandidates':len(rows),'potentiallyAffectedParts':len({t['uid']for r in rows for t in r['targets']}),'targets':rows,'runtimeTileHashes':hashes,'selectionPolicy':'Native target XY bounds +1m intersect retained surveyed footprint by>=1m²; source base>=2m below native target base; source top no more than30m below target base. Existing prepared/installed source UIDs excluded. Broad queue only: conservative acquisition/matching and actual triangle seams plus terrain/browser gates remain mandatory.','sourceDirectoryProof':'Not checked by this discovery step. Fetch only after canonical source reservation and exact directory/model matching.','publicationApproved':False};(DOC/'support-discovery.json').write_text(json.dumps(result,indent=2)+'\n');(HERE/'discovered-targets.json').write_text(json.dumps({'targets':[{'uid':r['uid'],'objectId':r['objectId'],'csuid':r['csuid'],'name':r['name']}for r in rows]},indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['targets','runtimeTileHashes']}))
if __name__=='__main__':main()
