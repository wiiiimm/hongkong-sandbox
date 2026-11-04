"""Bind a completed exact cached-terrain diagnostic to the existing inset CLI schema."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',required=True);p.add_argument('--terrain-check',required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-')and '/'not in a.batch and not out.exists()
    original,pins=authenticate(base/a.terrain_check);refs=[Path(__file__),base/a.terrain_check/'result.json']
    for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    summary=read(base/a.terrain_check/'summary.json');binding=read(base/a.terrain_check/'native-terrain-binding.json')
    assert summary['terrainInstalled']is False and summary['installationApproved']is False
    paths=[r['path']for r in binding['sources']];assert paths and len(paths)==len(set(paths));rows=[]
    for uid in summary['uids']:
        modes=[r for r in summary['rows']if r['uid']==uid]
        assert len(modes)==4 and {r['mode']for r in modes}=={'original','literal','leftF32','balancedF32'}
        assert all(r['covered']==r['triangles']and r['buried']==0 and r['buriedUpward']==0 for r in modes)
        detail=read(base/a.terrain_check/(uid.split('/')[1]+'--literal.json'))
        rows.append(dict(uid=uid,sourceSHA256=summary['sourceSHA256ByUid'][uid],sourceTerrainPaths=paths,
                         originalTerrainFoundation=detail['foundation'],fourWorldDiagnostic=modes,
                         installationApproved=False))
    result=dict(uids=summary['uids'],rows=rows,currentManifestSHA256=summary['currentManifestSHA256'],
                exactCachedTerrainJobId=original['jobId'],sourceGeometryChanges=0,terrainGeometryChanges=0,
                physicalAcceptance=False,installationApproved=False,publication=False,
                qualification='Schema binding only: exact source-terrain paths and verbatim literal foundation exposed for existing guarded inset CLI. All four complete-zero-burial diagnostics retained. No current terrain, neighbour, source-role, browser or publication acceptance transferred.')
    save(out/'summary.json',result)
    module('cached_terrain_candidate_binding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-cached-original-terrain-existing-candidate-schema-binding',refs,result)


if __name__=='__main__':main()
