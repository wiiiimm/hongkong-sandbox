"""Nominate exact same-parent government podium sources for floating XL towers.

Read-only discovery: recorded heights/footprints nominate; actual support remains unproved.
"""
from pathlib import Path
import subprocess
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-remaining-floating-podium-discovery-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)]
    recovery='government-xl-remaining-178-v3-identity-recovery-v1-20261023';receipt,pins=authenticate(base/recovery);refs.append(base/recovery/'result.json')
    p=base/recovery/'rows.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];rows=read(p);refs.append(p)
    sources={}
    for chunk in receipt['chunks']:
        name=chunk['runtimeBatch'];_,bound=authenticate(base/name);p=base/name/'selection.json.gz';assert digest(p.read_bytes())==bound[str(p.relative_to(ROOT))];refs.extend([base/name/'result.json',p]);sources.update({r['uid']:r for r in read(p)['rows']})
    selected=[r for r in rows if not r['identityReasons']and r['foundation']['status']=='captured'and r['foundation']['fullyBuriedTriangles']==0and r['foundation']['minimumGapM']>.1and sources[r['uid']]['source']['building'].get('structureType')=='Tower']
    parents={sources[r['uid']]['source']['building'].get('parent')for r in selected}-{None,''};forms={};tilehash={};manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);refs.append(manifestpath)
    expected=read(base/'government-xl-remaining-178-v3-current-scene-v1-20261023/selection.json')['manifestSHA256'];assert digest(manifestpath.read_bytes())==expected
    installed={}
    for url in manifest['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;refs.append(path)
        for m in read(path)['models']:installed[m['uid']]=dict(catalogue=url,entry=m)
    for tile in manifest['tiles']:
        path=ROOT/'3d-viewer'/tile['url'];matched=[f for f in read(path)['buildings']if f.get('parent')in parents and f.get('structureType')=='Podium']
        if matched:
            tilehash[str(path.relative_to(ROOT))]=digest(path.read_bytes());refs.append(path)
            for f in matched:assert f['uid']not in forms;forms[f['uid']]=dict(building=f,tile=tile['url'],tileSHA256=digest(path.read_bytes()))
    nominated=[]
    for r in selected:
        source=sources[r['uid']];f=source['source']['building'];baseheight=f.get('baseHeightHKPD')
        if not isinstance(baseheight,(float,int)):continue
        target=shapely.Polygon(f['rings'][0],f['rings'][1:])
        for uid,podium in forms.items():
            b=podium['building'];top=b.get('topHeightHKPD')
            if b.get('parent')!=f.get('parent')or not isinstance(top,(float,int))or abs(top-baseheight)>.5:continue
            poly=shapely.Polygon(b['rings'][0],b['rings'][1:]);overlap=target.intersection(poly).area
            if overlap<=0:continue
            nominated.append(dict(uid=r['uid'],supportUid=uid,source=source,supportForm=podium,recordedTowerBase=baseheight,recordedPodiumTop=top,recordedHeightDifferenceM=top-baseheight,towerFootprintAreaM2=target.area,podiumOverlapM2=overlap,towerFootprintCoverage=overlap/target.area if target.area else None,installedSupport=installed.get(uid),sourceCacheKey=source['native']['cacheKey']))
    wanted={r['supportUid']for r in nominated};prefixes={'B'+forms[u]['building']['buildingCSUID'][:10]+'02'for u in wanted};models=[]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for key,sheet,sha,m in db.execute("SELECT i.cache_key,i.sheet,r.result_sha,m FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models')m WHERE i.cache_key=ANY(%s) AND (m->'candidate'->>'uid'=ANY(%s) OR left(m->>'modelId',13)=ANY(%s))",(sorted({r['sourceCacheKey']for r in nominated}),sorted(wanted),sorted(prefixes))).fetchall():models.append(dict(cacheKey=key,sheet=sheet,resultSHA256=sha,model=m))
    paths=subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.glb.gz','source-scripts/city','3d-viewer/city/data'],cwd=ROOT,text=True).splitlines();lookup={}
    for name in paths:lookup.setdefault(Path(name).name.removesuffix('.glb.gz'),[]).append(name)
    for row in nominated:
        uid=row['supportUid'];csuid=forms[uid]['building']['buildingCSUID'];prefix='B'+csuid[:10]+'02'
        matches=[m for m in models if m['model'].get('candidate',{}).get('uid')==uid or m['model']['modelId'].startswith(prefix)]
        row['preparedOriginalMatches']=matches;row['verifiedLocalOriginalAssets']=[]
        for m in matches:
            asset=m['model'].get('asset',{});sha=asset.get('sha256')
            for name in lookup.get(sha,[]):
                path=ROOT/name
                if path.stat().st_size==asset['bytes']and digest(path.read_bytes())==sha:
                    row['verifiedLocalOriginalAssets'].append(dict(path=name,sha256=sha,modelId=m['model']['modelId']));refs.append(path);break
        row['supportApproved']=False
    assert digest(manifestpath.read_bytes())==expected
    save(out/'support-candidates.json.gz',nominated)
    result=dict(uids=sorted({r['uid']for r in nominated}),examinedCurrentSources=len(rows),floatingIdentityPassedTowerSources=len(selected),nominatedTowerSources=len({r['uid']for r in nominated}),nominatedPodiumSources=len(wanted),nominatedPairs=len(nominated),pairsWithInstalledSupport=sum(bool(r['installedSupport'])for r in nominated),pairsWithPreparedOriginalRecord=sum(bool(r['preparedOriginalMatches'])for r in nominated),pairsWithExactLocalOriginalAsset=sum(bool(r['verifiedLocalOriginalAssets'])for r in nominated),manifestSHA256=expected,currentFormTileHashes=tilehash,sourceGeometryChanges=0,installationApproved=False,publication=False,newlyInstalled=0,status='same-parent-podium-source-discovery',qualification='Same current parent, overlapping GIS footprints and recorded roof/base alignment within.5m only nominate support candidates. Prepared metadata/asset hashes are exact; uniqueness/actual rendered roof contact/full support/source identity/pose/current neighbours/browser remain unapproved. No new queue, source geometry edit or installation credit.')
    save(out/'summary.json',result);module('floating_podium_discovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'current-xl-same-parent-podium-support-discovery',refs,result);print({k:result[k]for k in ['floatingIdentityPassedTowerSources','nominatedTowerSources','nominatedPairs','pairsWithInstalledSupport','pairsWithPreparedOriginalRecord','pairsWithExactLocalOriginalAsset']},flush=True)

if __name__=='__main__':main()
