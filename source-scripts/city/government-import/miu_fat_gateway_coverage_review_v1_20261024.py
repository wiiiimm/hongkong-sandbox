"""Bind the existing original gateway to its estimated basic fallback record.

Staged-validation proposal only. No model, renderer, inventory or terrain writes.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from dependency_preflight import policy
BASE=ROOT/'docs/astra-city/government-import'
SOURCES={'landsd/165889:0':'5c2a3560515f4ad2f80e6f2d5b634988ae4d655a9268c137bd55c5952e00b862','landsd/233638:0':'0bd1fc65477e3b4f84805586f62cb2c0e8aca133532de79822eb413e88dcdf91','landsd/241215:0':'901fd6a0098ede2e783deeb9b308f9594fe31dc0ca44ef2c6e1790adb169ba7a'}
PRIMARY='landsd/165889:0';SECONDARY='landsd/197385:0'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);a=p.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch;out=BASE/a.batch;assert not out.exists();refs=[Path(__file__)];cache={}
    def take(n,f):
        if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        path=BASE/n/f;assert digest(path.read_bytes())==cache[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime='government-xl-next-repairs-miu-fat-three-current-runtime-v1-20261024';attrs='government-xl-next-repairs-miu-fat-three-current-attributes-v1-20261024';scope='government-xl-next-repairs-miu-fat-three-current-model-scope-v1-20261024';identity='government-xl-next-repairs-miu-fat-three-current-identity-v1-20261024'
    selected=take(runtime,'selection.json.gz');rows={r['uid']:r for r in selected['rows']};assert {u:r['sourceSHA256']for u,r in rows.items()}==SOURCES
    raw=take(identity,'165889:0/identity.json');assert raw['sourceSHA256']==SOURCES[PRIMARY]and raw['exactCurrentComponentRoute']['qualified']and raw['originalOwnership']['sourceGraphVerified']and raw['originalOwnership']['originalRootName']=='B164163115502063C0'
    assert raw['exactWholeCellCoverage']['covered']and raw['completeRecordProjection']
    s=take(scope,'summary.json');forms=take(scope,'165889:0-forms.json.gz');secondary=next(r for r in forms if r['building']['uid']==SECONDARY);form=secondary['building'];primary=rows[PRIMARY]['source']['building']
    assert form['objectId']==197385 and form['buildingCSUID']=='1637731168T20080122'and form['kind']=='roof'and form['structureType']=='Open-sided Structure'
    assert form['heightSource']=='estimated'and form['height']==3 and form['baseHeightHKPD']is None and form['topHeightHKPD']is None
    assert form['name']==primary['name']=='MIU FAT BUDDHIST MONASTERY COMPLEX BLOCK'
    path=ROOT/'3d-viewer'/secondary['tile'];assert digest(path.read_bytes())==secondary['tileSHA256'];assert next(f for f in read(path)['buildings']if f['uid']==SECONDARY)==form;refs.append(path)
    at={r['uid']:r for r in take(attrs,'attributes.json.gz')['rows']}[PRIMARY];index=np.asarray(at['completeOriginalIndex']).reshape(-1,3);asset=ROOT/rows[PRIMARY]['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[PRIMARY];refs.append(asset)
    worlds={'original':decode_original_world_triangles(asset.read_bytes())}
    for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(at[field]).reshape(-1,3)[index]
    polygon=shapely.Polygon(form['rings'][0],form['rings'][1:]);coverage=[]
    for mode,tri in worlds.items():
        projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));covered=bool(shapely.covers(projection,polygon));coverage.append(dict(mode=mode,completeSourceFaces=len(tri),targetAreaM2=float(polygon.area),intersectionAreaM2=float(projection.intersection(polygon).area),completeSourceProjectionCoversRecord=covered));assert covered,(mode,coverage[-1])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());assert msha==s['currentManifestSHA256']==selected['manifestSHA256'];refs.append(manifest);allmodels=[]
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;refs.append(path);allmodels+=read(path)['models']
    assert len(allmodels)==len({m['uid']for m in allmodels})==6873 and not({PRIMARY,SECONDARY}&{m['uid']for m in allmodels})
    for m in allmodels:
        assert SECONDARY not in {u for u,_ in policy.dependency_rows(m)},'An installed actor retains this basic support'
        assert all(d.get('supportUid')!=SECONDARY and d.get('uid')!=SECONDARY for d in m.get('retainedBasicSupportDependencies',[]))
    photoFolder=HERE/'local/government-xl-next-repairs-miu-fat-government-photo-context-v1-20261024';pp=photoFolder/'provenance.json';photos=read(pp);refs.append(pp);wanted={1:'ba8b',2:'unknown'};photoRefs=[]
    for number in [1,2]:
        path=photoFolder/('government-photo-'+str(number)+'.jpg');rec=next(r for r in photos['rows']if r['path']==str(path.relative_to(ROOT)));assert digest(path.read_bytes())==rec['sha256']and rec['sourceURL'].startswith('https://www.gohk.gov.hk/uploads/photo/large/16_TM_6_');refs.append(path);photoRefs.append(rec)
    result=dict(uids=[PRIMARY],secondaryUid=SECONDARY,sourceSHA256=SOURCES[PRIMARY],requiredOriginalAssembly=SOURCES,sourceModelId=rows[PRIMARY]['modelId'],currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=msha),secondaryCurrentForm=secondary,completeFourWorldCoverage=coverage,allInstalledActorsChecked=len(allmodels),installedSupportUsers=[],reviewer='ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,governmentPhotosActuallyViewed=photoRefs,sourcePhotosPage=photos['sourcePage'],interpretation='The identically named estimated-height roof record is the entrance gateway already present in the complete unchanged main-complex original. ROOT inspected the original assembly/contact diagrams and government photos1/2 showing the open gateway with layered cornices and substantial piers. The estimated flat three-metre canopy is its coarse fallback, not a separate original asset to invent. This mapping is limited to this source SHA and exact current secondary record. Photographs do not supply surveyed dimensions.',stagedProposal=dict(uid=PRIMARY,suppressesBuildingUids=[SECONDARY]),coverageApprovedForStagedValidation=True,installationApproved=False,publication=False,qualification='Proposed dynamic fallback coverage only: retain the basic record and terrain, hide its coarse geometry only while the exact verified detailed source is active, and require desktop/mobile activation/failure-retry evidence. No installation credit, source edits, independent-original alias or broad suppression permission. Full remaining identity/placement/related-source/elderly-home interface/runtime checks still required.')
    save(out/'gateway-coverage-review.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'dependency_preflight.py',HERE.parent/'island-detail-integration/model_dependencies.py']);module('gateway_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-source-gateway-basic-fallback-coverage-proposal',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
