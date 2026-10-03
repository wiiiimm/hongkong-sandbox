"""Recover exact government models around the Elements podium; never AI."""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import ROOT, HERE, read, save, connect, digest, NATIVE_RUN
sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
import shape_prepare

DOC = ROOT / 'docs/astra-city/government-import/government-xxl-20260911/second-pass/elements'
LOCAL = HERE / 'local/government-xxl-second-20260911/elements-supports'


def main():
    checks = read(DOC / 'neighbour-checks.json')
    wanted = {row['uid'] for row in checks['rows'] if row['reasons']}
    neighbour = read(DOC / 'neighbour-inputs.json.gz')
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    tiles = {tile['id']: tile['url'] for tile in manifest['tiles']}
    sources = {
        row['building']['uid']: {
            'building': row['building'],
            'tile': tiles[row['building']['tile']],
        }
        for row in neighbour['rows'] if row['building']['uid'] in wanted
    }
    for source in sources.values():
        raw = (ROOT / '3d-viewer' / source['tile']).read_bytes()
        source['tileSHA256'] = digest(raw)
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        rows = connection.execute("""SELECT i.sheet,r.cache_key,r.result_sha,x FROM astra_modelling.native_stage_members m
            JOIN astra_modelling.native_stage_results r USING(cache_key)
            JOIN astra_modelling.native_stage_inputs i USING(cache_key)
            CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x
            WHERE m.run_id=%s AND EXISTS(SELECT 1 FROM jsonb_array_elements(x->'matching'->'viewerMatches') v WHERE v->>'uid'=ANY(%s))""", (NATIVE_RUN, sorted(wanted))).fetchall()
    native = [{'sheet': sheet, 'cacheKey': key, 'resultSha': sha, 'model': model} for sheet, key, sha, model in rows]
    matched = {match['uid'] for item in native for match in item['model'].get('matching', {}).get('viewerMatches', []) if match['uid'] in wanted}
    save(LOCAL / 'inputs.json.gz', {'nativeRun': NATIVE_RUN, 'rows': sorted(wanted), 'requestedUids': sorted(wanted), 'sources': sources, 'native': native})
    result = shape_prepare.prepare(LOCAL / 'inputs.json.gz', LOCAL, allow_source=True, workers=4, env_file=ROOT / '.env.modelling')
    report = {
        'requested': len(wanted),
        'exactSourceMatches': len(matched),
        'recovered': len(result['rows']),
        'missingUids': sorted(wanted - matched),
        'errors': result['errors'],
        'methods': result['methods'],
        'aiCalls': 0,
        'geometryChanges': 0,
        'publication': False,
    }
    assert report['exactSourceMatches'] == report['recovered']
    save(DOC / 'support-source-recovery.json', report)
    print(json.dumps(report))


if __name__ == '__main__':
    main()
