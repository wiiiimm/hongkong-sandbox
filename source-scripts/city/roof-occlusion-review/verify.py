"""Verify source-backed candidate boundaries, coverage and unchanged inputs."""
from audit import *

def main():
 audit=read(D/'audit.json');report=read(D/'patch-review.json');root=R/'3d-viewer/city/data/terrain.json';assert sha(root)==report['parentSha256']==audit['rootTerrainSha256'];parent=shared.shared.fine.DemSampler(read(root),rendered=True);checked=[]
 for row in report['rows']:
  path=R/row['candidate'];assert sha(path)==row['sha256'];patch=read(path);sampler=shared.shared.fine.DemSampler(patch,rendered=True);g=patch['meta']['georef'];errors=[]
  for r in range(patch['h']):
   for c in range(patch['w']):
    if c not in(0,patch['w']-1)and r not in(0,patch['h']-1):continue
    x=g['bE']+c-834500;z=816500-g['bN']+r;errors.append(abs(sampler.ground(x,z)-parent.ground(x,z)))
  assert max(errors)<1e-5
  assert not row['regressions'] and len(row['neighbours'])==len({n['uid']for n in row['neighbours']})
  source=next(r for r in audit['rows']if r['uid']==row['uid']);assert sha(R/source['modelSourceManifest'])==source['modelSourceManifestSha256'];assert sha(R/source['terrainManifest'])==source['terrainManifestSha256'];assert source['nativeTIN']['areaAboveHighestRoofPlusTolerance']==0;assert abs(source['nativeTIN']['coverageArea']-source['sourceFootprintArea'])<1e-5
  assert row['highestRoofFlagResolved'];checked.append({'uid':row['uid'],'boundarySamples':len(errors),'maxRenderedBoundaryError':max(errors),'neighbourFeatures':len(row['neighbours']),'introducedEnvelopeFlags':0,'nativeFootprintCoverageFraction':source['nativeTIN']['coverageArea']/source['sourceFootprintArea'],'targetRoofClearance':row['targetNativeRoof']-row['targetAfter']['max']})
 save(D/'verification.json',{'issue':'HKS-214','passed':True,'verticalScale':1,'published':False,'modelsChanged':0,'rows':checked,'limitations':['These are staged source-TIN corrections. Normal-scene integration, broader walking/mobile checks and publication guards remain root workflow responsibilities.']});print(json.dumps(checked,indent=2))
if __name__=='__main__':main()
