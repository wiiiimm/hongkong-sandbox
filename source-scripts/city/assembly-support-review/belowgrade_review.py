"""Check exact lower-face elevations against the matching surveyed building base."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/astra-city/assembly-support-review';HERE=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();uid='landsd/255427:0';m=read(HERE/'belowgrade-candidates/catalogue.json')['models'][0];manifest=read(ROOT/'3d-viewer/city/data/manifest.json');found=[]
for tile in manifest['tiles']:
 path=ROOT/'3d-viewer'/tile['url']
 for b in read(path)['buildings']:
  if b['uid']==uid:found.append((b,path))
assert len(found)==1;b,path=found[0];assert b['baseSource']=='landsd' and b['buildingCSUID']==m['buildingCSUID'];r=read(OUT/'belowgrade-surface-review.json')['rows'][0];base=b['baseHeightHKPD'];assert all(t['yRange'][1]<base for t in r['buriedTriangles']);above=[t for t in r['buriedUpwardTriangles'] if t['yRange'][1]>=base];assert not above
proof={'issue':'HKS-214','uid':uid,'sourceSHA256':m['sha256'],'sourceCSUID':m['buildingCSUID'],'officialFootprintTile':str(path.relative_to(ROOT)),'officialFootprintTileSHA256':sha(path),'surveyedBaseHKPD':base,'nativeModelMinY':m['worldBounds'][0][1],'highestWhollyBuriedFaceY':max(t['yRange'][1] for t in r['buriedTriangles']),'buriedUpwardAreaM2':sum(t['area'] for t in r['buriedUpwardTriangles']),'whollyBuriedFacesAtOrAboveSurveyedBase':0,'sourceSurfaceReviewSha256':sha(OUT/'belowgrade-surface-review.json'),'visualEvidence':'docs/astra-city/assembly-support-review/framing-foundation/report.json','decision':'Accept exact native component with unchanged terrain. Every fully buried face lies below the matching surveyed LandsD base, and the exposed tower/facade/roof is clear in normal and isolated exports. Preserve below-grade source detail; no model shifts or invented supports.','wholeLandmarkAccepted':False}
(OUT/'belowgrade-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
