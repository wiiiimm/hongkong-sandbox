#!/usr/bin/env python3
"""Local, incremental inventory of published Astra buildings. No network or AI calls."""
import argparse
import hashlib
import json
import pathlib
import sqlite3
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS inputs(path TEXT PRIMARY KEY,sha256 TEXT NOT NULL,kind TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS buildings(
 uid TEXT PRIMARY KEY,source_id TEXT,object_id INTEGER,csuid TEXT,name TEXT,zh TEXT,
 tile TEXT NOT NULL,input_path TEXT NOT NULL,source_dataset TEXT,
 x REAL NOT NULL,z REAL NOT NULL,base REAL,height REAL,height_source TEXT,
 source_base REAL,source_top REAL,structure_type TEXT,
 rings_json TEXT NOT NULL,metadata_json TEXT NOT NULL,embedded INTEGER NOT NULL,
 active INTEGER NOT NULL DEFAULT 1);
CREATE INDEX IF NOT EXISTS building_location ON buildings(x,z);
CREATE INDEX IF NOT EXISTS building_object ON buildings(object_id);
CREATE INDEX IF NOT EXISTS building_input ON buildings(input_path);
CREATE TABLE IF NOT EXISTS models(
 uid TEXT PRIMARY KEY REFERENCES buildings(uid),catalogue TEXT NOT NULL,
 asset TEXT NOT NULL,sha256 TEXT NOT NULL,metadata_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS selections(
 selection TEXT NOT NULL,uid TEXT NOT NULL,reason TEXT NOT NULL,
 priority INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(selection,uid));
CREATE TABLE IF NOT EXISTS reviews(
 uid TEXT PRIMARY KEY,status TEXT NOT NULL DEFAULT 'unreviewed',notes TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS sections(id TEXT PRIMARY KEY,definition_json TEXT NOT NULL);
"""


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local(viewer, relative):
    path = (viewer / relative).resolve()
    if not path.is_relative_to(viewer.resolve()):
        raise ValueError(f'Input escapes viewer: {relative}')
    return path


def sync(viewer, database):
    started = time.monotonic()
    viewer = pathlib.Path(viewer).resolve()
    database = pathlib.Path(database)
    database.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(database, timeout=30)
    con.execute('PRAGMA foreign_keys=ON')
    try:
        con.executescript(SCHEMA)
        version = con.execute("SELECT value FROM settings WHERE key='schema'").fetchone()
        if version and version[0] != '1':
            raise ValueError('Unsupported inventory schema')
        con.execute('BEGIN IMMEDIATE')
        con.execute("INSERT OR IGNORE INTO settings VALUES('schema','1')")
        files = {}

        def read(relative, kind):
            if relative in files:
                raise ValueError(f'Duplicate manifest input: {relative}')
            raw = local(viewer, relative).read_bytes()
            sha = digest(raw)
            files[relative] = (sha, kind)
            old = con.execute('SELECT sha256 FROM inputs WHERE path=?', (relative,)).fetchone()
            return raw, not old or old[0] != sha

        raw, _ = read('city/data/manifest.json', 'manifest')
        manifest = json.loads(raw)
        changed, skipped = [], 0
        for tile in manifest['tiles']:
            raw, differs = read(tile['url'], 'tile')
            if differs:
                changed.append((tile, files[tile['url']][0]))
            else:
                skipped += 1
        # Deactivate all replaced/removed inputs first, allowing legitimate moves
        # between tiles. Historical selection/review records remain untouched.
        active_paths = {t['url'] for t in manifest['tiles']}
        changed_paths = {t['url'] for t, _ in changed}
        for (path,) in con.execute("SELECT path FROM inputs WHERE kind='tile'").fetchall():
            if path not in active_paths or path in changed_paths:
                con.execute('UPDATE buildings SET active=0 WHERE input_path=?', (path,))
        updated = 0
        columns = [r[1] for r in con.execute('PRAGMA table_info(buildings)')]
        update = ','.join(f'{c}=excluded.{c}' for c in columns[1:])
        for tile, expected_sha in changed:
            raw = local(viewer, tile['url']).read_bytes()
            if digest(raw) != expected_sha:
                raise ValueError(f'Input changed during import: {tile["url"]}')
            data = json.loads(raw)
            if data['id'] != tile['id'] or len(data['buildings']) != tile['counts']['buildings']:
                raise ValueError(f'Tile count/identity mismatch: {tile["id"]}')
            for b in data['buildings']:
                if b['tile'] != tile['id']:
                    raise ValueError(f'Wrong building tile: {b["uid"]}')
                if con.execute('SELECT 1 FROM buildings WHERE uid=? AND active=1', (b['uid'],)).fetchone():
                    raise ValueError(f'Duplicate active UID: {b["uid"]}')
                metadata = {k: v for k, v in b.items() if k not in ('rings', 'modelGeometry')}
                # Embedded geometry stays in its tile; keep an exact content fingerprint.
                if b.get('modelGeometry'):
                    metadata['inventoryModelSHA256'] = digest(encode(b['modelGeometry']).encode())
                values = (b['uid'], b.get('id'), b.get('objectId'), b.get('buildingCSUID'),
                          b.get('name', ''), b.get('zh', ''), b['tile'], tile['url'],
                          b.get('sourceDataset'), *b['centre'], b.get('base'), b.get('height'),
                          b.get('heightSource'), b.get('baseHeightHKPD'), b.get('topHeightHKPD'),
                          b.get('structureType'), encode(b['rings']), encode(metadata),
                          int(bool(b.get('modelGeometry'))), 1)
                con.execute(f'INSERT INTO buildings VALUES({",".join("?" for _ in values)}) '
                            f'ON CONFLICT(uid) DO UPDATE SET {update}', values)
                updated += 1
        # Reconcile model identity even if the catalogue itself is unchanged.
        con.execute('DELETE FROM models')
        checked_assets = skipped_assets = 0
        for catalogue in manifest.get('officialModelCatalogues', []):
            raw, _ = read(catalogue, 'catalogue')
            for model in json.loads(raw)['models']:
                row = con.execute('SELECT object_id,csuid,embedded FROM buildings WHERE uid=? AND active=1',
                                  (model['uid'],)).fetchone()
                if not row or row[0] != model['objectId'] or row[1] != model['buildingCSUID'] or row[2]:
                    raise ValueError(f'Model identity/embedded conflict: {model["uid"]}')
                relative = str(pathlib.PurePosixPath(catalogue).parent / model['asset'])
                raw, differs = read(relative, 'asset')
                if digest(raw) != model['sha256'] or len(raw) != model['bytes']:
                    raise ValueError(f'Model asset checksum/size mismatch: {relative}')
                checked_assets += int(differs)
                skipped_assets += int(not differs)
                con.execute('INSERT INTO models VALUES(?,?,?,?,?)',
                            (model['uid'], catalogue, relative, model['sha256'], encode(model)))
        raw, _ = read('city/data/review-sections.json', 'sections')
        sections = json.loads(raw)['sections']
        con.execute('DELETE FROM sections')
        con.executemany('INSERT INTO sections VALUES(?,?)', [(s['id'], encode(s)) for s in sections])
        count, embedded = con.execute('SELECT count(*),coalesce(sum(embedded),0) FROM buildings WHERE active=1').fetchone()
        if count != manifest['counts']['buildings']:
            raise ValueError(f'Manifest count mismatch: {count} != {manifest["counts"]["buildings"]}')
        con.execute('DELETE FROM inputs')
        con.executemany('INSERT INTO inputs VALUES(?,?,?)', [(p, sha, kind) for p, (sha, kind) in files.items()])
        con.execute("INSERT OR REPLACE INTO settings VALUES('source_manifest_sha256',?)",
                    (files['city/data/manifest.json'][0],))
        con.execute("INSERT OR REPLACE INTO settings VALUES('source_manifest_json',?)", (encode(manifest),))
        progressive = con.execute('SELECT count(*) FROM models').fetchone()[0]
        source_ids = con.execute('SELECT count(DISTINCT object_id) FROM buildings WHERE active=1').fetchone()[0]
        con.commit()
        return dict(buildings=count, governmentSourceIDs=source_ids, embeddedModels=embedded,
                    progressiveModels=progressive, sections=len(sections), changedTiles=len(changed),
                    skippedTiles=skipped, updatedBuildings=updated, changedAssets=checked_assets,
                    unchangedAssets=skipped_assets, seconds=round(time.monotonic()-started, 2),
                    databaseBytes=database.stat().st_size, aiCalls=0, networkRequests=0)
    except BaseException:
        con.rollback()
        raise
    finally:
        con.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--viewer', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[3]/'3d-viewer')
    parser.add_argument('--db', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parent/'local'/'buildings.sqlite')
    args = parser.parse_args()
    print(json.dumps(sync(args.viewer, args.db), indent=2))
