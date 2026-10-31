"""Trace native/source crossings to original facet pairs; diagnostic, never acceptance."""
import argparse
from collections import Counter
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def coordinate_deltas(original,represented):
    a=np.asarray(original,dtype='<f8');b=np.asarray(represented,dtype='<f8')
    assert a.shape==b.shape and a.ndim==3 and a.shape[1:]==(3,3) and len(a)>0
    assert np.isfinite(a).all()and np.isfinite(b).all()
    left=a.reshape(-1,3);right=b.reshape(-1,3);maximum=[];distinct=[]
    for axis in range(3):
        pairs=set(zip(map(float,left[:,axis]),map(float,right[:,axis])))
        # Exact repeated coordinate pairs have identical rational differences.
        maximum.append(str(max(abs(Fraction(x)-Fraction(y))for x,y in pairs)))
        distinct.append(len(pairs))
    return dict(completeIndexedVerticesCompared=len(left),exactMaximumAbsoluteCoordinateDeltaM=maximum,distinctCoordinatePairsByAxis=distinct)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','contacts','roles']:ap.add_argument('--'+key,required=True)
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert all(n.startswith('government-xl-')and'/'not in n for n in vars(a).values())and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,'selection.json.gz');sources={r['uid']:r for r in selection['rows']}
    attrs=take(a.attributes,'attributes.json.gz');assert attrs['startEndAllInputsVerified'];attrs={r['uid']:r for r in attrs['rows']}
    contacts=take(a.contacts,'summary.json');roles=take(a.roles,'summary.json')
    native={r['uid']:r for r in take(a.contacts,'native-input.json.gz')['rows']}
    native_attrs={r['uid']:r for r in take(a.contacts,'native-attributes.json.gz')['rows']}
    fields=dict(literal='completeLiteralWorldPosition',leftF32='completeExplicitLeftAssociatedFloat32WorldPosition',balancedF32='completeExplicitBalancedFloat32WorldPosition')
    result_rows=[]
    for pair in contacts['rows']:
        uid,nuid=pair['uid'],pair['nativeUid'];source=sources[uid];nr=native[nuid]
        assert source['sourceSHA256']==attrs[uid]['sourceSHA256']==pair['sourceSHA256']
        assert nr['entry']==pair['rawCurrentNativeEntry']and nr['entry']['sha256']==native_attrs[nuid]['sourceSHA256']==pair['nativeSHA256']
        worlds={};deltas={}
        for key,path,attr,sha in [(uid,ROOT/source['candidate']['path'],attrs[uid],pair['sourceSHA256']),(nuid,ROOT/nr['path'],native_attrs[nuid],pair['nativeSHA256'])]:
            assert digest(path.read_bytes())==sha;refs.append(path);tri=decode_original_world_triangles(path.read_bytes());ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
            worlds[key]={'original':tri};deltas[key]={}
            for mode,field in fields.items():
                represented=np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]
                deltas[key][mode]=coordinate_deltas(tri,represented);worlds[key][mode]=represented
        stem=uid.split('/')[1]+'--'+nuid.split('/')[1]+'--'
        original=take(a.roles,stem+'original.json.gz');by={(r['sourceFaceA'],r['sourceFaceB']):r for r in original};assert len(by)==len(original)
        rows=[]
        for mode in ['original',*fields]:
            raw=take(a.contacts,stem+mode+'.json.gz');classified=take(a.roles,stem+mode+'.json.gz')
            assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0 and len(raw['contacts'])==len(classified)
            assert all({k:v for k,v in c.items()if k!='contactRole'}==r for c,r in zip(classified,raw['contacts']))
            role=next(r for r in roles['rows']if r['uid']==uid and r['nativeUid']==nuid and r['mode']==mode)
            assert role['sourceSHA256']==pair['sourceSHA256']and role['nativeSHA256']==pair['nativeSHA256']
            assert role['sourceWorldSHA256']==digest(worlds[uid][mode].astype('<f8').tobytes())and role['nativeWorldSHA256']==digest(worlds[nuid][mode].astype('<f8').tobytes())
            mode_summary=next(r for r in pair['modes']if r['mode']==mode)
            assert len(worlds[uid][mode])==mode_summary['sourceFaces']and len(worlds[nuid][mode])==mode_summary['nativeFaces']
            records=[]
            for c in classified:
                if c['contactRole']!='transverse-surface-crossing':continue
                old=by.get((c['sourceFaceA'],c['sourceFaceB']))
                records.append(dict(representedContact=c,originalPairContact=old,originalPairRole=old['contactRole']if old else None,physicalAcceptance=False))
            row=dict(mode=mode,transverseSegments=len(records),allRepresentedCrossingsHaveOriginalFacetPairContacts=all(r['originalPairContact']is not None for r in records),originalRoleCounts=dict(Counter(r['originalPairRole']for r in records)),rows=records)
            save(out/(stem+mode+'.json.gz'),row);rows.append({k:v for k,v in row.items()if k!='rows'});print(rows[-1],flush=True)
        result_rows.append(dict(uid=uid,nativeUid=nuid,sourceSHA256=pair['sourceSHA256'],nativeSHA256=pair['nativeSHA256'],completeCorrespondingVertexDeltas=deltas,modes=rows))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==pins[a.contacts][str(manifest.relative_to(ROOT))];refs.append(manifest)
    result=dict(uids=contacts['uids'],rows=result_rows,currentManifestSHA256=selection['manifestSHA256'],sourceGeometryChanges=0,nativeMetadataChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Every represented crossing retains its complete raw contact and exact original facet-pair correspondence. Exact rational coordinate deltas compare ALL indexed vertices; deduplication only avoids repeating identical coordinate pairs. Original point/edge/crossing contact is not architectural intent or collision approval. New facet-pair crossings remain explicitly unproven. No tolerance, geometry change, engineering support or acceptance inferred.')
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('native_lineage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-native-source-represented-contact-original-facet-lineage',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
