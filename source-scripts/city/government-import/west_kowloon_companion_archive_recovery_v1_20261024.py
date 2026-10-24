"""Recover missing prepared West Kowloon originals from existing local ZIPs."""
from pathlib import Path
import subprocess,zipfile
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-west-kowloon-bus-companion-archive-recovery-v1-20261024';out=base/batch;local=HERE/'local'/batch;assert not out.exists()and not local.exists()
    prior=base/'government-xl-next-repairs-west-kowloon-bus-foreign-original-discovery-v1-20261024';_,pins=authenticate(prior);p=prior/'source-families.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];family=read(p)['rows'];wanted=[r for r in family if not r['verifiedLocalOriginals']];refs=[Path(__file__),prior/'result.json',p]
    names=subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.zip','source-scripts/city'],cwd=ROOT,text=True).splitlines();matches={r['uid']:[]for r in wanted};bad=[]
    for name in names:
        path=ROOT/name
        try:
            with zipfile.ZipFile(path)as z:
                members=set(z.namelist())
                for r in wanted:
                    if r['model']['sourceEntry']in members:matches[r['uid']].append(name)
        except(zipfile.BadZipFile,OSError)as e:bad.append(dict(path=name,error=type(e).__name__))
    converter=module('west_companion_archive_converter',HERE/'xl-second-pass.py');rows=[]
    for r in wanted:
        m=r['model'];record=dict(uid=r['uid'],cacheKey=r['cacheKey'],nativeResultSHA256=r['resultSHA256'],expectedSHA256=m['asset']['sha256'],archiveNominations=matches[r['uid']],sourceRecovered=False)
        if matches[r['uid']]:
            archive=ROOT/matches[r['uid']][0];asha=digest(archive.read_bytes());folder=local/r['uid'].split('/')[1];(folder/'packed').mkdir(parents=True)
            with zipfile.ZipFile(archive)as z:recovered=converter._convert_one(z,z.getinfo(m['sourceEntry']),folder/'decoded',folder/'packed',{},dict(modelId=m['modelId']))
            generated=folder/'packed'/recovered['asset']['asset'];raw=converter.recovery.canonical_bytes(generated.read_bytes(),m['asset']['sha256']);assert digest(raw)==m['asset']['sha256']and len(raw)==m['asset']['bytes'];tri=decode_original_world_triangles(raw);assert len(tri)==m['triangles']
            dest=folder/(m['asset']['sha256']+'.glb.gz');dest.write_bytes(raw);assert digest(archive.read_bytes())==asha;refs.append(dest)
            record.update(sourceRecovered=True,asset=dict(path=str(dest.relative_to(ROOT)),sha256=digest(raw),bytes=len(raw),completeTriangles=len(tri)),archive=dict(path=str(archive.relative_to(ROOT)),sha256=asha,member=m['sourceEntry']),completeOriginalWorldBounds=[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()])
        rows.append(record);print(dict(uid=r['uid'],recovered=record['sourceRecovered'],archives=len(matches[r['uid']])),flush=True)
    result=dict(uids=[r['uid']for r in wanted],rows=rows,archivesExamined=len(names),unreadableArchives=bad,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,identityApproved=False,publication=False,scriptExternalAICalls=0,qualification='Archive members deterministically converted; recovery only when canonical complete asset matches pinned native result SHA256, byte count and face count. Missing archive files do not imply corrupt source; no identity, placement, assembly or publication approval.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['xl-second-pass.py','exact_packed_world_geometry_20261009.py']);module('west_companion_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-prepared-west-kowloon-companion-local-archive-recovery',refs,result)

if __name__=='__main__':main()
