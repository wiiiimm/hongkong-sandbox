"""Reproducible per-landmark progress; model parts never count as whole landmarks."""
import argparse, collections, hashlib, json, pathlib, sqlite3
ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def review_status(review, uids, installed, root):
    if not review:
        return 'not-reviewed'
    if not review.get('identityReviewed') or not review.get('componentMembershipComplete'):
        return 'incomplete-review'
    if set(review.get('sourceUids', [])) != uids or not uids:
        return 'component-set-changed'
    if not uids <= installed:
        return 'models-not-installed'
    required = ('appearance', 'placement', 'picking', 'collision', 'viewerLoading')
    if not all(review.get('checks', {}).get(k) is True for k in required):
        return 'checks-incomplete'
    if not review.get('evidence') or review.get('blockingGaps'):
        return 'evidence-or-gap-pending'
    for path, sha in review['evidence'].items():
        p = root / path
        if not p.is_file() or digest(p) != sha:
            return 'evidence-changed'
    return 'ready-for-review'

def acquisition_records(root):
    """Latest explicit batch result per UID; an absent reference is not missing work."""
    base = root / 'docs/astra-city/landmark-acquisition'
    paths = ([base / 'report.json'] if (base / 'report.json').exists() else [])
    paths += sorted((base / 'batches').glob('*/report.json'))
    records = {}
    for path in sorted(paths, key=lambda p: (read(p).get('generatedAt', ''), str(p))):
        for row in read(path).get('rows', []):
            records[row['uid']] = dict(row, report=str(path.relative_to(root)))
    return records, paths

def source_status(part, installed, acquired):
    uid = part['uid']
    if uid in installed:
        return 'installed'
    if part.get('stagedAsset') or part.get('state') == 'candidate-staged':
        return 'prepared-for-review'
    if part.get('state') == 'no-government-identity':
        return 'identity-required'
    record = acquired.get(uid, {})
    if record.get('outcome') == 'no-exact-model-in-complete-checked-sheets':
        return 'exact-source-absent-in-checked-sheets'
    if record.get('outcome') == 'acquired-and-staged':
        return 'acquired-match-review' if record.get('standardMatch') is not True else 'acquired-preparation-pending'
    return 'acquisition-pending'

