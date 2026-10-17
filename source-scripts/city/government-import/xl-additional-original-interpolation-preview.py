"""Diagnose additional interpolation of original DTM alongside original TIN.

Reads the explicitly completed 113-mesh DTM receipt, skips installed meshes,
and requires unchanged source bytes, geometry and pose inputs. Changed terrain
context is recorded; these are historical diagnostics, never fresh acceptance.
Highest-facet TIN results are separate from mixed pointwise feasibility.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import numpy as np
from run import ROOT, read, save, digest
from terrain_source_preflight import SourceSheetIndex
from original_tin_point_diagnostic import indexed_surface, point_heights

DIR = ROOT/'source-scripts/city/government-import'
BASE = ROOT/'docs/astra-city/government-import'

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,DIR/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--receipt',required=True);a=p.parse_args()
    assert a.batch.startswith('government-xl-') and Path(a.batch).name==a.batch
    doc=BASE/a.batch;local=DIR/'local'/a.batch;assert not doc.exists()
    refs={}; memo={}
    def pinned(path):
        if path not in memo:
            refs[str(path.relative_to(ROOT))]=digest(path.read_bytes());memo[path]=read(path)
        return memo[path]
    receipt_path=(ROOT/a.receipt).resolve();assert receipt_path.is_relative_to(BASE);old=pinned(receipt_path)
    assert old['diagnosticOnly'] and not old['publication'] and old['exactProductionGeometryInputsVerified'] and 0<len(old['rows'])<=113
    assert digest((ROOT/old['source']['path']).read_bytes())==old['source']['sha256']
    manifest=pinned(ROOT/'3d-viewer/city/data/manifest.json')
    installed={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    root=pinned(ROOT/'3d-viewer/city/data/terrain.json')
    index=SourceSheetIndex(pinned(ROOT/'source-scripts/city/landmark-acquisition/index.json'))
    dtm=module('wide_original_dtm','xl-original-dtm-contact-preview.py');parent=module('wide_original_root','xl-three-original-surfaces-preview.py');cacheproof=module('wide_receipt','xl-cell-indexed-terrain-continuation.py');decoder=module('wide_decoder','xl-second-pass.py');decoder.LOCAL=local
    cache={};out=[];skipped=[]
    for prior in old['rows']:
        uid=prior['uid']
        if uid in installed:continue
        geompath=ROOT/prior['geometry']['path'];data=pinned(geompath);assert refs[str(geompath.relative_to(ROOT))]==prior['geometry']['sha256']
        model=next(r for r in data['rows'] if r['uid']==uid);assert model['sourceSHA256']==prior['sourceSHA256']
        selection=pinned(BASE/prior['priorBatch']/'selection.json.gz');source=next(r for r in selection['rows'] if r['uid']==uid)
        assert source['sourceSHA256']==model['sourceSHA256']==digest((ROOT/source['candidate']['path']).read_bytes())
        changed=[];unsafe=[]
        for path,sha in data['inputHashes'].items():
            current=digest((ROOT/path).read_bytes())
            if current!=sha:
                entry={'path':path,'historicalSHA256':sha,'currentSHA256':current}
                if path=='3d-viewer/city/data/manifest.json' or path.startswith('3d-viewer/city/data/terrain') or path.startswith('3d-viewer/city/data/government-native-'):
                    changed.append(entry)
                else:unsafe.append(entry)
        if unsafe:
            skipped.append({'uid':uid,'reason':'changed-nonterrain-runtime-input','changed':unsafe});continue
        verts=np.asarray(model['position']).reshape(-1,3);faces=verts[np.asarray(model['index']).reshape(-1,3)];bottom=float(verts[:,1].min());pts=[verts,faces.mean(axis=1)];edges=[]
        for face in faces:
            for k in range(3):
                x,y=face[k],face[(k+1)%3]
                if max(x[1],y[1])>bottom+.35:continue
                n=math.ceil(np.linalg.norm((x-y)[[0,2]]));edges.extend(x+(y-x)*j/n for j in range(1,n))
        if edges:pts.append(np.array(edges))
        points=np.concatenate(pts);low=points[:,1]<=bottom+.35
        gridpath=ROOT/prior['grid']['path'];assert digest(gridpath.read_bytes())==prior['grid']['sha256'];grid=pinned(gridpath)
        gap=points[:,1]-dtm.heights(points,np.asarray(grid['heights']),grid['bounds']);rootgap=points[:,1]-parent.parent_heights(points,root)
        valid=lambda g:(g>=-.5)&(~low|(g<=1))
        coords=dtm.grid_coordinates(points);cell=np.floor(coords).astype(int)
        u,v=(coords-cell).T;c,r=(cell-np.array(grid['bounds'][:2])).T
        values=np.asarray(grid['heights']);aa,bb,dd,ee=values[r,c],values[r,c+1],values[r+1,c],values[r+1,c+1]
        assert np.isfinite(np.stack([aa,bb,dd,ee])).all() and min(aa.min(),bb.min(),dd.min(),ee.min())>-9999
        alternate=np.where(v<=u,aa+(bb-aa)*u+(ee-bb)*v,aa+(ee-dd)*u+(dd-aa)*v)
        bilinear=aa*(1-u)*(1-v)+bb*u*(1-v)+dd*(1-u)*v+ee*u*v
        alternate_gap=points[:,1]-alternate;bilinear_gap=points[:,1]-bilinear
        original_possible=valid(gap)|valid(rootgap)
        original_contact=((valid(gap)&(gap<=.1))|(valid(rootgap)&(rootgap<=.1)))&low
        possible=original_possible|valid(alternate_gap)|valid(bilinear_gap)
        contact=original_contact|(((valid(alternate_gap)&(alternate_gap<=.1))|(valid(bilinear_gap)&(bilinear_gap<=.1)))&low)
        highest=np.full(len(points),-np.inf);anytin=np.zeros(len(points),bool);anycontact=np.zeros(len(points),bool);missing=[];receipts=[]
        sheets={source['native']['sheet'],*(r['sheet'] for r in index.covering_sheets([verts.min(axis=0).tolist(),verts.max(axis=0).tolist()]))}
        for sheet in sorted(sheets):
            if sheet not in cache:
                audit=next((p for p in [DIR/'local/government-xl-adjoining-current-terrain-directory-audit-20261007/sheets'/sheet/'directory/result.json', DIR/'local/government-xl-held-current-directory-audit-20261007/sheets'/sheet/'directory/result.json'] if p.exists()), DIR/'local/government-xl-held-current-directory-audit-20261007/sheets'/sheet/'directory/result.json')
                matched=None
                if audit.exists():
                    current=pinned(audit)
                    for folder in sorted((DIR/'local').glob('*/sheets/'+sheet)):
                        proof=cacheproof.verified_terrain(folder)
                        if proof and proof[0]['directorySHA256']==current['directorySHA256']:matched=(folder,proof);break
                if matched:
                    folder,(receipt,files)=matched;pieces=[]
                    for f in files:
                        path=folder/'terrain'/f['name'];refs[str(path.relative_to(ROOT))]=f['sha256']
                        if path.suffix=='.gltf':pieces.append(decoder.terrain_triangles(path))
                    pinned(folder/'original/download.json')
                    cache[sheet]=(indexed_surface(np.concatenate(pieces)),{'sheet':sheet,'directorySHA256':receipt['directorySHA256'],'cache':str(folder.relative_to(ROOT))})
                else:cache[sheet]=None
            if cache[sheet] is None:missing.append(sheet);continue
            surface,receipt=cache[sheet];receipts.append(receipt);si,heights,top=point_heights(points,surface);highest=np.maximum(highest,top)
            g=points[si,1]-heights;ok=(g>=-.5)&(~low[si]|(g<=1));np.logical_or.at(anytin,si,ok);np.logical_or.at(anycontact,si,ok&(g<=.1)&low[si])
        tin_gap=points[:,1]-highest;topvalid=valid(tin_gap)&np.isfinite(highest)
        mixed=possible|anytin;contacts=contact|anycontact
        old_mixed=original_possible|anytin;old_contacts=original_contact|anycontact
        row={'uid':uid,'sourceSHA256':model['sourceSHA256'],'priorBatch':prior['priorBatch'],'checks':len(points),'lowChecks':int(low.sum()),'unavailableCurrentTerrainSheets':missing,'terrainReceipts':receipts,'historicalTerrainChanges':changed,'highestOriginalTINUnresolved':int((~topvalid).sum()),'highestOriginalTINPositive':bool(topvalid.all() and (topvalid&low&(tin_gap<=.1)).any() and not missing),'mixedOriginalPointwiseUnresolved':int((~mixed).sum()),'mixedOriginalPointwisePositive':bool(mixed.all() and contacts.any() and not missing),
             'previousSurfaceBankPointwisePositive':bool(old_mixed.all() and old_contacts.any() and not missing),
             'newlyPositiveByAdditionalInterpolation':bool(mixed.all() and contacts.any() and not missing and not(old_mixed.all() and old_contacts.any())),
             'bilinearDTMOnlyPositive':bool(valid(bilinear_gap).all() and (valid(bilinear_gap)&low&(bilinear_gap<=.1)).any()),
             'alternateDTMOnlyPositive':bool(valid(alternate_gap).all() and (valid(alternate_gap)&low&(alternate_gap<=.1)).any()),
             'additionalOriginalInterpolationResolvableSamples':int(((~old_mixed)&mixed).sum())}
        out.append(row);print(json.dumps({k:row[k] for k in ['uid','highestOriginalTINPositive','mixedOriginalPointwisePositive','newlyPositiveByAdditionalInterpolation','additionalOriginalInterpolationResolvableSamples','unavailableCurrentTerrainSheets']}),flush=True)
    for path,sha in refs.items():assert digest((ROOT/path).read_bytes())==sha
    for name in [Path(__file__).name,'original_tin_point_diagnostic.py','test_original_tin_point_diagnostic.py']:refs[str((DIR/name).relative_to(ROOT))]=digest((DIR/name).read_bytes())
    result={'rows':out,'skipped':skipped,'inputHashes':refs,'diagnosticOnly':True,'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'qualification':'Previously decoded exact unchanged original meshes with current loader/pose hashes, refreshed adjoining original TIN directory/file receipts, all vertices/face centers/<=1m low edges. Additional original DTM bilinear and alternate-cell-diagonal interpolation, with unchanged surveyed nodes. Highest-facet and mixed pointwise results remain necessary-condition diagnostics, not coherent actual terrain or acceptance; every fresh identity, coherent terrain, foundation, native/basic neighbor and browser gate remains required.'}
    save(doc/'result.json',result)
    print(json.dumps({'models':len(out),'skipped':len(skipped),'highestTINPositives':[r['uid'] for r in out if r['highestOriginalTINPositive']],'mixedPositives':[r['uid'] for r in out if r['mixedOriginalPointwisePositive']],'newInterpolationPositives':[r['uid'] for r in out if r['newlyPositiveByAdditionalInterpolation']], 'bilinearOnlyPositives':[r['uid'] for r in out if r['bilinearDTMOnlyPositive']]}),flush=True)

if __name__=='__main__':main()
