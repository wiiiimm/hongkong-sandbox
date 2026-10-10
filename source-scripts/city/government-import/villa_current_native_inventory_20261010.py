"""Current native lineage for the exact own GeoRef and distinct missing canopy."""
from run import NATIVE_RUN
from villa_original_courtyard_upper_boundary_identity_20261010 import SOURCE_SHA

MODEL = 'B216233340102062G0'


def native_rows(connection):
    return [dict(sourceKey=key+'/'+model['modelId'], model=model, resultSHA256=sha)
        for key, model, sha in connection.execute(
        "SELECT r.cache_key,m,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members s USING(cache_key), LATERAL jsonb_array_elements(r.result->'models')m WHERE s.run_id=%s AND (m->>'modelId' LIKE 'B2162333401%%' OR m->>'modelId' LIKE 'B2162233384%%') ORDER BY r.cache_key,m->>'modelId'",
        (NATIVE_RUN,)).fetchall()]


def missing_profiles(connection):
    return [list(r) for r in connection.execute(
        "SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE 'B2162233384%%' ORDER BY cache_key,sheet",
        (NATIVE_RUN,)).fetchall()]


def verify_native_rows(rows):
    assert len(rows) == 1, 'Exactly one complete current native source; no missing/duplicate/new foreign original version'
    r = rows[0]
    assert r['model']['modelId'] == MODEL and r['model']['asset']['sha256'] == SOURCE_SHA
    assert r['sourceKey'].endswith('/'+MODEL) and len(r['sourceKey'].split('/')) == 2
    assert r['model']['triangles'] == 16669
    return True
