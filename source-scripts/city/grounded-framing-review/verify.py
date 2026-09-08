"""Verify full-source framing evidence and preserve provenance; no acceptance inference."""
import hashlib,json,pathlib
R=pathlib.Path(__file__).resolve().parents[3];D=R/'docs/astra-city/grounded-framing-review'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 selected=read(R/'source-scripts/city/grounded-model-review/selection.json');report=read(D/'report.json');inputs=read(D/'inputs.json');expected={r['uid']for r in selected['parts']};assert len(report['rows'])==len(expected)==24;assert {r['uid']for r in report['rows']}==expected;assert not report['errors'];assert sha(R/'source-scripts/city/grounded-model-review/selection.json')==inputs['selectionSha256'];assert sha(R/'source-scripts/city/grounded-model-review/candidates/catalogue.json')==inputs['catalogueSha256'];rows=[]
 for r in report['rows']:
  assert len(r['views'])==2 and {v['mode']for v in r['views']}=={'scene','isolated'}
  for v in r['views']:
   assert sha(D/v['file'])==v['sha256'];assert v['active'] and v['terrainUnchanged'] and v['nativeGeometryUnchanged'];assert v['final']['fullyFramed'];assert len(v['final']['projectedBounds'])==8
  isolated=next(v for v in r['views']if v['mode']=='isolated');scene=next(v for v in r['views']if v['mode']=='scene');assert isolated['final']['clear'];rows.append({'uid':r['uid'],'sourceComponentInspectable':True,'normalSceneCameraClear':scene['final']['clear'],'isolatedCameraClear':True,'bothViewsContainWholeBounds':True,'normalSceneTargetRayFraction':scene['final']['targetRays']/scene['final']['totalRays']})
 result={'issue':'HKS-214','verifiedParts':len(rows),'verifiedScreenshots':sum(len(r['views'])for r in report['rows']),'rows':rows,'inputManifestSha256':inputs['manifestSha256'],'currentManifestSha256':sha(R/'3d-viewer/city/data/manifest.json'),'selectionSha256':inputs['selectionSha256'],'candidateCatalogueSha256':inputs['catalogueSha256'],'published':False,'qualification':'Framing and source-component inspectability only. Human/agent image inspection and source/identity decisions remain separately recorded. Unrelated catalogue additions do not invalidate unchanged candidate bytes.'};(D/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'verifiedParts':result['verifiedParts'],'verifiedScreenshots':result['verifiedScreenshots'],'normalSceneClear':sum(r['normalSceneCameraClear']for r in rows),'isolatedClear':len(rows)}))
if __name__=='__main__':main()
