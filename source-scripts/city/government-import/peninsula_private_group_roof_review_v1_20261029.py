"""Review exact source/OSM roof correspondence for a private runtime experiment."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from peninsula_private_group_roof_contract_v1_20261029 import OWNER,TOWER,ROOF,SOURCES,form_sha
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-peninsula-private-group-roof-review-v1-20261029'
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    primary='government-xl-peninsula-primary-component-context-v1-20261029';source=take(primary,BASE/primary/'summary.json');assert source['sourceSHA256ByUid']==SOURCES
    scope='government-xl-peninsula-pair-current-v1-20261029-model-scope';forms={r['building']['uid']:r['building']for r in take(scope,BASE/scope/'270876:0-forms.json.gz')};assert set(forms)=={OWNER,TOWER,ROOF}
    views='government-xl-peninsula-osm-roof-contact-views-v1-20261029';take(views,BASE/views/'summary.json');picture=BASE/views/'before-after-contact-context.png';assert digest(picture.read_bytes())==pins[views][str(picture.relative_to(ROOT))];refs.append(picture)
    preview='government-xl-peninsula-pair-retained-roof-private-browser-v1-20261029';preview_receipt,pins[preview]=authenticate(BASE/preview);refs.append(BASE/preview/'result.json');assert preview_receipt['previewOnly']is True and preview_receipt['installationApproved']is False
    images=[dict(path=str(picture.relative_to(ROOT)),sha256=digest(picture.read_bytes()))]
    for width in [1280,390]:
        report=take(preview,BASE/preview/str(width)/'staged-browser.json');assert report['passed']and not report['errors']
        for v in report['views']:
            if 'time'not in v:continue
            p=BASE/preview/str(width)/v['file'];assert digest(p.read_bytes())==pins[preview][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[preview][str(manifest.relative_to(ROOT))];refs.append(manifest)
    review=dict(uids=[OWNER,TOWER],sourceSHA256ByUid=SOURCES,ownerUid=OWNER,roofUid=ROOF,activationGroup=sorted(SOURCES),sourceFormSHA256ByUid={u:form_sha(forms[u])for u in SOURCES},exactRoofForm=forms[ROOF],roofFormSHA256=form_sha(forms[ROOF]),primaryOSMWay=source['overlappingOSMForm'],currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),privateExperimentApproved=True,imagesActuallyViewed=images,reviewer='Codex ROOT',sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,identityAccepted=False,installationApproved=False,publication=False,qualification='ROOT inspected all eight real desktop/mobile day/night original-source exports and the four-angle exact contact diagram. The one-storey OSM roof part is the existing BASIC entrance-canopy box, visibly intersecting the detailed original roof, posts and roof recesses. Its complete current form, version4 roof tags, both source revisions and current manifest are pinned. Permit only a private exact-pair atomic availability test and conditional suppression of this exact duplicate while its owner is active. No global OSM/canopy policy change, no source/BASIC geometry edits, no support-root credit, no physical/visual/publication approval. Both originals must load/retire together; roof must return on failed download/Base-only/eviction. Raw spatial/support failures remain independently obligated.')
    save(out/'ROOT-PRIVATE-EXPERIMENT-REVIEW.json',review);save(out/'summary.json',review);refs.append(HERE/'peninsula_private_group_roof_contract_v1_20261029.py');module('peninsula_private_roof_review',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-Peninsula-pair-and-OSM-roof-private-availability-experiment-review',refs,review)
if __name__=='__main__':main()
