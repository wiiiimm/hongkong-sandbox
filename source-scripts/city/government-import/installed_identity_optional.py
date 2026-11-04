"""Decline unsupported legacy receipt shapes without inferring installed identity.

Supported single-source evidence still uses the existing strict byte/form/pose
checks. Malformed hashes or failed supported proof checks remain hard failures.
"""
from run import ROOT, read, digest, connect
from installed_source_identity import installed_identity as strict_installed_identity


def supports_single_source_reuse(acceptance):
    return isinstance(acceptance, dict) and all(
        key in acceptance for key in ('uid', 'sourceSHA256', 'catalogueSHA256'))


def installed_identity(row, manifest):
    pointer = read(ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        found = con.execute('SELECT review_state,result FROM astra_modelling.model_reviews '
                            'WHERE snapshot_id=%s AND uid=%s', (pointer['snapshotId'], row['uid'])).fetchone()
    if not found or found[0] != 'installed-verified':
        return None
    evidence = (ROOT / found[1]['evidence']).resolve()
    assert evidence.is_relative_to(ROOT), 'Installed receipt must be inside the repository'
    assert digest(evidence.read_bytes()) == found[1]['sha256'], 'Installed receipt hash changed'
    if not supports_single_source_reuse(read(evidence)):
        return None
    return strict_installed_identity(row, manifest)
