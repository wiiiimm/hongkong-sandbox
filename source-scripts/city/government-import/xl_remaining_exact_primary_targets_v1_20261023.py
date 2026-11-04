"""Compare all186 remaining indexed originals with exact current target metadata."""
from pathlib import Path
from collections import Counter,defaultdict
import json
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from xl_primary_target_contract_v1_20261023 import compare_target


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-remaining-186-exact-primary-targets-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)];prior='government-xl-remaining-186-primary-metadata-v1-20261023';_,pins=authenticate(base/prior);refs.append(base/prior/'result.json')
    p=base/prior/'metadata.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);metadata=read(p);sources=metadata['rows'];wanted={r['uid']for r in sources if r['uid']is not None};assert len(sources)==len({r['sourceKey']for r in sources})==186 and len(wanted)==184
    spec='government-xl-island-industrial-typed-primary-routing-v2-20261023';_,bound=authenticate(base/spec);p=base/spec/'spec-binding.json';assert digest(p.read_bytes())==bound[str(p.relative_to(ROOT))];refs.extend([base/spec/'result.json',p]);specification=read(p)
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';raw=manifestpath.read_bytes();manifestsha=digest(raw);manifest=json.loads(raw);refs.append(manifestpath);current=defaultdict(list);tilehashes={};allforms=0
    for i,tile in enumerate(manifest['tiles']):
        p=ROOT/'3d-viewer'/tile['url'];blob=p.read_bytes();sha=digest(blob);tilehashes[str(p.relative_to(ROOT))]=sha;refs.append(p);forms=json.loads(blob)['buildings'];allforms+=len(forms)
        for form in forms:
            if form['uid']in wanted:current[form['uid']].append(dict(building=form,tile=str(p.relative_to(ROOT)),tileSHA256=sha))
        if i%50==0:print(dict(tiles=i,targetsFound=len(current)),flush=True)
    rows=[]
    for source in sources:
        matches=current[source['uid']]if source['uid']is not None else [];record=compare_target(source,matches[0]['building']if len(matches)==1 else None,source['footprintMatches']);record['currentFormMatches']=len(matches);record['currentSourceForms']=matches;record['currentManifestSHA256']=manifestsha
        if len(matches)>1:record['reasons']=[r for r in record['reasons']if r!='current-viewer-target-missing']+['current-viewer-target-ambiguous'];record['exactTargetMetadataQualified']=False
        record['nextAction']='Continue unchanged original asset/graph and physical/browser checks'if record['exactTargetMetadataQualified']else'Resolve exact recorded primary/target metadata differences before identity acceptance; no remodelling inferred'
        rows.append(record)
    assert digest(manifestpath.read_bytes())==manifestsha
    for path,sha in tilehashes.items():assert digest((ROOT/path).read_bytes())==sha
    reasons=Counter(reason for r in rows for reason in r['reasons']);groups=defaultdict(list)
    for row in rows:groups['exact-target-metadata'if not row['reasons']else' | '.join(sorted(row['reasons']))].append(dict(uid=row['uid'],sourceKey=row['sourceKey'],originalModelId=row['originalModelId']))
    result=dict(uids=sorted(wanted),sourceKeys=sorted(r['sourceKey']for r in sources),sourceModels=186,mappedViewerTargets=184,unmappedSourceModels=2,currentMapFormsScanned=allforms,currentManifestSHA256=manifestsha,exactTargetMetadataQualified=sum(r['exactTargetMetadataQualified']for r in rows),metadataInvestigationRequired=sum(not r['exactTargetMetadataQualified']for r in rows),officialObjectIdChanged=sum(r['officialObjectIdChanged']for r in rows),reasonCounts=dict(reasons),groupedSources=dict(groups),sourceIdentityAccepted=False,sourceGraphOrAssetBytesChecked=False,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0,permanentRejection=False,qualification='All186 exact indexed ModelIDs compared to current unique viewer UID/CSUID, official model subtype and cached official primary records from the authenticated23October snapshot. Exact CSUID/BuildingID/type/base/top and Active state required; rotated official OBJECTID is recorded separately, not treated as source corruption. Every current map tile was searched to establish target uniqueness. The complete186source-key scope includes184mappedviewerUIDs and2unmappedsourcekeys; neither unmapped source is deduplicated or discarded. No source geometry or root graph checked here, no support/placement/visual/publication approval, queue, skip or installation credit.')
    save(out/'target-comparisons.json.gz',dict(rows=rows,officialSubtypeSpecification=specification));save(out/'current-tile-hashes.json',tilehashes);save(out/'summary.json',result);refs.extend(HERE/n for n in ['xl_primary_target_contract_v1_20261023.py','test_xl_primary_target_contract_v1_20261023.py']);module('remaining_target_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'complete-remaining-xl-exact-current-primary-metadata-comparison',refs,result);print({k:result[k]for k in ['sourceModels','exactTargetMetadataQualified','metadataInvestigationRequired','officialObjectIdChanged','reasonCounts']},flush=True)

if __name__=='__main__':main()
