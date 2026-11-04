"""Resolve exact model-subtype metadata ambiguity; retain all other failures."""
from pathlib import Path
import gzip,re,subprocess,sys
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from typed_native_candidate_identity_v1_20261023 import qualify
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
URL='https://static.csdi.gov.hk/csdi-webpage/download/common/5fae157cd31d217e580ea22cd65cc3e12f4bd55a26bf26339693b2865204ae1e'


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-industrial-typed-primary-routing-v1-20261023';out=base/batch;assert not out.exists();out.mkdir();refs=[Path(__file__)];cache={}
    def take(batch,name):
        if batch not in cache:cache[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=base/batch/name;assert digest(p.read_bytes())==cache[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    wire,receipt=request(URL,json_expected=False);pdf=gzip.decompress(wire)if wire.startswith(b'\x1f\x8b')else wire;assert pdf.startswith(b'%PDF-');path=out/'official-model-information-sheet.pdf';path.write_bytes(pdf);save(out/'official-model-information-sheet-request.json',dict(**receipt,decodedSHA256=digest(pdf),gzipDecoded=wire!=pdf))
    textpath=out/'official-model-information-sheet.txt';subprocess.run(['pdftotext','-layout',str(path),str(textpath)],check=True);text=textpath.read_text();assert re.search(r'01\s*=\s*Tower',text)and re.search(r'02\s*=\s*Podium',text)
    spec=dict(url=URL,pdfSHA256=digest(pdf),pdfPageOneBased=3,version='1.0 September 2025',meaning='Building Model ID subtype at characters 12–13: 01 Tower, 02 Podium. Source GeoRef is characters 2–11. No building geometry or physical acceptance inferred.');save(out/'spec-binding.json',spec)
    capture='government-xl-island-cheong-shing-four-original-runtime-v2-20261023';selection=take(capture,'selection.json.gz');identities='government-xl-island-cheong-shing-four-original-identities-v1-20261023';primary=take('government-xl-island-industrial-three-primary-identity-v1-20261023','summary.json');records=[r['officialFootprint']for r in primary['rows']];rows=[]
    tile=ROOT/'3d-viewer/city/data/tiles/0_-3.json';forms=read(tile)['buildings'];manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.extend([tile,manifest])
    for uid in ['landsd/20270:0','landsd/159422:0']:
        row=next(r for r in selection['rows']if r['uid']==uid);assert [f for f in forms if f['uid']==uid]==[row['source']['building']]
        raw=take(identities,uid.split('/')[1]+'/identity.json');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);result=qualify(raw,row,records,forms);assert result['passed']is False
        save(out/(uid.split('/')[1]+'.json'),dict(**result,rawIdentityVerbatim=raw,specBinding=spec));rows.append(result);print(dict(uid=uid,typedRoutingQualified=True,remainingReasons=result['reasons']),flush=True)
    result=dict(uids=[r['uid']for r in rows],rows=rows,currentManifestSHA256=selection['manifestSHA256'],typedMetadataRoutesQualified=True,identityAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Official Model ID Tower/Podium subtype plus exact active primary records disambiguates the two complete same-GeoRef cached native candidates. Original source graphs/bytes and current records rechecked; spatial, unrelated-source overlap, partial-podium coverage/cell and all physical failures remain. Generic production identity verifier is unchanged; no model queued, skipped or approved.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['typed_native_candidate_identity_v1_20261023.py','test_typed_native_candidate_identity_v1_20261023.py']);refs.append(HERE.parent/'landsd-territory/source.py');module('typed_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-official-typed-metadata-routing-with-raw-spatial-failures',refs,result)

if __name__=='__main__':main()
