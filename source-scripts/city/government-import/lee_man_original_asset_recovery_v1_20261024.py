"""Recover the exact prepared Lee & Man asset from an existing government archive."""
from pathlib import Path
import zipfile
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-lee-man-original-asset-recovery-v1-20261024';out=base/batch;local=HERE/'local'/batch;assert not out.exists()and not local.exists();refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    family='government-xl-next-repairs-sung-fung-lee-man-original-family-discovery-v1-20261024';discovery='government-xl-next-repairs-lee-man-missing-original-files-v1-20261024';r=next(r for r in take(family,base/family/'source-families.json.gz')['rows']if r['uid']=='landsd/47160:0');found=take(discovery,base/discovery/'discovery.json.gz');assert len(found)==1 and found[0]['uid']==r['uid'];nominations=found[0]['unapprovedArchiveMembers'];assert len(nominations)==1
    nomination=nominations[0];archive=Path(nomination['archivePath']);assert archive.is_relative_to(ROOT)and archive.exists();m=r['model'];assert nomination['member']==m['sourceEntry'];local.mkdir(parents=True)
    tools=module('lee_man_original_converter',HERE/'xl-second-pass.py')
    archive_sha=digest(archive.read_bytes())
    with zipfile.ZipFile(archive)as z:
        recovered=tools._convert_one(z,z.getinfo(m['sourceEntry']),local/'decoded',local/'packed',{},dict(modelId=m['modelId']))
    generated=local/'packed'/recovered['asset']['asset'];raw=tools.recovery.canonical_bytes(generated.read_bytes(),m['asset']['sha256']);assert digest(raw)==m['asset']['sha256']and len(raw)==m['asset']['bytes']
    destination=local/'assets'/(m['asset']['sha256']+'.glb.gz');destination.parent.mkdir();destination.write_bytes(raw);tri=decode_original_world_triangles(raw);assert len(tri)==m['triangles'];assert digest(archive.read_bytes())==archive_sha
    refs.extend([destination,HERE/'xl-second-pass.py',HERE.parent/'citywide-native/convert.py',HERE.parent/'enhancement-screening/shape_prepare.py',HERE/'exact_packed_world_geometry_20261009.py'])
    result=dict(uids=[r['uid']],sourceRecovered=True,asset=dict(path=str(destination.relative_to(ROOT)),sha256=digest(raw),bytes=len(raw)),cacheKey=r['cacheKey'],nativeResultSHA256=r['resultSHA256'],originalTriangles=len(tri),originalWorldBounds=[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()],archive=dict(path=str(archive.relative_to(ROOT)),sha256=archive_sha,member=m['sourceEntry']),sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,identityApproved=False,publication=False,scriptExternalAICalls=0,qualification='Existing local archive deterministically converted and canonical compressed output matches exact prepared government asset SHA256/bytes and original face count. Archive nomination alone grants no approval; final exact asset hash anchors recovery to the pinned prepared result.')
    save(out/'summary.json',result);module('lee_man_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-prepared-lee-man-original-recovered-from-local-archive',refs,result);print({k:result[k]for k in ['sourceRecovered','asset','originalTriangles']},flush=True)


if __name__=='__main__':main()