def build(root=ROOT):
    registry_path = root / 'source-scripts/city/landmark-registry/landmarks.json'
    batch_path = root / 'docs/astra-city/landmark-bulk/bulk-report.json'
    reviews_path = root / 'source-scripts/city/landmark-progress/reviews.json'
    registry, batch, reviews = read(registry_path), read(batch_path), read(reviews_path)
    landmarks = registry['landmarks']; rows = {r['id']: r for r in batch['rows']}
    input_paths = [registry_path, batch_path, reviews_path]
    stage_path = root / 'docs/astra-city/landmark-identity/stage-summary.json'
    if stage_path.exists():
        stage = read(stage_path); source_parts = {p['uid']: p for p in stage['parts']}
        if {r['id'] for r in stage['rows']} != set(rows):
            raise ValueError('Combined stage does not account for the registry')
        for r in stage['rows']:
            parts = [source_parts[u] for u in r['members']]
            state = ('nonbuilding-scope' if r['identityState']=='historical-interior-host-unresolved' else
                     'no-identity' if r['identityState']=='no-supported-identity' else
                     'ambiguous' if r['identityState']=='identity-needs-review' else
                     'proposed-identity' if r['identityState']=='proposed-identity-overlay' else
                     'known-placement-holds' if any(p.get('knownHold') for p in parts) else
                     'cache-absent' if any(p['state'] in ('not-in-retained-staged-models','no-government-identity') for p in parts) else
                     'candidates-staged' if any(p['state']=='candidate-staged' for p in parts) else 'already-detailed')
            rows[r['id']] = dict(r,parts=parts,state=state)
        input_paths.append(stage_path)
    ids = {r['id'] for r in landmarks}
    if len(ids) != len(landmarks) or ids != set(rows):
        raise ValueError('Registry/batch membership differs; regenerate the bulk accounting first')
    if set(reviews) - ids:
        raise ValueError('Review references unknown landmark')
    db = root / 'source-scripts/city/building-batch/local/buildings.sqlite'
    with sqlite3.connect(db.resolve().as_uri() + '?mode=ro', uri=True) as c:
        for path, sha in c.execute('SELECT path,sha256 FROM inputs'):
            p = root / '3d-viewer' / path
            if not p.is_file() or digest(p) != sha:
                raise ValueError('Inventory stale: ' + path + '; regenerate inventory first')
        installed = {u for u, in c.execute('SELECT uid FROM buildings WHERE active=1 AND embedded=1')}
        installed |= {u for u, in c.execute('SELECT DISTINCT uid FROM models')}
    acquired, acquisition_paths = acquisition_records(root)
    input_paths.extend(acquisition_paths)
    result = []
    for landmark in landmarks:
        row = rows[landmark['id']]
        parts = {p['uid']: p for p in row['parts']}; uids = set(parts)
        staged = {u for u,p in parts.items() if p.get('stagedAsset') or p.get('state')=='candidate-staged'}
        held = {u:p['knownHold'] for u,p in parts.items() if p.get('knownHold')}
        sources = {u:source_status(p, installed, acquired) for u,p in parts.items()}
        review = review_status(reviews.get(landmark['id']), uids, installed, root)
        result.append(dict(id=landmark['id'], name=landmark['name'], preparationState=row['state'],
                           identifiedParts=len(uids), installedIdentifiedParts=len(uids & installed),
                           stagedUninstalledParts=len(staged - installed), heldParts=held,
                           sourceUids=sorted(uids), sourceStates=sources, reviewStatus=review,
                           nextAction='User review' if review=='ready-for-review' else
                           'Resolve host and historical scope' if row['state']=='nonbuilding-scope' else
                           'Resolve identity/component membership' if row['state'] in ('no-identity','ambiguous','proposed-identity') else
                           'Review source support or terrain; higher modelling effort may be needed' if held else
                           'Acquire remaining source components' if 'acquisition-pending' in sources.values() else
                           'Prepare acquired exact sources' if 'acquired-preparation-pending' in sources.values() else
                           'Review acquired source correspondence' if 'acquired-match-review' in sources.values() else
                           'Review alternatives for exact sources absent in checked sheets' if 'exact-source-absent-in-checked-sheets' in sources.values() else
                           'Verify full landmark appearance, placement and interaction in viewer'))
    counts = dict(collections.Counter(r['reviewStatus'] for r in result))
    return dict(schemaVersion=1, landmarks=len(result), readyForReview=counts.get('ready-for-review',0),
                reviewStates=counts, installedTerritoryDetailed=len(installed),
                uniqueSourceStates=dict(collections.Counter({u:state for r in result for u,state in r['sourceStates'].items()}.values())),
                preparationStates=dict(collections.Counter(r['preparationState'] for r in result)),
                qualification='Readiness requires explicit whole-landmark evidence. Existing model references and staged parts are not completion. This report does not publish models or change review decisions.',
                stagedUninstalledUnique=len({p['uid'] for r in rows.values() for p in r['parts'] if (p.get('stagedAsset') or p.get('state')=='candidate-staged') and p['uid'] not in installed}),
                inputHashes={str(p.relative_to(root)):digest(p) for p in input_paths},
                rows=result)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=pathlib.Path,default=ROOT);a=p.parse_args()
    result=build(a.root);out=a.root/'docs/astra-city/landmark-progress';out.mkdir(parents=True,exist_ok=True)
    (out/'progress.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    lines=['# Landmark readiness','',result['qualification'],'',f"{result['readyForReview']} / {result['landmarks']} have explicit whole-landmark readiness records. This is not a count of visible or detailed buildings.",'','| Landmark | Identified / installed parts | Prepared, uninstalled | Review | Next action |','|---|---:|---:|---|---|']
    summary=['## Source preparation', '', 'Counts below are unique identified model parts, not complete landmarks.', '']
    summary += [f'- {state}: {count}' for state,count in sorted(result['uniqueSourceStates'].items())]
    lines[6:6] = summary + ['']
    for r in result['rows']:
        name=r['name'].replace('|','/');lines.append(f"| {name} | {r['identifiedParts']} / {r['installedIdentifiedParts']} | {r['stagedUninstalledParts']} | {r['reviewStatus']} | {r['nextAction']} |")
    (out/'README.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
