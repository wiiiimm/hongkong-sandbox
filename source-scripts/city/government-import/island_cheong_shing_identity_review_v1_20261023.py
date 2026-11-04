"""Bind ROOT's exact four-original identity interpretation; physical work stays held."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from island_cheong_shing_named_identity_v1_20261023 import EXACT,FOREIGN,validate_named_boundary_contract


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-cheong-shing-named-identity-review-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)];cache={}
    def take(batch,name):
        if batch not in cache:cache[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=base/batch/name;assert digest(p.read_bytes())==cache[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    capture='government-xl-island-cheong-shing-four-original-runtime-v2-20261023';selected=take(capture,'selection.json.gz');sources={r['uid']:r for r in selected['rows']};assert set(sources)==set(EXACT)
    identities='government-xl-island-cheong-shing-four-original-identities-v1-20261023';primary=take('government-xl-island-cheong-shing-four-primary-identity-v1-20261023','summary.json');typed=take('government-xl-island-industrial-typed-primary-routing-v2-20261023','summary.json');spec=take('government-xl-island-industrial-typed-primary-routing-v2-20261023','spec-binding.json');family=take('government-xl-island-industrial-complete-family-coverage-v1-20261023','summary.json');boundarybatch='government-xl-island-cheong-shing-full-boundary-context-v1-20261023';boundary=take(boundarybatch,'summary.json');current=take('government-xl-island-industrial-paired-current-neighbours-v1-20261023','neighbour-inputs.json.gz');forms={r['building']['uid']:r['building']for r in current['rows']};assert len(forms)==774
    required={uid:r[2]for uid,r in EXACT.items()};validate_named_boundary_contract(boundary,family,required);assert typed['typedMetadataRoutesQualified']is True
    for path,sha in current['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']==family['currentManifestSHA256'];refs.append(manifest)
    images=[]
    for name in ['four-complete-originals.png','remaining-foreign-footprint-strip.png']:
        p=base/boundarybatch/name;assert digest(p.read_bytes())==cache[boundarybatch][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    reports=[]
    for uid,(modelid,csuid,sha,count,permit)in EXACT.items():
        row=sources[uid];form=row['source']['building'];assert row['modelId']==modelid and row['sourceSHA256']==sha and row['triangles']==count and form==forms[uid]and form['buildingCSUID']==csuid
        asset=ROOT/row['candidate']['path'];blob=asset.read_bytes();assert digest(blob)==sha;refs.append(asset);tri=decode_original_world_triangles(blob);assert len(tri)==count
        raw=take(identities,uid.split('/')[1]+'/identity.json');assert raw['sourceSHA256']==sha and raw['worldTrianglesSHA256']==digest(tri.astype('<f8').tobytes());assert raw['originalOwnership']['sourceGraphVerified']is True and raw['originalOwnership']['originalRootName']==modelid
        route=raw['exactCurrentComponentRoute'];assert route['qualified']is True and route['uid']==uid and route['source']['building']==form and route['official']['buildingCSUID']==csuid and route['official']['objectId']==form['objectId']
        record=next(p for p in primary['rows']if p['uid']==uid);p=record['officialFootprint'];assert record['exactCurrentCSUID']==csuid and record['occupationPermits']==[permit]and p['Status']=='Active'and p['GeoRefNo']==csuid[:10]
        assert p['BuildingID']==form['buildingId']and p['BuildingBlockType']==form['structureType']and p['BaseHeight']==form['baseHeightHKPD']and p['TopHeight']==form['topHeightHKPD']
        assert form['structureType']=={'01':'Tower','02':'Podium'}[modelid[11:13]]
        if uid in family['uids']:
            context=next(r for r in family['rows']if r['uid']==uid);assert set(context['remainingReasons'])==FOREIGN
            typedrow=next(r for r in typed['rows']if r['uid']==uid);assert typedrow['typedRoutingQualified']is True and typedrow['sourceSHA256']==sha
        else:assert raw['passed']is True and not raw['reasons']and raw['geographicCell']['originalProjectionCoversWholeCell']is True
        reports.append(dict(uid=uid,modelId=modelid,buildingCSUID=csuid,sourceSHA256=sha,completeSourceFaces=count,sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],currentManifestSHA256=selected['manifestSHA256'],identityAccepted=True,identityReviewApproved=True,proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawIdentityVerbatim=raw,coInstallationRequired=required,currentFormSuppression=False,currentTerrainExemption=False,currentCollisionExemption=False,physicalAccepted=False,installationApproved=False))
    interpretation=dict(reviewer='ROOT',sourceIdentityInterpretationUsedAI=True,aiGeometryModelling=False,imagesActuallyViewed=images,officialModelSubtypeSpec=spec,decision='These are the exact original Tower/Podium assets of two adjacent separately attributed permit families. The K28/80 podium is an exposed source contributor, so its coverage is assessed with its exact same-GeoRef tower, not by filling its source hole. The only remaining foreign projection strip is the fully identified adjacent K42/90 podium boundary. Complete original geometry and current vectors show that strip at their shared model boundary; it is not an alternate source identity. All774current forms and the raw spatial/intersection negatives remain. This source identity interpretation grants no collision, terrain, support, legal ownership, placement or publication exception.',identityAttributionOnly=True)
    save(out/'root-identity-interpretation.json',interpretation);save(out/'identity-by-uid.json.gz',dict(rows=reports));result=dict(uids=list(EXACT),rows=[{k:v for k,v in r.items()if k!='rawIdentityVerbatim'}for r in reports],identityAccepted=True,identityReviewOnly=True,coInstallationRequired=required,all774CurrentFormsRetained=True,currentManifestSHA256=selected['manifestSHA256'],rawSourceBoundaryAndIntersectionFailuresRetained=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='One hash-bound ROOT identity interpretation of four exact original assets and current primary records. All four originals must be present at installation. Generic identity rules and native cached evidence are unchanged; original source/foreign support/terrain/runtime/device/browser/publication checks remain separate and unapproved.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['island_cheong_shing_named_identity_v1_20261023.py','test_island_cheong_shing_named_identity_v1_20261023.py','exact_packed_world_geometry_20261009.py']);module('identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'root-exact-original-two-family-boundary-identity-review',refs,result);print(dict(identitiesApproved=list(EXACT),physicalAccepted=False,installationApproved=False),flush=True)

if __name__=='__main__':main()
