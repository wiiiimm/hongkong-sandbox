"""Summarise all four independently audited tiers and verify their Neon identities."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import batch
from db import connect, CONFIG
import jobs
from psycopg.rows import dict_row
import registry


def summarise(folder, apply=False):
    snap=registry.read(folder/'sources.json')
    batch.check_snapshot(snap)
    expected={}
    audits={}
    for tier in ('original','high','balanced','lightweight'):
        recipe=registry.read(folder/(tier+'-recipe.json'))
        recipe_sha=registry.digest(recipe)
        for source in snap['selected']:
            expected[registry.digest([source['revisionId'],recipe_sha])]=(tier,source)
        paths=sorted((folder/tier).glob('readback-*.json'))
        if not paths: raise ValueError('Missing complete tier audit')
        report=registry.read(paths[-1])
        checkpoint=registry.read(folder/tier/'neon-sync.json')
        if (report['processedCount']!=len(snap['selected']) or report['failedCount']
                or report['recipeSha256']!=recipe_sha or not checkpoint['exactReadback']
                or checkpoint['reportSha256']!=hashlib.sha256(paths[-1].read_bytes()).hexdigest()):
            raise ValueError('Tier audit/receipt mismatch')
        audits[tier]={'report':str(paths[-1].relative_to(batch.ROOT)),
            'reportSha256':checkpoint['reportSha256'],'checkpointJobId':checkpoint['jobId'],
            'recipeSha256':recipe_sha}
    with connect() as con:
        con.row_factory=dict_row
        rows=con.execute('SELECT * FROM astra_modelling.optimisation_status WHERE variant_id=ANY(%s)',
            (list(expected),)).fetchall()
        checkpoints=con.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)',
            ([a['checkpointJobId'] for a in audits.values()],)).fetchall()
        active=con.execute('''SELECT count(*) AS count FROM astra_modelling.reservation_groups
            WHERE owner=%s AND batch LIKE %s AND released_at IS NULL AND lease_until>clock_timestamp()''',
            (batch.ACTOR,folder.name+'%')).fetchone()['count']
    if len(rows)!=len(expected) or active:
        raise ValueError('Missing variants or live batch reservations')
    if len(checkpoints)!=4 or any(row['status']!='complete' for row in checkpoints):
        raise ValueError('Missing complete Neon checkpoints')
    for row in checkpoints:
        audit=next(a for a in audits.values() if a['checkpointJobId']==row['id'])
        if row['result']['reportSha256']!=audit['reportSha256']:
            raise ValueError('Neon checkpoint differs from local audit')
    tiers={}
    for tier in audits:
        selected=[row for row in rows if expected[row['variant_id']][0]==tier]
        if len(selected)!=len(snap['selected']): raise ValueError('Incomplete tier')
        metrics=[]
        for row in selected:
            source=expected[row['variant_id']][1]
            result=row['result']
            if (row['processing_status']!='complete' or row['validation_status']!='unreviewed'
                    or result['variantId']!=row['variant_id'] or result['revisionId']!=source['revisionId']
                    or result['sourceSha256']!=source['sourceSha256'] or result['published'] is not False):
                raise ValueError('Variant identity/state mismatch')
            metrics.append(result['metrics'])
        total=lambda key:sum(m[key] for m in metrics)
        smaller=[m for m in metrics if m['beneficial']]
        source_bytes=total('originalDownloadBytes')
        savings=sum(m['originalDownloadBytes']-m['downloadBytes'] for m in smaller)
        tiers[tier]={'processedCount':len(metrics),'beneficialCount':len(smaller),
            'nonBeneficialCount':len(metrics)-len(smaller),'sourceBytes':source_bytes,
            'allCandidateBytes':total('downloadBytes'),'savedBytesUsingSmallerCandidates':savings,
            'effectiveBytesKeepingOtherOriginals':source_bytes-savings,'effectiveSavingsPercent':savings/source_bytes*100,
            'originalTriangles':sum(m.get('originalTriangles',m['triangles']) for m in metrics),
            'candidateTriangles':total('triangles'),'candidateVertices':total('vertices'),
            'candidateAccessorByteEstimate':total('decodedAccessorBytes'),**audits[tier]}
        if tier!='original':
            for key in ('maxPositionQuantisationErrorMetres','simplifierEstimatedErrorMetres',
                    'combinedEstimatedErrorMetres','maxLocalNormalAngleDegrees','maxColourComponentError'):
                tiers[tier][key]=max(m[key] for m in metrics)
            for key in ('quantisationCollapsedFaces','quantisationFlippedFaces','quantisationExpandedDegenerateFaces',
                    'quantisationProtectedFaces','quantisationRestoredVertices','removedVertices'):
                tiers[tier][key]=total(key)
            if any(tiers[tier][key] for key in ('quantisationCollapsedFaces',
                    'quantisationFlippedFaces','quantisationExpandedDegenerateFaces')):
                raise ValueError('Unexpected lossy geometry regression')
    report={'schemaVersion':1,'executor':'Codex','branchId':CONFIG['branch_id'],
        'sourceCommit':snap['sourceCommit'],'sourceSnapshotSha256':hashlib.sha256((folder/'sources.json').read_bytes()).hexdigest(),
        'selectionPolicy':snap['selectionPolicy'],'installedCount':len(snap['selected']),
        'variantsPerModel':4,'completeVariants':len(rows),'reviewBasedExclusions':len(snap['held']),
        'failedCount':0,'publishedCount':0,'validationStatus':'unreviewed','activeOwnReservations':active,
        'tiers':tiers,'qualification':'Measured offline candidates for every installed source. Original assets/reviews and runtime catalogues unchanged. Simplifier error is estimated; Float32 placement/visual/collision/device gates remain untested.'}
    path=folder/'summary.json';report_sha=batch.write(path,report)
    if apply:
        name=folder.name+'-delivery'
        payload={'report':str(path.relative_to(batch.ROOT)),'reportSha256':report_sha}
        job_id=jobs.enqueue(name,'model-optimisation-delivery-v1',payload)
        job=jobs.claim(name,batch.ACTOR,['model-optimisation-delivery-v1'],job_ids=[job_id])
        if job and not jobs.finish(job,result={**report,**payload}):raise ValueError('Summary lease lost')
        with connect() as con:
            row=con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job_id,)).fetchone()
        if row[0]!='complete' or row[1]['reportSha256']!=report_sha or row[1]['completeVariants']!=len(rows):
            raise ValueError('Summary Neon readback mismatch')
        batch.write(folder/'neon-sync.json',{'jobId':job_id,'status':'complete','branchId':CONFIG['branch_id'],
            'reportSha256':report_sha,'exactReadback':True,'completeVariants':len(rows)})
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--folder',type=Path,required=True);p.add_argument('--apply',action='store_true')
    args=p.parse_args();summarise(args.folder.resolve(),args.apply)
