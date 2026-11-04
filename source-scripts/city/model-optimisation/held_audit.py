"""Explain historical exclusions using committed catalogues and read-only Neon evidence."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

import batch
from db import connect, CONFIG
import jobs
from psycopg.rows import dict_row


def audit(prior_path, output, apply=False):
    prior = json.loads(prior_path.read_bytes())
    current = batch.snapshot()
    entries = {}
    for name in current['catalogueHashes']:
        cat = json.loads((batch.ROOT / name).read_bytes())
        for entry in cat['models']:
            entries[entry['uid']] = (name, entry)
    held_uids = [row['uid'] for row in prior['held']]
    with connect() as con:
        con.row_factory = dict_row
        rows = con.execute('''SELECT DISTINCT ON(uid) uid,snapshot_id,source_sha256,
            review_state,result,initial_evidence,updated_at FROM astra_modelling.model_reviews
            WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC,snapshot_id DESC''',
            (held_uids,)).fetchall()
    raw = (json.dumps(rows, default=str, ensure_ascii=False, sort_keys=True) + '\n').encode()
    archive = output / 'latest-neon-reviews.json.gz'
    archive.parent.mkdir(parents=True, exist_ok=True)
    packed = gzip.compress(raw, mtime=0)
    if archive.exists() and archive.read_bytes() != packed:
        raise ValueError('Use a new immutable audit directory')
    archive.write_bytes(packed)
    by_uid = {row['uid']: row for row in rows}
    reports = []
    for old in prior['held']:
        name, entry = entries[old['uid']]
        asset = (batch.ROOT / name).parent / entry['asset']
        source_sha = hashlib.sha256(asset.read_bytes()).hexdigest()
        if source_sha != entry['sha256']:
            raise ValueError('Current held source hash mismatch')
        flags = {key: entry.get(key) for key in ('publicationApproved', 'placementReviewed',
            'identityReviewApproved', 'sourceIdentityReviewed', 'landmarkMembershipApproved',
            'wholeLandmarkAccepted', 'placementScreened', 'placementScreening', 'knownPlacementHold')}
        reason = ('publication-blocked' if flags['publicationApproved'] is False else
            'identity-negative' if flags['identityReviewApproved'] is False else
            'placement-unreviewed')
        row = by_uid.get(entry['uid'])
        review = None
        if row:
            result = row['result'] or {}
            evidence = result.get('evidence')
            path = (batch.ROOT / evidence).resolve() if isinstance(evidence, str) else None
            evidence_sha = (hashlib.sha256(path.read_bytes()).hexdigest()
                if path and path.is_relative_to(batch.ROOT) and path.is_file() else None)
            review = {'snapshotId': row['snapshot_id'], 'state': row['review_state'],
                'updatedAt': str(row['updated_at']), 'sourceSha256': row['source_sha256'],
                'currentSourceBytesMatch': row['source_sha256'] == source_sha,
                'evidence': evidence, 'expectedEvidenceSha256': result.get('sha256'),
                'actualEvidenceSha256': evidence_sha,
                'evidenceHashMatches': evidence_sha is not None and evidence_sha == result.get('sha256'),
                'observation': result.get('observation'),
                'currentPlacementMetadataMatch': None,
                'qualification': 'Matching source bytes and an old installed review do not prove current pose/terrain/support acceptance.'}
        explicit_component = (flags['sourceIdentityReviewed'] is True
            and flags['publicationApproved'] is True and flags['placementReviewed'] is True)
        reports.append({'uid': entry['uid'], 'label': entry.get('label'), 'catalogue': name,
            'currentSourceSha256': source_sha, 'reason': reason, 'flags': flags,
            'reviewScope': entry.get('reviewScope'), 'placementReview': entry.get('placementReview'),
            'explicitNativeComponentAcceptanceConflictsWithIdentityFlag': explicit_component
                and flags['identityReviewApproved'] is False,
            'latestNeonReview': review,
            'nextAction': ('Reconcile source-component acceptance versus landmark naming without approving the proposed identity.'
                if explicit_component else 'Reconcile exact current pose/support/terrain acceptance and original review evidence on Astra; retain the hold until resolved.')})
    counts = Counter(row['reason'] for row in reports)
    summary = {'executor': batch.ACTOR, 'branchId': CONFIG['branch_id'],
        'sourceCommit': current['sourceCommit'], 'historicalSnapshot': str(prior_path.relative_to(batch.ROOT)),
        'historicalSnapshotSha256': hashlib.sha256(prior_path.read_bytes()).hexdigest(),
        'historicalHeldCount': len(reports), 'reasonCounts': dict(counts),
        'explicitNativeComponentFlagConflicts': sum(row['explicitNativeComponentAcceptanceConflictsWithIdentityFlag'] for row in reports),
        'latestReviewCount': len(rows), 'latestReviewStates': dict(Counter(row['review_state'] for row in rows)),
        'matchingInstalledReviews': sum(bool(row['latestNeonReview'] and
            row['latestNeonReview']['state'] == 'installed-verified' and
            row['latestNeonReview']['currentSourceBytesMatch']) for row in reports),
        'matchingInstalledReviewsWithVerifiedEvidence': sum(bool(row['latestNeonReview'] and
            row['latestNeonReview']['state'] == 'installed-verified' and
            row['latestNeonReview']['currentSourceBytesMatch'] and
            row['latestNeonReview']['evidenceHashMatches']) for row in reports),
        'noLatestNeonReviewCount': len(reports)-len(rows),
        'neonArchive': str(archive.relative_to(batch.ROOT)),
        'neonArchiveSha256': hashlib.sha256(packed).hexdigest(),
        'qualification': 'Source acceptance records remain unchanged. This audit diagnoses conflicts; it neither waives negative flags nor backfills placement approval.',
        'models': reports}
    report_path = output / 'held-audit.json'
    report_sha = batch.write(report_path, summary)
    if apply:
        payload = {'report': str(report_path.relative_to(batch.ROOT)), 'reportSha256': report_sha}
        name = 'accepted-enhanced-held-audit-v1-20261012'
        job_id = jobs.enqueue(name, 'model-optimisation-source-audit-v1', payload)
        job = jobs.claim(name, batch.ACTOR, ['model-optimisation-source-audit-v1'], job_ids=[job_id])
        if job and not jobs.finish(job, result={**payload, **{key:value for key,value in summary.items() if key != 'models'}}):
            raise ValueError('Audit lease lost')
        with connect() as con:
            row = con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (job_id,)).fetchone()
        if row[0] != 'complete' or row[1]['reportSha256'] != report_sha:
            raise ValueError('Neon audit readback mismatch')
        batch.write(output/'neon-sync.json', {'jobId':job_id, 'status':'complete',
            'reportSha256':report_sha, 'exactReadback':True, 'branchId':CONFIG['branch_id']})
    print(json.dumps({key:value for key,value in summary.items() if key != 'models'}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prior', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    audit(args.prior.resolve(), args.output.resolve(), args.apply)
