"""Exact BASIC contacts with separately measured full overlapping-native context; diagnostic only."""
import argparse
from pathlib import Path
import numpy as np
import subprocess
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','scope','runtime','attributes','native-context']:p.add_argument('--'+k,required=True)
    p.add_argument('--supports');p.add_argument('--uid',action='append');a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    scope=take(a.scope,base/a.scope/'summary.json');selection=take(a.runtime,base/a.runtime/'selection.json.gz');attrs={r['uid']:r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']};support=take(a.supports,base/a.supports/'support-bindings.json')if a.supports else [];by_support={r['uid']:r['supportUid']for r in support}
    wanted=set(a.uid or scope['uids']);assert wanted and wanted<=set(scope['uids'])and wanted<={r['uid']for r in selection['rows']}
    scope={**scope,'rows':[r for r in scope['rows']if r['uid']in wanted]};selection={**selection,'rows':[r for r in selection['rows']if r['uid']in wanted]}
    forms={};per_source={};native_separation=[];native_uids={};native_overlap=[]
    native_context=take(a.native_context,base/a.native_context/'summary.json')
    selected_sources={r['uid']:r for r in selection['rows']}
    for r in scope['rows']:
        native_uids[r['uid']]={n['uid']for n in r['nearbyNativeActors']}
        lo,hi=np.asarray(r['completeSourceFourWorldBounds'])
        for native in r['nearbyNativeActors']:
            values=np.asarray(native['completeFourWorldBounds']).reshape(-1,3);nlo,nhi=values.min(0),values.max(0);gaps=np.maximum(nlo-hi,lo-nhi)
            if not np.any(gaps>0):
                pair=next(q for q in native_context['rows']if q['uid']==r['uid']and q['nativeUid']==native['uid'])
                assert pair['sourceSHA256']==selected_sources[r['uid']]['sourceSHA256']==attrs[r['uid']]['sourceSHA256']
                assert pair['nativeSHA256']==native['sourceSHA256']==pair['rawCurrentNativeEntry']['sha256']
                assert {m['mode']for m in pair['modes']}=={'original','literal','leftF32','balancedF32'}and len(pair['modes'])==4
                for m in pair['modes']:
                    proof=take(a.native_context,base/a.native_context/(r['uid'].split('/')[1]+'--'+native['uid'].split('/')[1]+'--'+m['mode']+'.json.gz'))
                    assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0 and len(proof['contacts'])==m['finiteContactPairs']
                    assert m['sourceFaces']==len(attrs[r['uid']]['completeOriginalIndex'])//3 and m['nativeFaces']==pair['rawCurrentNativeEntry']['triangles']
                native_overlap.append(pair)
                continue
            native_separation.append(dict(uid=r['uid'],nativeUid=native['uid'],nativeSourceSHA256=native['sourceSHA256'],completeSourceFourWorldBounds=r['completeSourceFourWorldBounds'],completeNativeFourWorldBounds=native['completeFourWorldBounds'],strictSeparatingAxisGapsM=gaps.tolist(),qualification='Conservative complete four-world bounds strictly disjoint; exact represented endpoint inequalities, no epsilon or margin exemption.'))
        rows=take(a.scope,base/a.scope/(r['uid'].split('/')[1]+'-forms.json.gz'));per_source[r['uid']]=rows
        for form in rows:forms[form['building']['uid']]=dict(building=form['building'],tile='3d-viewer/'+form['tile'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==scope['currentManifestSHA256'];refs.append(manifest)
    assert digest(manifest.read_bytes())==pins[a.native_context][str(manifest.relative_to(ROOT))]
    native_assets=[]
    for pair in native_overlap:
        matches=[]
        for url in read(manifest)['officialModelCatalogues']:
            catalogue=ROOT/'3d-viewer'/url
            for entry in read(catalogue)['models']:
                if entry['uid']==pair['nativeUid']:matches.append((entry,catalogue))
        assert len(matches)==1;entry,catalogue=matches[0];assert entry==pair['rawCurrentNativeEntry']
        asset=catalogue.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];refs.extend([catalogue,asset]);native_assets.append((asset,entry['sha256']))
    inputpath=out/'basic-inputs.json';save(inputpath,dict(manifestSHA256=scope['currentManifestSHA256'],currentInputHashes=scope['currentFormTileHashes'],rows=list(forms.values())))
    tool=HERE/'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs';basicpath=out/'basic.json'
    with(out/'capture.log').open('w')as log:subprocess.run(['node',str(tool),str(inputpath.relative_to(ROOT)),str(basicpath.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    basic=read(basicpath);meshes={r['uid']:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in basic['rows']};summary=[]
    for row in selection['rows']:
        uid=row['uid'];attr=attrs[uid];index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
        modes={'before-basic':meshes[uid],'original':decode_original_world_triangles(asset.read_bytes())}
        for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:modes[mode]=np.asarray(attr[field]).reshape(-1,3)[index]
        foreign=[r['building']['uid']for r in per_source[uid]if r['building']['uid']not in [uid,by_support.get(uid)]and r['building']['uid']not in native_uids[uid]]
        for other in foreign:
            target=meshes[other];foreign_projection=shapely.union_all(shapely.polygons(target[:,:,[0,2]]));pairs=[]
            for mode,tri in modes.items():
                proof=exact_finite_contacts(tri,list(range(len(tri))),target,list(range(len(target))))
                path=out/(uid.split('/')[1]+'--'+other.split('/')[1]+'--'+mode+'.json.gz');save(path,proof)
                source_projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));area=source_projection.intersection(foreign_projection).area
                positive=[c for c in proof['contacts']if c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
                pairs.append(dict(mode=mode,completeSourceFaces=len(tri),completeForeignFaces=len(target),positiveContactPairs=len(positive),allFiniteContactPairs=len(proof['contacts']),projectedOverlapAreaM2=area))
                print(dict(uid=uid,foreign=other,mode=mode,positiveContactPairs=len(positive),projectedOverlapAreaM2=area),flush=True)
            summary.append(dict(uid=uid,foreignUid=other,modes=pairs))
    for path,sha in basic['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    assert digest(manifest.read_bytes())==scope['currentManifestSHA256']
    for asset,sha in native_assets:assert digest(asset.read_bytes())==sha
    result=dict(overlappingNativeRawContexts=native_overlap,nativeContext=a.native_context,uids=[r['uid']for r in selection['rows']],foreignPairs=len(summary),rows=summary,nativeCompleteFourWorldSeparation=native_separation,sourceGeometryChanges=0,installationApproved=False,publication=False,status='model-only-current-foreign-basic-finite-contacts',qualification='Every complete scoped foreign basic render mesh checked against before-BASIC and all4 original-source coordinate streams, including exact degenerate source primitives. Finite surface contacts and projected overlap diagnostics only; positive results require role/containment review. Nominated natives are either strictly separated or bound to completed full4world finite-contact evidence with exact unchanged native entries/assets; every raw native contact remains unapproved. Optional nominated support actors require separate binding/canonical checks; without a support record no actor is excluded except the source itself.')
    save(out/'summary.json',result);refs.extend([tool,HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']);module('model_only_foreign_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'model-only-complete-current-foreign-basic-contacts',list(dict.fromkeys(refs)),result);print(dict(foreignPairs=len(summary)),flush=True)

if __name__=='__main__':main()
