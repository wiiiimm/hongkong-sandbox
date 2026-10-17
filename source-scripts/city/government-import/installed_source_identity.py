"""Resolve an unchanged installed acceptance from current manifest and Neon."""
from run import ROOT,HERE,read,digest,connect
from accepted_source_identity import reuse_identity


def installed_identity(row,manifest):
    uid=row['uid'];pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        found=con.execute('SELECT to_jsonb(r) FROM astra_modelling.model_reviews r WHERE snapshot_id=%s AND uid=%s', (pointer['snapshotId'],uid)).fetchone()
    if not found or found[0]['review_state']!='installed-verified':return None
    review=found[0];matches=[]
    for url in manifest['officialModelCatalogues']:
        catalogue=ROOT/'3d-viewer'/url
        for model in read(catalogue)['models']:
            if model['uid']==uid:matches.append((catalogue,model))
    assert len(matches)==1, 'Installed source must be unique in the current manifest'
    catalogue,model=matches[0]
    accepted=HERE/'accepted'/catalogue.parent.name/'source-forms.json'
    if not accepted.exists():return None  # Missing original accepted form is not inferred.
    forms=[f for f in read(accepted) if f['uid']==uid];assert len(forms)==1
    evidence=(ROOT/review['result']['evidence']).resolve();assert evidence.is_relative_to(ROOT)
    current=row['source']['building'];tile=ROOT/'3d-viewer'/row['source']['tile']
    assert digest(tile.read_bytes())==row['source']['tileSHA256']
    assert [f for f in read(tile)['buildings'] if f['uid']==uid]==[current]
    assert digest((catalogue.parent/model['asset']).read_bytes())==row['sourceSHA256']
    assert digest((ROOT/row['candidate']['path']).read_bytes())==row['sourceSHA256']
    proof=reuse_identity(current_form=current,accepted_form=forms[0],candidate=row['candidate']['entry'],
        installed_model=model,catalogue_sha=digest(catalogue.read_bytes()),acceptance=read(evidence),
        acceptance_sha=digest(evidence.read_bytes()),review=review)
    proof['evidenceRefs']=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in (catalogue,accepted,evidence,tile)]
    return proof
