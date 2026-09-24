"""Match and pack retained government models using existing source tools; never publish."""
import argparse
import collections
import gzip
import importlib.util
import json
import pathlib
import sys
import threading
import uuid
from inventory import digest, encode
from runner import SCHEMA, connect, execute_jobs

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parents[2]
TOOL_PATHS = ['source-scripts/city/central-completion/pack_models.py',
              'docs/astra-city/mui-wo-buildings/review/bake_model_geometry.py',
              'docs/astra-city/mui-wo-buildings/review/prepare_model_sample.py']


def safe(root, relative):
    path = (root/relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Source path escapes repository')
    return path


def check_source(root, candidate):
    folder = safe(root, candidate['manifest']).parent
    for relative, expected in candidate['spec']['sourceHashes'].items():
        if digest(safe(folder, relative).read_bytes()) != expected:
            raise ValueError('Source checksum mismatch: '+relative)


def generation(c):
    manifest = c.execute("SELECT value FROM settings WHERE key='source_manifest_sha256'").fetchone()[0]
    return digest(encode([manifest, [tuple(r) for r in c.execute('SELECT path,sha256 FROM inputs ORDER BY path')]]).encode())


def tool_hash(root):
    return digest(b''.join(safe(root, p).read_bytes() for p in TOOL_PATHS)+
                  pathlib.Path(__file__).read_bytes()+(HERE/'runner.py').read_bytes())


def prepare(db, root, selection, dry_run=False):
    root = pathlib.Path(root).resolve()
    c = connect(db)
    try:
        c.executescript(SCHEMA)
        selected = c.execute('SELECT * FROM selection_sets WHERE name=?', (selection,)).fetchone()
        gen = generation(c)
        if not selected or selected['inventory_sha256'] != gen:
            raise ValueError('Selection missing/stale; refresh inventory and selection')
        rows = c.execute('''SELECT b.* FROM buildings b JOIN selection_members s ON s.uid=b.uid
              LEFT JOIN models m ON m.uid=b.uid WHERE s.name=? AND b.active=1
              AND b.embedded=0 AND m.uid IS NULL ORDER BY s.priority DESC,b.uid''', (selection,)).fetchall()
        by_csuid = {r['csuid']: dict(r) for r in rows if r['csuid']}
        unique = {r[0]: r[1] for r in c.execute('SELECT csuid,count(*) FROM buildings WHERE active=1 GROUP BY csuid')}
        candidates = collections.defaultdict(list)
        manifests = sorted(root.glob('source-scripts/city/*/staged/*/manifest.json'))
        original = root/'docs/astra-city/mui-wo-buildings/review/model-sample/manifest.json'
        if original.exists():
            manifests.append(original)
        for path in manifests:
            manifest = json.loads(path.read_bytes())
            for spec in manifest['models']:
                cs = spec.get('officialBuildingCSUIDs', [])
                for identity in cs:
                    if identity in by_csuid:
                        candidates[by_csuid[identity]['uid']].append(dict(
                            manifest=str(path.relative_to(root)), spec=spec, tile=manifest['tile'],
                            revision=manifest['tileRevision'], sourceArchiveSHA256=manifest['sourceArchiveSha256']))
        # Reuse existing compact assets, including held ones: reuse is NOT placement approval.
        compact = collections.defaultdict(list)
        for path in sorted(root.glob('source-scripts/city/*/compact/catalogue.json')):
            for model in json.loads(path.read_bytes()).get('models', []):
                if model.get('asset'):
                    compact[(model['uid'], model['modelId'], model['sourceTileRevision'])].append(
                        dict(record=model, file=str((path.parent/model['asset']).relative_to(root))))
        jobs = []
        counts = collections.Counter()
        tools = tool_hash(root)
        for b in rows:
            b = dict(b)
            options = candidates[b['uid']]
            status = None
            if not b['csuid']:
                status = 'no-government-identity'
            elif unique.get(b['csuid']) != 1:
                status = 'ambiguous-building-components'
            elif not options:
                status = 'not-in-retained-staged-models'
            elif len({s['spec']['id'] for s in options}) != 1:
                status = 'multiple-source-model-identities'
            elif any(len(s['spec']['officialBuildingCSUIDs']) != 1 for s in options):
                status = 'multiple-official-footprint-matches'
            options.sort(key=lambda o: (o['revision'], o['tile'], o['manifest']), reverse=True)
            candidate = options[0] if options and status is None else None
            if candidate:
                same_revision = [s for s in options if s['revision'] == candidate['revision']]
                if len({encode(s['spec']['sourceHashes']) for s in same_revision}) != 1:
                    status = 'conflicting-same-revision-source-bytes'
                    candidate = None
            reuse = compact.get((b['uid'], candidate['spec']['id'], candidate['revision']), []) if candidate else []
            payload = dict(building=b, candidate=candidate, priorCompact=reuse,
                           disposition=status or 'match-and-pack', toolSHA256=tools)
            fingerprint = digest(encode(payload).encode())
            key = digest((b['uid']+'cached-model-v1'+fingerprint).encode())
            payload['jobKey'] = key
            jobs.append((key, b['uid'], 'cached-model-v1', fingerprint, encode(payload)))
            counts[payload['disposition']] += 1
        set_name = selection+':cached-models'
        existing = {r['id']: r['status'] for r in c.execute('SELECT id,status FROM batch_jobs')}
        report = dict(selection=selection, jobSet=set_name, cachedSheetManifests=len(manifests),
                      jobs=len(jobs), dispositions=dict(counts), alreadyComplete=sum(existing.get(j[0]) == 'complete' for j in jobs),
                      newJobs=sum(j[0] not in existing for j in jobs), dryRun=dry_run,
                      qualification='Cache coverage only; absence here does not prove absence in government datasets.')
        if not dry_run:
            with c:
                c.execute('DELETE FROM batch_job_sets WHERE name=?', (set_name,))
                c.executemany('INSERT OR IGNORE INTO batch_jobs(id,uid,stage,fingerprint,payload) VALUES(?,?,?,?,?)', jobs)
                c.executemany('INSERT INTO batch_job_sets VALUES(?,?)', [(set_name, j[0]) for j in jobs])
                c.execute('INSERT OR REPLACE INTO batch_plans VALUES(?,?)',
                          (set_name, digest((selected['config_sha256']+gen+tools).encode())))
        return report
    finally:
        c.close()


class Processor:
    def __init__(self, root, out, max_input_bytes=32*1024**2, max_output_bytes=1024**3):
        self.root, self.out = pathlib.Path(root).resolve(), pathlib.Path(out).resolve()
        if self.out.is_relative_to(self.root/'3d-viewer'):
            raise ValueError('Candidate output must stay outside the live viewer')
        self.max_input_bytes, self.max_output_bytes = max_input_bytes, max_output_bytes
        self.lock = threading.Lock()
        self.out.mkdir(parents=True, exist_ok=True)
        self.output_bytes = sum(p.stat().st_size for p in self.out.glob('*.glb.gz'))
        # Reuse the original decoder and exact-bit packer; no second geometry converter.
        sys.path.insert(0, str(self.root/'docs/astra-city/mui-wo-buildings/review'))
        from prepare_model_sample import model_geometry
        self.geometry = model_geometry
        spec = importlib.util.spec_from_file_location('astra_shared_pack', self.root/TOOL_PATHS[0])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.pack = module.pack

    def __call__(self, payload):
        b = payload['building']
        if payload['disposition'] != 'match-and-pack':
            return dict(outcome=payload['disposition'], nextAction='source-review-or-acquisition', uid=b['uid'])
        candidate = payload['candidate']
        spec = candidate['spec']
        if spec['officialBuildingCSUIDs'] != [b['csuid']] or not any(m['objectId'] == b['object_id'] for m in spec['officialMatches']):
            raise ValueError('Source identity mismatch')
        folder = safe(self.root, candidate['manifest']).parent
        source = safe(folder, spec['sourceEntry'])
        sizes = sum(safe(folder, p).stat().st_size for p in spec['sourceHashes'])
        if sizes > self.max_input_bytes or spec['vertices'] > 500000:
            return dict(outcome='per-model-resource-limit', uid=b['uid'], sourceBytes=sizes, nextAction='review-resource-budget')
        check_source(self.root, candidate)
        if spec['sourceEntry'] not in spec['sourceHashes']:
            raise ValueError('Source glTF lacks recorded hash')
        data = json.loads(source.read_bytes())
        for buffer in data.get('buffers', []):
            path = safe(source.parent, buffer['uri'])
            if str(path.relative_to(folder)) not in spec['sourceHashes']:
                raise ValueError('Source buffer missing from provenance hashes')
        positions, triangles = self.geometry(data, lambda uri: safe(source.parent, uri).read_bytes())
        if triangles != spec['triangles']:
            raise ValueError('Source triangle count mismatch')
        from shapely.geometry import MultiPoint, Polygon
        from shapely import make_valid
        hull = MultiPoint(positions[:, [0, 2]]).convex_hull
        rings = json.loads(b['rings_json'])
        footprint = Polygon(rings[0], rings[1:])
        if not footprint.is_valid:
            footprint = make_valid(footprint)
        area = min(hull.area, footprint.area)
        overlap = hull.intersection(footprint).area/area if area > 0 else 0
        distance = hull.centroid.distance(footprint.centroid)
        proof = dict(overlapOfSmallerFootprint=overlap, centroidDistanceMetres=distance,
                     sourceManifest=candidate['manifest'], sourceHashes=spec['sourceHashes'],
                     sourceArchiveSHA256=candidate['sourceArchiveSHA256'])
        if overlap < .5 or distance > 10:
            return dict(uid=b['uid'], outcome='current-footprint-match-failed', nextAction='source-identity-review', proof=proof)
        compressed = record = None
        reused = False
        for cached in payload['priorCompact']:
            rec = cached['record']
            if (rec.get('buildingCSUID') != b['csuid'] or rec.get('objectId') != b['object_id']
                    or rec.get('sourceTile') != candidate['tile'] or rec.get('triangles') != triangles
                    or rec.get('worldBounds') != spec['worldBounds']):
                continue
            path = safe(self.root, cached['file'])
            if not path.exists() or path.stat().st_size != rec['bytes']:
                continue
            raw = path.read_bytes()
            if digest(raw) == rec['sha256']:
                compressed, record, reused = raw, dict(rec), True
                proof['reusedCompactFile'] = cached['file']
                break
        if compressed is None:
            glb, stats = self.pack(source)
            if stats['triangles'] != triangles:
                raise ValueError('Packed triangle count mismatch')
            compressed = gzip.compress(glb, mtime=0)
            record = dict(encoding='gzip', bytes=len(compressed), sha256=digest(compressed),
                          glbBytes=len(glb), decodedGeometryBytes=stats['decodedGeometryBytes'],
                          indexedVertices=stats['vertices'], triangles=triangles)
        dest = self.out/(record['sha256']+'.glb.gz')
        with self.lock:
            if not dest.exists():
                if self.output_bytes+len(compressed) > self.max_output_bytes:
                    return dict(uid=b['uid'], outcome='output-resource-limit', nextAction='review-resource-budget')
                tmp = dest.with_suffix('.'+uuid.uuid4().hex+'.tmp')
                tmp.write_bytes(compressed)
                tmp.replace(dest)
                self.output_bytes += len(compressed)
            elif digest(dest.read_bytes()) != record['sha256']:
                # Recreate a corrupt derivative from verified source; source stays untouched.
                tmp = dest.with_suffix('.'+uuid.uuid4().hex+'.tmp')
                tmp.write_bytes(compressed)
                tmp.replace(dest)
        record.update(uid=b['uid'], buildingCSUID=b['csuid'], objectId=b['object_id'], modelId=spec['id'],
                      sourceTile=candidate['tile'], sourceTileRevision=candidate['revision'],
                      worldBounds=spec['worldBounds'], recordedBaseHeight=b['source_base'], recordedTopHeight=b['source_top'],
                      structureType=b['structure_type'], label=b['name'] or spec['id'], priority='unreviewed',
                      placementReviewed=False, asset=dest.name)
        return dict(uid=b['uid'], outcome='staged-needs-placement-review', nextAction='fresh-terrain-and-browser-validation',
                    record=record, proof=proof, reusedCompact=reused, liveReplacement=False)


def run_stage(db, root, out, selection, workers=2, limit=10000, max_output_bytes=1024**3, retry_failed=False):
    if max_output_bytes <= 0:
        raise ValueError('Output budget must be positive')
    root = pathlib.Path(root).resolve()
    c = connect(db)
    name = selection+':cached-models'
    try:
        s = c.execute('SELECT * FROM selection_sets WHERE name=?', (selection,)).fetchone()
        p = c.execute('SELECT fingerprint FROM batch_plans WHERE name=?', (name,)).fetchone()
        gen = generation(c)
        if not s or not p or s['inventory_sha256'] != gen or p[0] != digest((s['config_sha256']+gen+tool_hash(root)).encode()):
            raise ValueError('Plan stale: refresh selection and cached model plan')
        # Missing/corrupt outputs must not remain silently complete on resume.
        for job in c.execute("SELECT j.* FROM batch_jobs j JOIN batch_job_sets s ON j.id=s.id WHERE s.name=? AND j.status='complete'", (name,)).fetchall():
            result = json.loads(job['result'])
            if 'record' in result:
                check_source(root, json.loads(job['payload'])['candidate'])
                rec = result['record']
                asset = pathlib.Path(out)/rec['asset']
                if not asset.exists() or digest(asset.read_bytes()) != rec['sha256']:
                    c.execute("UPDATE batch_jobs SET status='pending',attempts=0,result=NULL WHERE id=?", (job['id'],))
        if retry_failed:
            c.execute("UPDATE batch_jobs SET status='pending',attempts=0,error=NULL WHERE status='failed' AND id IN (SELECT id FROM batch_job_sets WHERE name=?)", (name,))
        c.commit()
    finally:
        c.close()
    result = execute_jobs(db, name, Processor(root, out, max_output_bytes=max_output_bytes), workers, limit)
    c = connect(db)
    try:
        outcomes = collections.Counter()
        models, proofs, exceptions = [], [], []
        reused = 0
        for job in c.execute('SELECT j.* FROM batch_jobs j JOIN batch_job_sets s ON j.id=s.id WHERE s.name=? ORDER BY j.uid', (name,)):
            if job['status'] == 'failed':
                exceptions.append(dict(uid=job['uid'], outcome='job-failed', error=job['error']))
            if job['result']:
                r = json.loads(job['result'])
                outcomes[r['outcome']] += 1
                if 'record' in r:
                    models.append(r['record'])
                    proofs.append(dict(uid=r['uid'], **r['proof']))
                    reused += int(r['reusedCompact'])
                else:
                    exceptions.append(r)
        result = dict(jobSet=name, status=result['status'], outcomes=dict(outcomes), seconds=result['seconds'],
                      candidateModels=len(models), reusedCompact=reused, newLiveModels=0,
                      aiCalls=0, networkRequests=0, qualification='Staged identity matches; fresh placement and browser acceptance required.')
        out = pathlib.Path(out)
        catalogue = dict(schemaVersion=1, kind='staged-official-model-catalogue', area=selection,
                         datasetId='landsd_rcd_1742809441342_98380',
                         coordinatePolicy='Native source nodes and exact indexed attributes; apply root translation once. No terrain draping or height correction.',
                         loadingPolicy='Staging only. Retain the basic building until placement and browser acceptance.',
                         crs='EPSG:2326', verticalDatum='Hong Kong Principal Datum', rootTranslation=[-834500, 0, 816500],
                         counts=dict(packedModels=len(models)), models=models)
        # Keep the review inventory separate from bounded viewer-compatible catalogues.
        chunks = []
        outputs = [('catalogue.json', catalogue), ('proofs.json', proofs), ('exceptions.json', exceptions), ('report.json', result)]
        for offset in range(0, len(models), 1024):
            name = f'catalogue-{offset//1024:03d}.json'
            part = models[offset:offset+1024]
            outputs.append((name, dict(catalogue, counts=dict(packedModels=len(part)), models=part)))
            chunks.append(name)
        outputs.append(('catalogue-index.json', dict(schemaVersion=1, staged=True, catalogues=chunks, models=len(models))))
        for filename, data in outputs:
            temp = out/(filename+'.tmp')
            temp.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
            temp.replace(out/filename)
        return result
    finally:
        c.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['plan', 'run'])
    p.add_argument('--root', type=pathlib.Path, default=DEFAULT_ROOT)
    p.add_argument('--db', type=pathlib.Path, default=HERE/'local/buildings.sqlite')
    p.add_argument('--out', type=pathlib.Path, default=HERE/'local/candidates')
    p.add_argument('--selection', default='tourist-trial-v1')
    p.add_argument('--workers', type=int, default=2)
    p.add_argument('--limit', type=int, default=10000)
    p.add_argument('--max-output-mib', type=int, default=1024)
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--retry-failed', action='store_true', help='Explicitly retry failed jobs after correcting their inputs')
    args = p.parse_args()
    if args.dry_run and args.command != 'plan':
        p.error('--dry-run applies only to plan')
    result = prepare(args.db, args.root, args.selection, args.dry_run) if args.command == 'plan' else run_stage(
        args.db, args.root, args.out, args.selection, args.workers, args.limit, args.max_output_mib*1024**2, args.retry_failed)
    print(json.dumps(result, indent=2))
