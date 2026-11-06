"""Nominate disjoint unchanged Cheung terrain follow-ups; no acceptance."""
import copy
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import box
from islands_direct_stage import ROOT,HERE,read,save,sha,rel,module
from run import connect

BATCH=DOC=None


def main():
    assert not DOC.exists()
    base=ROOT/'docs/astra-city/government-import'
    context_paths=[base/f'government-islands-cheung-chau-context-{i}-20261106-v2/context.json.gz' for i in range(4)]
    identity_paths=[base/f'government-islands-cheung-chau-identity-{part}-20261106-v1/identities.json.gz' for part in ('part3','rest','terrain-0','terrain-1')]
    pins={};contexts={};identities={};terrain_errors={};refs=[]
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for path in context_paths+identity_paths:
            sync=read(path.parent/'neon-sync.json');assert sync['exactResultMatch']
            expected={'path':rel(path),'sha256':sha(path)}
            assert db.execute("SELECT result->'evidence' FROM astra_modelling.jobs WHERE id=%s AND status='complete'",(sync['jobId'],)).fetchone()[0]==expected
            data=read(path); target=contexts if path in context_paths else identities
            for row in data['rows']:
                assert row['uid'] not in target;target[row['uid']]=row
            terrain_errors.update(data.get('terrainValidationExceptions',{}))
            refs.append({**expected,'jobId':sync['jobId']});pins[rel(path)]=sha(path)
            for p,h in data['inputHashes'].items():
                if p=='3d-viewer/city/data/manifest.json':continue
                assert sha(ROOT/p)==h,p
    source_path=base/'government-islands-cheung-chau-source-terrain-20261106-v1/check-selection.json.gz'
    source={r['uid']:r for r in read(source_path)['rows']};pins[rel(source_path)]=sha(source_path)
    eligible=[]
    for uid,c in contexts.items():
        strict=not c['diagnosticReasons']
        full_cell=set(c['diagnosticReasons'])=={'strict-identity-fit'} and identities.get(uid,{}).get('passed')
        if not (strict or full_cell):continue
        row=copy.deepcopy(source[uid]);assert row['candidate']['entry']['sha256']==c['sourceSHA256']
        if full_cell:
            assert identities[uid]['context']['sourceSHA256']==c['sourceSHA256']
            row['identityProof']=identities[uid]['proof']
        eligible.append(row)
    assert len(eligible)==672
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=sha(manifest_path);manifest=read(manifest_path)
    installed={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        states=dict(db.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC',([r['uid']for r in eligible],)))
    old=module('cheung_disjoint_existing',HERE/'tai-o-terrain-pass.py');parent=read(ROOT/'3d-viewer/city/data/terrain.json')
    patches=[read(ROOT/'3d-viewer'/p['url']) for p in manifest['terrainPatches']]
    bounds=np.asarray([r['candidate']['entry']['worldBounds'] for r in eligible]);extent=[bounds[:,:,0].min()-100,bounds[:,:,2].min()-100,bounds[:,:,0].max()+100,bounds[:,:,2].max()+100]
    final=module('cheung_disjoint_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms(extent);tree=shapely.STRtree([poly for _,poly,_ in forms])
    previous=[base/'government-islands-cheung-chau-disjoint-terrain-20261106-v1/nomination.json',*sorted(base.glob('government-islands-cheung-chau-sweep-*-20261106-v1/nomination.json'))]
    tried=set()
    for path in previous:
        tried.update(read(path)['uids']);pins[rel(path)]=sha(path)
    nominees=[];excluded=[]
    for row in eligible:
        uid=row['uid']
        if uid in tried:
            excluded.append({'uid':uid,'reason':'prior-TIN-attempt-retained'});continue
        if uid in installed or states.get(uid) in ('held','source-unavailable','identity-unresolved','installed-verified'):
            excluded.append({'uid':uid,'reason':'existing-installation-or-review','state':states.get(uid)});continue
        cells=old.resolve.rectangle_for(row['candidate']['entry']['worldBounds'],parent)
        if any(old.terrain_helpers.overlap(cells,p['coarseCells']) for p in patches):
            excluded.append({'uid':uid,'reason':'retain-installed-terrain'});continue
        domain=old.resolve.extent(cells,parent);neighbours=len(tree.query(box(*domain)))
        nominees.append((neighbours,uid,cells,row))
    chosen=[]
    for n,uid,cells,row in sorted(nominees,key=lambda r:(r[0],r[1])):
        if any(old.terrain_helpers.overlap(cells,c['cells']) for c in chosen):continue
        chosen.append({'uid':uid,'cells':cells,'affectedFootprintNominations':n,'row':row})
        if len(chosen)==50:break
    assert sha(manifest_path)==manifest_sha
    save(DOC/'nomination.json',{'uids':[r['uid']for r in chosen],'domains':[{k:v for k,v in r.items()if k!='row'}for r in chosen],
        'rows':[r['row']for r in chosen],'manifestSHA256':manifest_sha,'eligibleNominationPool':len(eligible),
        'excluded':excluded,'inputHashes':pins,'publication':False,'qualification':'Historical diagnostics nominate only; fresh source-TIN/contact/current-neighbour/runtime/browser/publication checks remain mandatory.'})
    save(DOC/'context-evidence.json.gz',{'rows':list(contexts.values()),'terrainValidationExceptions':terrain_errors,'sourceEvidence':refs,'publication':False})
    save(DOC/'identity-evidence.json.gz',{'rows':list(identities.values()),'sourceEvidence':refs,'qualification':'Replay-only original identity aggregate, no physical approval'})
    print({'sourceTINNominees':len(eligible),'disjointFirstWave':len(chosen),'reviewOrTerrainExclusions':len(excluded),'publication':False},flush=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch',required=True);args=parser.parse_args()
    assert args.batch.startswith('government-islands-cheung-chau-sweep-') and '/' not in args.batch
    BATCH=args.batch;DOC=ROOT/'docs/astra-city/government-import'/BATCH
    main()
