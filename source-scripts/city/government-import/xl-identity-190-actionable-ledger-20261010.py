"""Separate fixed source identity investigation from actual installation.

This is a read-only evidence ledger, not a queue or new acceptance decision.
Every status uses the exact original UID/model/source hash. All cases had the
initial provider search and spatial ranking; 'unstarted' means deeper semantic
component investigation only, never that no scripts/search were performed.
"""
from collections import Counter
from run import ROOT,read,save,digest
BASE=ROOT/'docs/astra-city/government-import'
DOC=BASE/'government-xl-identity-190-actionable-ledger-20261010'
DEEP_PREFIXES=('government-xl-science-','government-xl-two-harbourfront-',
 'government-xl-tung-sing-','government-xl-yoho-','government-xl-miami-',
 'government-xl-popcorn-','government-xl-source-format-comparison-',
 'government-xl-southside-','government-xl-tuen-mun-')
def main():
    assert not (DOC/'result.json').exists();input=BASE/'government-xl-identity-search-20261009/actionable-dispositions.json.gz';ranking=BASE/'government-xl-identity-primary-spatial-ranking-20261009/ranking.json.gz';prior=BASE/'government-xl-identity-search-20261009/current-positive-proof-bindings.json.gz'
    initial=read(input)['rows'];assert len(initial)==190 and len({r['sourceKey'] for r in initial})==190
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());pins={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [input,ranking,prior,manifest]};installed={}
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;pins[str(path.relative_to(ROOT))]=digest(path.read_bytes())
        for row in read(path)['models']:
            if row.get('placementReviewed') is True:installed[(row['uid'],row['modelId'],row['sha256'])]={'catalogue':str(path.relative_to(ROOT)),'sha256':pins[str(path.relative_to(ROOT))]}
    lookup={(r['uid'],r['modelId'],r['sourceSHA256']):r['sourceKey'] for r in initial};evidence={k:[] for k in lookup.values()}
    for row in read(prior)['rows']:
        key=(row['uid'],row['modelId'],row['sourceSHA256'])
        if key in lookup:
            ref=row['proofRef'];assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'];pins[ref['path']]=ref['sha256'];evidence[lookup[key]].append({'kind':'identity-cleared-historical-context','jobId':row['parentJobId'],'proofRef':ref,'reason':'complete previous exact-source identity proof; full current physical/runtime remain independent','currentManifestBound':False})
    for folder in sorted(BASE.iterdir()):
        if not folder.is_dir() or not folder.name.startswith(DEEP_PREFIXES):continue
        resultpath=folder/'result.json';selectionpath=folder/'selection.json.gz'
        if not resultpath.exists() or not selectionpath.exists():continue
        result=read(resultpath);selection=read(selectionpath);rows=selection.get('rows',[]) if isinstance(selection,dict) else selection
        if not isinstance(rows,list):continue
        status={r.get('uid'):bool(r.get('passed')) for r in result.get('rows',[]) if isinstance(r,dict) and 'passed' in r}
        accepteduids=set(result.get('uids',[])) if result.get('identityAccepted') is True else set()
        for row in rows:
            key=(row.get('uid'),row.get('modelId'),row.get('sourceSHA256'))
            if key not in lookup:continue
            for p in [resultpath,selectionpath]:pins[str(p.relative_to(ROOT))]=digest(p.read_bytes())
            passed=row.get('uid') in accepteduids or status.get(row.get('uid')) is True
            evidence[lookup[key]].append({'kind':'identity-cleared' if passed else 'deep-investigation-completed',
                'jobId':result.get('jobId'),'resultRef':{'path':str(resultpath.relative_to(ROOT)),'sha256':digest(resultpath.read_bytes())},
                'selectionRef':{'path':str(selectionpath.relative_to(ROOT)),'sha256':digest(selectionpath.read_bytes())},
                'reason':result.get('remainingReason') or result.get('nextStep') or 'complete source-specific investigation receipt',
                'currentManifestBound':selection.get('manifestSHA256')==mh if isinstance(selection,dict) else False})
    rank={r['sourceKey']:r for r in read(ranking)['rows']};output=[]
    for row in initial:
        key=(row['uid'],row['modelId'],row['sourceSHA256']);proofs=evidence[row['sourceKey']];cleared=any(p['kind'].startswith('identity-cleared') for p in proofs)
        state='installed-exact-source' if key in installed else ('identity-cleared-physical-pending' if cleared else ('deep-investigated-held' if proofs or row['identityState'] in ['provider-source-classification-mismatch','provider-source-gis-lineage-unresolved'] else 'deeper-component-investigation-to-do'))
        output.append({k:row[k] for k in ['uid','modelId','sourceKey','sourceSHA256','name','identityState']}|{
            'ledgerState':state,'initialPrimaryLookupAndSpatialRankingDone':True,
            'originalHistoricalReasons':row['historicalReasons'],'evidence':proofs,
            'installed':key in installed,'installationEvidence':installed.get(key),
            'currentBoundIdentityProof':any(p['kind'].startswith('identity-cleared') and p['currentManifestBound'] for p in proofs),
            'physicalAcceptanceInferredFromIdentity':False,'liveWorkerStateClaimed':False,
            'nextStep':('done for exact original source' if key in installed else ('fresh current context and complete physical/support/runtime acceptance' if cleared else row['nextStep'])),
            'rank':rank[row['sourceKey']]['diagnosticRank'],'rankedMeasuresHistorical':rank[row['sourceKey']].get('measures'),
            'rankedForeignActorsHistorical':rank[row['sourceKey']].get('foreignActors',[]),'requiresAIModelGeometry':False,'permanentRejection':False})
    shortlist=[]
    for item in sorted(output,key=lambda r:r['rank']):
        if item['ledgerState']!='deeper-component-investigation-to-do':continue
        metrics=item['rankedMeasuresHistorical'] or {}
        if metrics.get('targetCoverage',0)<.95 or metrics.get('maximumSourceExtentM',100)>10:continue
        shortlist.append({'uid':item['uid'],'modelId':item['modelId'],'sourceKey':item['sourceKey'],'sourceSHA256':item['sourceSHA256'],'name':rank[item['sourceKey']].get('primaryAttributes',{}).get('BuildingNameEN') or item['name'],'rank':item['rank'],'historicalMeasures':metrics,'foreignActors':item['rankedForeignActorsHistorical'],'nextStep':'fresh exact provider/current forms and complete original offending-face ownership; retrieve only exact counterpart originals, preserve all other actors and physical gates'})
        if len(shortlist)==8:break
    assert digest(manifest.read_bytes())==mh
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
    counts=dict(Counter(r['ledgerState'] for r in output));save(DOC/'ledger.json.gz',{'rows':output,'counts':counts,'totalExactOriginalSources':190,'manifestSHA256':mh,'inputHashes':pins,'shortlist':shortlist,'queueCreated':False,'newAcceptance':False,'qualification':'Fixed original190 source-version ledger. All190 previously received provider searches and complete spatial ranking. Deeper-to-do excludes completed source-specific receipts; identities cleared historically still require fresh current bound physical acceptance. Neither source identifier presence nor a completed compute job implies installation.'});print(counts,flush=True)
    text='# Fixed 190 government identity cases\n\nThis ledger binds the original 190 exact source versions to the current catalogue and completed source-specific evidence. Every case has already had provider lookup and spatial ranking; to-do means deeper component interpretation.\n\n'
    text+='\n'.join('- '+k+': '+str(v) for k,v in counts.items())+'\n\nIdentity clearance does not certify physical installation. Historical proofs need a fresh current context; no missing sources are permanently rejected.\n\nNext source investigations:\n\n'
    text+='\n'.join('- '+str(r['uid'])+' — '+str(r['name'])+'; foreign excess '+str(round(r['historicalMeasures']['unrelatedExcessOverlapM2'],3))+' m² across '+str(len(r['foreignActors']))+' actors.' for r in shortlist)+'\n'
    (DOC/'README.md').write_text(text)
if __name__=='__main__':main()
