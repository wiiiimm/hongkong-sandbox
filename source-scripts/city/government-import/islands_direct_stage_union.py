"""Combine current private direct nominations before fresh browser acceptance.

No terrain, source geometry, review flags or publication changes. Every parent
was separately checked; the ordinary worker repeats all gates for this union.
"""
import argparse
import copy
from pathlib import Path
from islands_direct_stage import ROOT,HERE,read,save,sha,rel
from run import connect


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--source-batch',action='append',required=True);a=p.parse_args()
    assert 1<=len(a.source_batch)<=4
    assert all(b.startswith('government-islands-') and '/' not in b for b in [a.batch,*a.source_batch])
    doc=ROOT/'docs/astra-city/government-import'/a.batch;stage=HERE/'accepted'/a.batch
    assert not doc.exists() and not stage.exists()
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=sha(manifest_path)
    pins={rel(manifest_path):manifest_sha,rel(Path(__file__)):sha(Path(__file__))};rows={};models={};identities={};parents=[];catalogue=None
    def pin(path):
        path=Path(path);key=rel(path);h=sha(path);assert key not in pins or pins[key]==h;pins[key]=h
    for batch in a.source_batch:
        parent=ROOT/'docs/astra-city/government-import'/batch;private=HERE/'accepted'/batch
        proof=read(parent/'stage.json');selected=read(parent/'selection.json.gz');plan=read(private/'plan.json');cat=read(private/'catalogue.json')
        assert selected['manifestSHA256']==manifest_sha and not plan['topLevelTerrainPatches'] and all(not area['terrain']for area in plan['areas'])
        assert sha(private/'catalogue.json')==proof['catalogueSHA256'] and sha(private/'plan.json')==proof['planSHA256']
        for path,h in proof['inputHashes'].items():assert sha(ROOT/path)==h,path;pin(ROOT/path)
        by_row={r['uid']:r for r in selected['rows']};by_model={m['uid']:m for m in cat['models']}
        assert set(proof['uids'])==set(by_row)==set(by_model)
        metadata={k:v for k,v in cat.items()if k not in ('area','models','counts')}
        if catalogue is None:catalogue=metadata
        else:assert catalogue==metadata
        identity_path=ROOT/proof['identityEvidencePath'];ir={r['uid']:r for r in read(identity_path)['rows']};pin(identity_path)
        for uid in proof['uids']:
            assert uid not in rows
            row=copy.deepcopy(by_row[uid]);entry=copy.deepcopy(by_model[uid]);source=private/entry['asset']
            assert sha(source)==entry['sha256']==row['candidate']['entry']['sha256']
            assert all(entry[k] is False for k in ('publicationApproved','placementReviewed','sourceIdentityReviewed','identityReviewApproved'))
            assert not entry.get('supportDependencies') and not entry.get('retainedBasicSupportDependencies')
            if row.get('identityProof'):
                assert ir[uid]['passed'] and ir[uid]['proof']==row['identityProof'];identities[uid]=ir[uid]
            pin(source);rows[uid]=row;models[uid]=(entry,source)
        for path in (parent/'stage.json',parent/'selection.json.gz',private/'catalogue.json',private/'plan.json'):pin(path)
        parents.append({'path':rel(parent/'stage.json'),'sha256':sha(parent/'stage.json')})
    uids=sorted(rows);assert 0<len(uids)<=40
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        states=dict(db.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC',(uids,)))
    assert not any(s in ('held','source-unavailable','identity-unresolved','installed-verified')for s in states.values())
    catalogue.update(area='Unchanged island originals on installed terrain',models=[models[u][0]for u in uids],counts={'packedModels':len(uids)})
    for entry,source in models.values():
        target=stage/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());assert sha(target)==entry['sha256']
    save(stage/'catalogue.json',catalogue);save(stage/'catalogue-index.json',{'models':len(uids),'catalogues':['catalogue.json']})
    save(stage/'source-forms.json',[{**rows[u]['source']['building'],'tile':Path(rows[u]['source']['tile']).stem}for u in uids])
    save(doc/'selection.json.gz',{'batch':a.batch,'manifestSHA256':manifest_sha,'rows':[rows[u]for u in uids],'nominationOnly':True})
    identity_path=doc/'identity-evidence.json.gz';save(identity_path,{'rows':list(identities.values()),'sourceEvidence':parents,'publication':False});pin(identity_path)
    destination=f'city/data/official-models/{a.batch}/catalogue.json'
    save(stage/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':rel(stage/'catalogue.json'),'destination':destination,'terrain':[]}],'topLevelTerrainPatches':[]})
    save(stage/'browser-config.json',{'stage':rel(stage)+'/','doc':rel(doc)+'/','catalogueURL':destination,'terrain':[],'fitBox':True,'browserUids':uids,'failureTestUids':uids,'visibilitySupplementUids':[],'captureDirectionByModel':{u:[.2,4,.2]for u in uids},'viewQualification':'High oblique unchanged original views; no every-facade/as-built claim.'})
    save(doc/'stage.json',{'batch':a.batch,'uids':uids,'sources':len(uids),'inputHashes':pins,'identityEvidencePath':rel(identity_path),'catalogueSHA256':sha(stage/'catalogue.json'),'planSHA256':sha(stage/'plan.json'),'sourceGeometryChanges':0,'terrainChanges':0,'publication':False,'qualification':'Nomination union only; fresh ordinary metrics/browser/publisher/live checks remain mandatory.'})
    print({'privateOriginals':len(uids),'terrainChanges':0,'publication':False},flush=True)


if __name__=='__main__':main()
