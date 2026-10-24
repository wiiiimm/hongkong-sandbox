"""DRAFT additive exact actual archive resolution; v2 result remains immutable."""
from pathlib import Path
import json
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';PRIOR=B/'government-xl-beverly-elm-exact-reference-resolution-v2-20261011/resolution.json';DOC=B/'government-xl-beverly-elm-exact-reference-resolution-v3-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(PRIOR);expected=dict(path='3d-viewer/city/data/manifest.json',sha256='c44b60b3963116940dc8cbab95e6d4acda6944bc2decdf874703828bba7465d6');assert old['unresolvedExactVersions']==[expected]and not old['resolutionComplete'];p=HERE/'local/government-xl-owned-57-sequence-20261006-242281-0-installed/manifest-before-installation.json';assert ref(p)['sha256']==expected['sha256'];alias=dict(originalPath=expected['path'],sha256=expected['sha256'],archive=ref(p),exactExistingPublisherBeforeManifest=True);new={**old,'historicalManifestAliases':old['historicalManifestAliases']+[alias],'unresolvedExactVersions':[],'resolutionComplete':True,'priorIncompleteResolution':ref(PRIOR),'evidenceRefs':old['evidenceRefs']+[ref(PRIOR),ref(Path(__file__)),ref(p)]};save(DOC/'resolution.json',new);print(json.dumps(dict(historicalExactAliases=len(new['historicalManifestAliases']),registryPreparedMetadataPointers=len(new['metadataLeafJsonPointers']),unresolved=[],currentAcceptance=False)))
if __name__=='__main__':main()
