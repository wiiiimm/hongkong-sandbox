"""HKS-222 read-only preparation audit; no converter, review or viewer mutation.

Stream accepted sheet results from a repeatable-read Neon snapshot. Write a compact
summary and JSONL exception ledger, then compare absent exact GeoRefNo references
with every record in the retained raw government footprint source.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def normal_ref(value):
    """Diagnostic normalisation only; never used to rewrite an identity."""
    try:
        number=Decimal(str(value).strip())
        if not number.is_finite() or number!=number.to_integral_value():
            return None
        return str(int(number))
    except (InvalidOperation,ValueError,TypeError,OverflowError):
        return None


def raw_reference_matches(path, refs):
    # Reuse the incremental source reader, retaining only requested identities.
    sys.path.insert(0,str(HERE.parent/'landsd-territory'))
    from retain import iter_features
    normalised=defaultdict(set)
    for ref in refs:
        key=normal_ref(ref)
        if key is not None:normalised[key].add(ref)
    found=defaultdict(list);types=Counter();count=0
    for f in iter_features(path):
        count+=1;a=f['properties'];value=a.get('GeoRefNo');types[type(value).__name__]+=1;methods=defaultdict(set)
        if str(value) in refs:methods[str(value)].add('exact-GeoRefNo')
        for ref in normalised.get(normal_ref(value),[]):methods[ref].add('normalised-GeoRefNo')
        prefix=str(a.get('BuildingCSUID','')).strip()[:10]
        if prefix in refs:methods[prefix].add('BuildingCSUID-prefix')
        for ref,why in methods.items():
            found[ref].append({'objectId':a.get('OBJECTID'),'geoRefNo':value,'geoRefType':type(value).__name__,'buildingCSUID':a.get('BuildingCSUID'),'methods':sorted(why)})
    return {'sourceSHA256':sha(path),'sourceRecordsScanned':count,'geoRefValueTypes':dict(types),'queriedGeoRefs':len(refs)},found


def audit_records(records, expected, raw_source, ledger, expected_source_sha=None, source_defects=None, terrain_repair=None):
    """Pure streamed aggregation; records are one sheet result at a time."""
    known_defects={(d['sheet'],d['modelId']):d for d in (source_defects or [])}
    repair_entries=(terrain_repair or {}).get('entries',{});used_repairs=set();effective_terrain_states=Counter();effective_terrain_errors=Counter()
    states=Counter();errors=Counter();terrain_states=Counter();terrain_errors=Counter();diagnostics=Counter();categories=Counter()
    candidate_uids=defaultdict(list);missing_refs=defaultdict(list);accepted_sheets=0;indexed_accepted=0;model_rows=0;terrain_rows=0
    mismatches=0;burial_flags=0;support_flags=0
    def emit(category, **fields):
        categories[category]+=1
        ledger.write(json.dumps({'category':category,**fields},ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n')
    for record in records:
        accepted_sheets+=1;sheet=record['sheet'];result=record['result'];models=result.get('models',[]);source_count=record['expectedModels'];indexed_accepted+=source_count;model_rows+=len(models)
        declared=result.get('counts',{}).get('sourceModels')
        if len(models)!=source_count or declared!=source_count:
            mismatches+=1;emit('mechanical-count-mismatch',sheet=sheet,indexedModels=source_count,declaredModels=declared,outcomeRows=len(models))
        for m in models:
            state=m.get('state','missing-state');states[state]+=1
            identity={'sheet':sheet,'modelId':m.get('modelId'),'sourceEntry':m.get('sourceEntry')}
            if state=='packed-needs-placement-review':
                candidate=m.get('candidate') or {};uid=candidate.get('uid')
                if not uid:
                    emit('mechanical-candidate-missing-uid',**identity)
                else:
                    candidate_uids[uid].append({**identity,'assetSHA256':(m.get('asset') or {}).get('sha256') or candidate.get('sha256')})
            elif state=='source-match-held':
                match=m.get('matching',{});source_candidates=match.get('officialCandidates',[])
                if not source_candidates:
                    model=m.get('modelId','');ref=model[1:11] if re.match(r'^B\d{10}',model) else None
                    if ref:missing_refs[ref].append(identity)
                    else:emit('mechanical-invalid-native-reference',**identity,holdReason=m.get('holdReason'))
                else:
                    emit('source-identity-or-geometry-review',**identity,holdReason=m.get('holdReason'),officialCandidates=len(source_candidates),officialMatches=len(match.get('officialMatches',[])),viewerMatches=len(match.get('viewerMatches',[])),matchEvidence=source_candidates)
            elif state=='unsupported-source':
                error=m.get('error') or m.get('holdReason') or 'Unspecified unsupported source'
                errors[(state,error)]+=1;emit('converter-capability-review',**identity,error=error,assetRetained=bool(m.get('asset')))
            else:
                error=m.get('error') or m.get('holdReason') or 'Unspecified conversion failure'
                errors[(state,error)]+=1
                known=known_defects.get((sheet,m.get('modelId')))
                if known and known.get('nativeStageSourceSHA256')==record.get('sourceSHA256'):
                    emit('confirmed-source-corrupt',**identity,originalState=state,error=error,sourceEvidence=known)
                else:
                    emit('unclassified-conversion-failure',**identity,state=state,error=error,assetRetained=bool(m.get('asset')),qualification='Mechanical-stage failure; investigate source defect versus converter limitation before prescribing a fix')
            check=m.get('terrainCheck',{});status=check.get('status','missing');diagnostics[status]+=1
            if status in ('diagnostic-partial-coverage','outside-terrain-coverage'):
                emit('terrain-coverage-review',**identity,terrainCheck=check)
            elif status!='diagnostic-complete':
                if not m.get('asset') and state in ('failed','unsupported-source'):
                    emit('terrain-diagnostic-blocked-by-source',**identity,originalState=state,terrainCheck=check)
                else:
                    emit('mechanical-terrain-diagnostic-failure',**identity,terrainCheck=check)
            if check.get('belowTerrainQuarterMetre',0)>0:
                burial_flags+=1;emit('sampled-terrain-intersection-review',**identity,terrainCheck=check,qualification='Sampled vertices may include legitimate foundations; not full triangle burial proof or automatic rejection')
            rim=check.get('lowRimGapRange')
            if rim and rim[0] is not None and rim[0]>2:
                support_flags+=1;emit('elevated-support-or-placement-review',**identity,lowRimGapRange=rim,qualification='Elevated native base may be a supported tower/overhang; no automatic repositioning')
        terrains=result.get('terrain',[]);terrain_rows+=len(terrains)
        if len(terrains)!=result.get('counts',{}).get('sourceTerrainModels',0):
            mismatches+=1;emit('mechanical-terrain-count-mismatch',sheet=sheet,declaredModels=result.get('counts',{}).get('sourceTerrainModels'),outcomeRows=len(terrains))
        for t in terrains:
            state=t.get('state','missing-state');terrain_states[state]+=1
            repair_key=(record.get('cacheKey'),record.get('sourceSHA256'),t.get('sourceEntry'))
            repair=repair_entries.get(repair_key)
            effective=state
            if state!='prepared-geometry-only':
                error=t.get('error','Unspecified terrain preparation failure');terrain_errors[(state,error)]+=1
                if state=='failed' and repair and repair['outcome']['state'] in ('prepared-geometry-only','source-empty'):
                    effective=repair['outcome']['state'];used_repairs.add(repair_key)
                    emit('original-terrain-failure-repaired',sheet=sheet,sourceEntry=t.get('sourceEntry'),originalState=state,originalError=error,repair=repair)
                else:
                    effective_terrain_errors[(state,error)]+=1
                    emit('mechanical-terrain-preparation-failure',sheet=sheet,sourceEntry=t.get('sourceEntry'),state=state,error=error)
            effective_terrain_states[effective]+=1
    if terrain_repair:
        for error in terrain_repair.get('validationErrors',[]):emit('mechanical-terrain-repair-validation-error',detail=error)
        for key in set(repair_entries)-used_repairs:
            # Failed repair outcomes leave the original failure visible; they are
            # not additional successful overlays awaiting a matching original.
            if repair_entries[key]['outcome']['state'] in ('prepared-geometry-only','source-empty'):
                emit('mechanical-terrain-repair-binding-error',originalCacheKey=key[0],sourceSHA256=key[1],sourceEntry=key[2])
    collision_uids=0;collision_members=0;identical_groups=0;distinct_groups=0
    for uid,members in sorted(candidate_uids.items()):
        if len({m['sheet']for m in members})<2:continue
        collision_uids+=1;collision_members+=len(members)
        identical=len({(m['modelId'],m['assetSHA256'])for m in members})==1 and all(m['assetSHA256'] for m in members)
        identical_groups+=int(identical);distinct_groups+=int(not identical)
        emit('cross-sheet-identical-candidate-duplicate' if identical else 'cross-sheet-candidate-identity-review',uid=uid,members=members,candidatesAltered=False)
    raw_info,matches=raw_reference_matches(raw_source,set(missing_refs))
    raw_info['matchesExpectedSourceSHA256']=None if expected_source_sha is None else raw_info['sourceSHA256']==expected_source_sha
    if raw_info['matchesExpectedSourceSHA256'] is False:
        emit('raw-source-snapshot-mismatch',expectedSHA256=expected_source_sha,actualSHA256=raw_info['sourceSHA256'],qualification='Missing identity comparisons do not establish the frozen run source status')
    missing_class=Counter()
    for ref,models in sorted(missing_refs.items()):
        raw=matches.get(ref,[])
        exact=any('exact-GeoRefNo'in r['methods']for r in raw)
        normalised=any('normalised-GeoRefNo'in r['methods']for r in raw)
        category='mechanical-footprint-selection-or-shape-gap' if exact else 'mechanical-reference-normalisation-review' if normalised else 'source-reference-inconsistency-review' if raw else 'retained-footprint-identity-absent'
        missing_class[category]+=len(models)
        emit(category,geoRefNo=ref,models=models,rawMatches=raw,qualification='No automatic remapping; absence describes the retained footprint snapshot, not the current physical building')
    def patterns(counter):return [{'state':state,'error':error,'count':n}for (state,error),n in counter.most_common()]
    unknown_mechanical=sum(n for category,n in categories.items() if category.startswith('mechanical-') or category in ('unclassified-conversion-failure','converter-capability-review','raw-source-snapshot-mismatch'))
    pending=expected['expectedSheets']-accepted_sheets;complete=pending==0 and model_rows==expected['indexedModels'] and mismatches==0
    return {'issue':'HKS-222','runId':expected['runId'],'snapshotAt':expected.get('snapshotAt'),'status':'raw-source-mismatch-audit' if raw_info['matchesExpectedSourceSHA256'] is False else 'complete-mechanical-audit' if complete else 'partial-mechanical-audit','expectedSheets':expected['expectedSheets'],'acceptedSheets':accepted_sheets,'unacceptedSheets':pending,'indexedModels':expected['indexedModels'],'indexedModelsInAcceptedSheets':indexed_accepted,'modelOutcomeRows':model_rows,'indexedModelsWithoutAcceptedOutcomes':expected['indexedModels']-model_rows,'allAcceptedIndexedModelsAccounted':indexed_accepted==model_rows and mismatches==0,'countMismatches':mismatches,'unknownMechanicalFailures':unknown_mechanical,'confirmedSourceCorruptModels':categories['confirmed-source-corrupt'],'modelStates':dict(states),'modelErrorPatterns':patterns(errors),'terrainOutcomeRows':terrain_rows,'terrainStates':dict(terrain_states),'terrainErrorPatterns':patterns(terrain_errors),'effectiveTerrainStates':dict(effective_terrain_states),'effectiveTerrainErrorPatterns':patterns(effective_terrain_errors),'terrainRepair':None if not terrain_repair else {**terrain_repair['metadata'],'matchedOriginalFailures':len(used_repairs),'unusedPreparedEntries':sum(1 for key in set(repair_entries)-used_repairs if repair_entries[key]['outcome']['state'] in ('prepared-geometry-only','source-empty')),'validationErrors':terrain_repair.get('validationErrors',[])},'terrainDiagnosticStates':dict(diagnostics),'sampledTerrainIntersectionModels':burial_flags,'elevatedLowRimModels':support_flags,'candidateModels':states['packed-needs-placement-review'],'uniqueCandidateUIDs':len(candidate_uids),'crossSheetUIDCollisions':{'uids':collision_uids,'members':collision_members,'identicalSourceGroups':identical_groups,'distinctSourceGroups':distinct_groups},'absentSelectedFootprintCases':sum(map(len,missing_refs.values())),'absentSelectedFootprintClassifications':dict(missing_class),'rawFootprintAudit':raw_info,'exceptionCategories':dict(categories),'published':False,'candidatesAltered':False,'qualification':'Mechanical preparation audit only. Source identity, sampled terrain, supported towers and architectural review remain separate; no placement approval or whole-region completion.'}


def repair_overlay(records, metadata):
    """Validate repair metadata without applying it to any viewer/candidate data."""
    entries={};errors=[]
    for record in records:
        item=record['item'];inputs=item['inputs'];result=record['result'];selected=inputs.get('sourceEntries',[]);terrain=result.get('terrain',[])
        if item['stage']!='native-terrain-repair' or not inputs.get('originalCacheKey'):
            errors.append({'cacheKey':record['cacheKey'],'reason':'Not a bound native-terrain-repair stage'});continue
        actual=[r.get('sourceEntry')for r in terrain]
        if len(set(selected))!=len(selected) or sorted(actual)!=sorted(selected) or len(set(actual))!=len(actual) or result.get('models',[]) or result.get('counts',{}).get('sourceTerrainModels')!=len(selected):
            errors.append({'cacheKey':record['cacheKey'],'reason':'Repair selected/model/terrain outcome completeness mismatch'});continue
        for row in terrain:
            if row.get('state') not in ('prepared-geometry-only','source-empty','failed'):
                errors.append({'cacheKey':record['cacheKey'],'sourceEntry':row.get('sourceEntry'),'reason':'Unsupported repair state'});continue
            if row['state']!='failed' and (not row.get('sourceHashes') or not isinstance(row.get('geometryProof'),dict)):
                errors.append({'cacheKey':record['cacheKey'],'sourceEntry':row.get('sourceEntry'),'reason':'Repair source/geometry proof missing'});continue
            key=(inputs['originalCacheKey'],item['sourceSha256'],row['sourceEntry'])
            if key in entries:
                errors.append({'cacheKey':record['cacheKey'],'sourceEntry':row['sourceEntry'],'reason':'Duplicate repair target'});continue
            entries[key]={'repairCacheKey':record['cacheKey'],'repairResultSHA256':record.get('resultSHA256'),'originalCacheKey':inputs['originalCacheKey'],'sourceSHA256':item['sourceSha256'],'outcome':row}
    return {'entries':entries,'metadata':metadata,'validationErrors':errors}


def read_repair_overlay(con, run_id):
    counts=con.execute("""SELECT count(*) AS sheets,count(r.cache_key) AS accepted,coalesce(sum(jsonb_array_length(i.input_json->'inputs'->'sourceEntries')),0) AS entries FROM astra_modelling.native_stage_members m JOIN astra_modelling.native_stage_inputs i USING(cache_key) LEFT JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE m.run_id=%s""",(run_id,)).fetchone()
    if not counts['sheets']:raise ValueError('Unknown or empty terrain repair run')
    metadata={'runId':run_id,'expectedSheets':counts['sheets'],'acceptedSheets':counts['accepted'],'pendingSheets':counts['sheets']-counts['accepted'],'expectedEntries':counts['entries']}
    with con.cursor(name='native_audit_terrain_repairs')as cursor:
        cursor.itersize=64
        cursor.execute("""SELECT i.input_json AS item,r.cache_key AS "cacheKey",r.result_sha AS "resultSHA256",r.result FROM astra_modelling.native_stage_members m JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE m.run_id=%s ORDER BY i.sheet""",(run_id,))
        return repair_overlay(cursor,metadata)


def audit_database(run_id, output, source, terrain_repair_run=None):
    sys.path.insert(0,str(HERE.parent/'shared-modelling'))
    from db import connect
    from psycopg.rows import dict_row
    output.mkdir(parents=True,exist_ok=True);ledger_path=output/'exceptions.jsonl'
    known_path=ROOT/'docs/astra-city/citywide-native/source-defect-audit.json'
    known_bytes=known_path.read_bytes() if known_path.exists() else None
    known_sha=hashlib.sha256(known_bytes).hexdigest() if known_bytes is not None else None
    source_defects=json.loads(known_bytes).get('models',[]) if known_bytes is not None else []
    with connect() as con:
        con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY');con.row_factory=dict_row
        counts=con.execute('''SELECT count(*) AS sheets,coalesce(sum((i.input_json->'inputs'->'plan'->>'models')::int),0) AS models,now()::text AS snapshot FROM astra_modelling.native_stage_members m JOIN astra_modelling.native_stage_inputs i USING(cache_key) WHERE m.run_id=%s''',(run_id,)).fetchone()
        if not counts['sheets']:raise ValueError('Unknown or empty run')
        expected={'runId':run_id,'expectedSheets':counts['sheets'],'indexedModels':counts['models'],'snapshotAt':counts['snapshot']}
        first=con.execute('''SELECT i.input_json FROM astra_modelling.native_stage_members m JOIN astra_modelling.native_stage_inputs i USING(cache_key) WHERE m.run_id=%s ORDER BY i.sheet LIMIT 1''',(run_id,)).fetchone()['input_json']
        plan=first['inputs']['plan'];selected=ROOT/plan['official'];expected_source_sha=None
        if selected.is_file():
            if sha(selected)!=first['footprintSha256']:raise ValueError('Local official selection differs from frozen run input')
            expected_source_sha=json.loads(gzip.decompress(selected.read_bytes())).get('sourceSHA256')
        terrain_repair=read_repair_overlay(con,terrain_repair_run) if terrain_repair_run else None
        with con.cursor(name='native_audit_sheets') as cursor:
            cursor.itersize=64
            cursor.execute('''SELECT i.sheet,r.cache_key AS "cacheKey",i.source_sha AS "sourceSHA256",(i.input_json->'inputs'->'plan'->>'models')::int AS "expectedModels",r.result FROM astra_modelling.native_stage_members m JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE m.run_id=%s ORDER BY i.sheet''',(run_id,))
            with ledger_path.open('w',encoding='utf-8') as ledger:
                summary=audit_records(cursor,expected,source,ledger,expected_source_sha,source_defects,terrain_repair)
    summary['sourceDefectEvidenceSHA256']=known_sha
    summary['exceptionLedgerSHA256']=sha(ledger_path)
    summary['exceptionLedger']='exceptions.jsonl'
    (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-id',required=True);p.add_argument('--output',required=True,type=Path);p.add_argument('--terrain-repair-run');p.add_argument('--source',type=Path,default=HERE.parent/'landsd-territory/landsd-hong-kong-source.geojson.gz');a=p.parse_args()
    summary=audit_database(a.run_id,a.output,a.source,a.terrain_repair_run)
    print(json.dumps({k:summary[k]for k in ('status','snapshotAt','acceptedSheets','expectedSheets','modelOutcomeRows','indexedModels','modelStates','terrainStates','crossSheetUIDCollisions','absentSelectedFootprintClassifications','exceptionLedgerSHA256')}))

if __name__=='__main__':main()
