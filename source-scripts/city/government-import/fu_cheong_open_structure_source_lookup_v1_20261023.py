"""Bounded exact source availability search for the retained open-sided actor."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BATCH = 'government-xl-fu-cheong-open-structure-source-lookup-v1-20261023'
GEO = 'government-xl-nam-cheong-foreign-geometry-v1-20261023'
ACQUIRE = 'government-xl-nam-cheong-fu-yun-acquire-v1-20261023'


def main():
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / BATCH
    assert not doc.exists()
    refs = [Path(__file__)]
    pins = {}
    for name in [GEO, ACQUIRE]:
        _, pins[name] = authenticate(base / name)
        refs.append(base / name / 'result.json')
    path = base / GEO / 'basic-input.json.gz'
    assert digest(path.read_bytes()) == pins[GEO][str(path.relative_to(ROOT))]
    refs.append(path)
    form = read(path)['rows'][0]
    assert form['uid'] == 'landsd/233291:0' and form['buildingCSUID'] == '3395520992T20110713'
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        db.execute("SET LOCAL statement_timeout='120s'")
        count = db.execute('SELECT count(DISTINCT cache_key) FROM astra_modelling.native_stage_members WHERE run_id=%s', (NATIVE_RUN,)).fetchone()[0]
        models = db.execute("""SELECT DISTINCT r.cache_key,r.result_sha,i.sheet,m.value
          FROM astra_modelling.native_stage_results r
          JOIN astra_modelling.native_stage_inputs i USING(cache_key)
          JOIN astra_modelling.native_stage_members membership USING(cache_key)
          CROSS JOIN LATERAL jsonb_array_elements(r.result->'models')m
          WHERE membership.run_id=%s AND (m.value->>'modelId' LIKE %s OR EXISTS (
            SELECT 1 FROM jsonb_array_elements(COALESCE(m.value#>'{matching,officialCandidates}','[]'::jsonb)) candidate
            WHERE candidate->>'buildingCSUID'=%s))
          ORDER BY r.cache_key""", (NATIVE_RUN, 'B3395520992%', form['buildingCSUID'])).fetchall()
        directories = db.execute("""SELECT cache_key,sheet,index_sha,result-'models',m.value
          FROM astra_modelling.city_source_directories
          CROSS JOIN LATERAL jsonb_array_elements(result->'models')m
          WHERE m.value->>'modelId' LIKE %s ORDER BY cache_key,m.value->>'modelId'""", ('B3395520992%',)).fetchall()
        directorycount = db.execute('SELECT count(*) FROM astra_modelling.city_source_directories').fetchone()[0]
    save(doc / 'prepared-source-matches.json.gz', [dict(cacheKey=k,resultSHA256=h,sheet=s,model=m) for k,h,s,m in models])
    save(doc / 'directory-index-matches.json.gz', [dict(cacheKey=k,sheet=s,indexSHA256=h,directory=d,model=m) for k,s,h,d,m in directories])
    directorypath = HERE / 'local' / ACQUIRE / 'directory/zip-directory.bin'
    assert digest(directorypath.read_bytes()) == pins[ACQUIRE][str(directorypath.relative_to(ROOT))]
    refs.append(directorypath)
    parser = module('open_structure_raw_directory', HERE.parent / 'landmark-acquisition/acquire.py')
    infos, _ = parser.parse_directory(directorypath.read_bytes())
    rawmatches = [x.filename for x in infos if '3395520992' in x.filename]
    save(doc / 'complete-same-sheet-members.json.gz', [x.filename for x in infos])
    result = dict(uids=['landsd/268867:0'], relatedUID=form['uid'], exactCSUID=form['buildingCSUID'],
                  nativeRun=NATIVE_RUN, nativeStageMembers=count, preparedMatches=len(models),
                  directoryIndexRows=directorycount, directoryIndexMatches=len(directories),
                  completeSameSheetMembers=len(infos), exactSameSheetRawMembers=rawmatches,
                  actorRetained=True, installationApproved=False, permanentRejection=False,
                  qualification='Exact GeoRef prefix and CSUID search across pinned prepared run, exact GeoRef across all retained indexed directories, and complete authenticated raw current-sheet directory. Index scanner covers01/02tower/podium only; same-sheet raw list is unfiltered. A negative is not proof of territory-wide provider absence or permission to delete/rebuild the retained actor.')
    save(doc / 'summary.json', result)
    refs.extend([HERE.parent / 'landmark-acquisition/acquire.py', HERE.parent / 'citywide-source/discover.py'])
    module('open_structure_source_lookup_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'retained-open-sided-actor-exact-government-source-lookup', refs, result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
