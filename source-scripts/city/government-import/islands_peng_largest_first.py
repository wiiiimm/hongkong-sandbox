"""Freeze remaining Peng Chau originals in descending source-size order.

Local cached originals only. Existing classifications and triangle counts define
priority, not quality or acceptance. No uploads, review writes or publication.
"""
import copy
from collections import Counter
from pathlib import Path
from islands_direct_stage import ROOT,HERE,read,save,sha,rel
from run import connect

BATCH='government-islands-peng-chau-largest-first-20261107-v1'
DOC=ROOT/'docs/astra-city/government-import'/BATCH


def main():
    assert not DOC.exists()
    base=ROOT/'docs/astra-city/government-import'
    metadata={};pins={}
    for name in ('government-islands-peng-chau-0000-1000-20261106','government-islands-peng-chau-1000-425-20261106'):
        p=base/name/'selection.json.gz';pins[rel(p)]=sha(p)
        for row in read(p)['rows']:assert row['uid']not in metadata;metadata[row['uid']]=row
    source_path=base/'government-islands-peng-chau-source-terrain-20261106/check-selection.json.gz';source={r['uid']:r for r in read(source_path)['rows']};pins[rel(source_path)]=sha(source_path)
    assert set(source)==set(metadata)and len(source)==1425
    identity_path=base/'government-islands-peng-chau-identity-20261106-v1/identities.json.gz';identity=read(identity_path);pins[rel(identity_path)]=sha(identity_path);sync=read(identity_path.parent/'neon-sync.json')
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert sync['exactResultMatch']and db.execute("SELECT result->'evidence' FROM astra_modelling.jobs WHERE id=%s AND status='complete'",(sync['jobId'],)).fetchone()[0]=={'path':rel(identity_path),'sha256':sha(identity_path)}
        states=dict(db.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC',(list(source),)))
    identities={r['uid']:r for r in identity['rows']}
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=sha(manifest_path);manifest=read(manifest_path);pins[rel(manifest_path)]=manifest_sha;pins[rel(Path(__file__))]=sha(Path(__file__))
    installed={m['uid']for url in manifest['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
    targets=set(source)-installed;assert len(targets)==1383
    current={}
    for tile in manifest['tiles']:
        path=ROOT/'3d-viewer'/tile['url']
        for form in read(path)['buildings']:
            if form['uid']in targets:
                assert form['uid']not in current;current[form['uid']]=(form,tile['url'],sha(path))
    assert set(current)==targets
    priority={'xxl':6,'xl':5,'large':4,'medium':3,'small':2,'xs':1,'unmeasured':0};ranked=[];rows=[]
    for uid in targets:
        meta=metadata[uid];row=copy.deepcopy(source[uid]);entry=row['candidate']['entry'];asset=ROOT/row['candidate']['path'];assert sha(asset)==entry['sha256']==meta['sourceSHA256']and entry['triangles']==meta['triangles']
        form,tile,h=current[uid];same_form=form==row['source']['building'];row['source']={'building':form,'tile':tile,'tileSHA256':h}
        proof=identities.get(uid)
        if same_form and proof and proof['passed']:
            assert proof['context']['sourceSHA256']==entry['sha256'];row['identityProof']=proof['proof']
        low,high=entry['worldBounds'];group=meta['sizeGroup'];assert group in priority
        ranked.append({'uid':uid,'name':meta['name'],'sizeGroup':group,'triangles':meta['triangles'],'sourceBytes':asset.stat().st_size,'sourceSHA256':entry['sha256'],'physicalDimensionsMetres':[high[i]-low[i]for i in range(3)],'latestReview':states.get(uid),'currentFormUnchanged':same_form,'source':row})
    ranked.sort(key=lambda r:(-priority[r['sizeGroup']],-r['triangles'],-r['sourceBytes'],r['uid']))
    for i,r in enumerate(ranked,1):r['priorityRank']=i
    public=[{k:v for k,v in r.items()if k!='source'}for r in ranked]
    save(DOC/'ranked-remaining.json.gz',{'rows':public,'models':len(public),'sizeGroups':dict(Counter(r['sizeGroup']for r in ranked)),'manifestSHA256':manifest_sha,'inputHashes':pins,'order':'Size group, triangles, original compressed source bytes, UID; descending size','uploads':False,'publication':False})
    # Explicit fifty-source first cohort keeps the normal worker's <=50 guard.
    rows=[r['source']for r in ranked[:50]]
    for row in rows:pins[row['candidate']['path']]=row['candidate']['entry']['sha256'];pins[rel(ROOT/'3d-viewer'/row['source']['tile'])]=row['source']['tileSHA256']
    assert sha(manifest_path)==manifest_sha
    batch=BATCH+'-direct-001';save(base/batch/'selection.json.gz',{'batch':batch,'rows':rows,'manifestSHA256':manifest_sha,'inputHashes':pins,'identityEvidencePath':rel(identity_path),'priorityRanks':[1,50],'nominationOnly':True,'publication':False})
    save(DOC/'state.json',{'state':'first-50-prepared','models':1383,'sizeGroups':dict(Counter(r['sizeGroup']for r in ranked)),'firstBatch':batch,'firstNames':[r['name']for r in ranked[:9]],'uploads':False,'publication':False})
    print({'remaining':len(ranked),'first50':batch,'sizeGroups':dict(Counter(r['sizeGroup']for r in ranked))},flush=True)


if __name__=='__main__':main()
