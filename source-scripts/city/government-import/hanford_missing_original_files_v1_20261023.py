"""Find exact missing original assets or source members; no source approval transfer."""
from pathlib import Path
import subprocess
import shutil
import zipfile
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';prior='government-xl-next-repairs-hanford-original-family-discovery-v2-20261023';batch='government-xl-next-repairs-hanford-missing-original-files-v1-20261023';out=base/batch;local=HERE/'local'/batch;assert not out.exists()and not local.exists()
    _,pins=authenticate(base/prior);path=base/prior/'source-families.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];rows=[r for r in read(path)['rows']if not r['verifiedLocalOriginals']];assert len(rows)==7
    shared=ROOT.parents[2];assert shared.name=='hongkong-sandbox'
    names=subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.glb.gz','-g','*.gltf','-g','*.zip',str(shared)],cwd=ROOT,text=True).splitlines();assets={};gltfs={};archives=[]
    for name in names:
        p=Path(name)
        if name.endswith('.glb.gz'):assets.setdefault(p.name.removesuffix('.glb.gz'),[]).append(p)
        elif name.endswith('.gltf'):gltfs.setdefault(p.name,[]).append(p)
        elif name.endswith('.zip'):archives.append(p)
    refs=[Path(__file__),base/prior/'result.json',path];results=[];wanted={r['model']['modelId']+'.gltf'for r in rows};archivehits={k:[]for k in wanted}
    for archive in dict.fromkeys(archives):
        try:
            with zipfile.ZipFile(archive)as z:
                for member in z.namelist():
                    if Path(member).name in wanted:archivehits[Path(member).name].append(dict(archivePath=str(archive),member=member))
        except (OSError,zipfile.BadZipFile):continue
    for row in rows:
        m=row['model'];asset=m['asset'];verified=[]
        for p in assets.get(asset['sha256'],[]):
            if p.stat().st_size==asset['bytes']and digest(p.read_bytes())==asset['sha256']:
                dest=local/'assets'/(asset['sha256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);assert digest(dest.read_bytes())==asset['sha256'];refs.append(dest);verified=[dict(path=str(dest.relative_to(ROOT)),sha256=asset['sha256'],copiedFrom=str(p))];break
        results.append(dict(uid=row['uid'],modelId=m['modelId'],expectedAssetSHA256=asset['sha256'],cacheKey=row['cacheKey'],resultSHA256=row['resultSHA256'],verifiedExactOriginalAssets=verified,unapprovedRawGLTFPaths=[str(p)for p in gltfs.get(m['modelId']+'.gltf',[])],unapprovedArchiveMembers=archivehits[m['modelId']+'.gltf'],qualification='Raw files/members are nominations only until pinned archive provenance and deterministic output are verified.',installationApproved=False))
    save(out/'discovery.json.gz',results);result=dict(uids=[r['uid']for r in results],requestedOriginals=7,exactAssetsRecovered=sum(bool(r['verifiedExactOriginalAssets'])for r in results),withRawSourceNomination=sum(bool(r['unapprovedRawGLTFPaths']or r['unapprovedArchiveMembers'])for r in results),archiveInventoriesExamined=len(archives),sourceGeometryChanges=0,installationApproved=False,publication=False)
    save(out/'summary.json',result);module('hanford_missing_files_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-missing-original-asset-and-raw-source-discovery',refs,result);print(result,flush=True)


if __name__=='__main__':main()
