#!/usr/bin/env python3
"""Lossless, immutable SQLite inventory snapshots in PostgreSQL; bounded-memory restore.

Only ``import`` creates PostgreSQL records. Historical job rows do not enter the
shared runnable queue. Source SQLite is held in a read transaction for all scans.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import sqlite3
import uuid

FORMAT_VERSION = 1
BATCH_SIZE = 1000


def packed(value):
    return json.dumps(value, ensure_ascii=True, separators=(',', ':'), allow_nan=False)


def quote(name):
    return '"' + name.replace('"', '""') + '"'


def encode(value):
    if isinstance(value, bytes):
        return {'blob': base64.b64encode(value).decode('ascii')}
    if isinstance(value, float):
        # Hex preserves signed zero, infinities, and every finite IEEE754 bit value.
        return {'float': value.hex()}
    return value


def decode(value):
    if isinstance(value, dict):
        if set(value) == {'blob'}:
            return base64.b64decode(value['blob'], validate=True)
        if set(value) == {'float'}:
            return float.fromhex(value['float'])
        raise ValueError('Unknown encoded SQLite value')
    return value


def open_source(path):
    path = Path(path).resolve(strict=True)
    conn = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
    conn.execute('BEGIN')
    return conn


def schema_info(conn):
    objects = conn.execute("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type,name").fetchall()
    virtual = {name for kind, name, _, sql in objects
               if kind == 'table' and sql.upper().startswith('CREATE VIRTUAL TABLE')}
    # Use SQLite's own shadow classification rather than guessing every virtual
    # table's implementation. Only Rtree is supported by this snapshot format.
    unsupported = [name for kind, name, _, sql in objects if name in virtual and 'USING RTREE' not in sql.upper()]
    if unsupported:
        raise ValueError(f'Unsupported virtual tables: {unsupported}')
    shadow = {row[1] for row in conn.execute('PRAGMA table_list') if row[2] == 'shadow'}
    # Compatibility with older SQLite libraries without PRAGMA table_list.
    for name in virtual:
        shadow.update(name + suffix for suffix in ('_node', '_parent', '_rowid'))
    objects = [list(row) for row in objects if row[1] not in shadow and not row[1].startswith('sqlite_')]
    tables = []
    for kind, name, _, sql in objects:
        if kind != 'table':
            continue
        column_info = list(conn.execute(f'PRAGMA table_xinfo({quote(name)})'))
        columns = [r[1] for r in column_info if r[6] == 0]
        primary_key = [r[1] for r in sorted(column_info, key=lambda r: r[5]) if r[5]]
        without_rowid = 'WITHOUT ROWID' in sql.upper()
        rowid_alias = None
        if not without_rowid and name not in virtual:
            rowid_alias = next((a for a in ('rowid', '_rowid_', 'oid') if a.lower() not in {c.lower() for c in columns}), None)
            if rowid_alias is None:
                raise ValueError(f'{name}: all rowid aliases shadowed; refusing lossy snapshot')
        tables.append({'name': name, 'columns': columns, 'rowid_alias': rowid_alias,
                       'virtual': name in virtual, 'without_rowid': without_rowid, 'primary_key': primary_key})
    if conn.execute("SELECT 1 FROM sqlite_master WHERE name='sqlite_sequence'").fetchone():
        tables.append({'name': 'sqlite_sequence', 'columns': ['name', 'seq'],
                       'rowid_alias': 'rowid', 'virtual': False, 'without_rowid': False, 'primary_key': ['name']})
    return {'objects': objects, 'tables': sorted(tables, key=lambda t: t['name']),
            'user_version': conn.execute('PRAGMA user_version').fetchone()[0],
            'application_id': conn.execute('PRAGMA application_id').fetchone()[0]}


def source_rows(conn, table):
    cols = table['columns']
    expressions = ([table['rowid_alias']] if table['rowid_alias'] else []) + cols
    order = [table['rowid_alias']] if table['rowid_alias'] else cols
    cursor = conn.execute(f'SELECT {",".join(quote(c) for c in expressions)} FROM {quote(table["name"])} ORDER BY {",".join(quote(c) for c in order)}')
    for row in cursor:
        yield packed([encode(value) for value in row])


def source_key(table, row_json):
    values = json.loads(row_json)
    columns = ([table['rowid_alias']] if table['rowid_alias'] else []) + table['columns']
    # Nullable SQLite text primary keys need rowid fallback; null PK rows are not
    # unique in ordinary SQLite tables. Include a discriminator in every key.
    keys = table['primary_key']
    if keys and all(values[columns.index(key)] is not None for key in keys):
        return packed({'primary_key': [[key, values[columns.index(key)]] for key in keys]})
    if table['rowid_alias']:
        return packed({'rowid': values[0]})
    # Rtree's first column is its integer id even though table_info has no PK bit.
    if table['virtual']:
        return packed({'virtual_id': values[0]})
    raise ValueError(f'{table["name"]}: cannot identify source row')


def lookup_row(pg, snapshot_id, table_name, key):
    """Key is {primary_key: [[column, encoded_value], ...]} or {rowid: int}."""
    key_json = packed(key)
    rows = pg.execute('SELECT row_json FROM astra_modelling.inventory_rows WHERE snapshot_id=%s AND table_name=%s AND source_key_sha256=%s AND source_key_json=%s',
                      (snapshot_id, table_name, hashlib.sha256(key_json.encode()).hexdigest(), key_json)).fetchall()
    if len(rows) > 1:
        raise ValueError('Ambiguous inventory source key')
    return [decode(value) for value in json.loads(rows[0][0])] if rows else None


def digest_rows(rows):
    digest = hashlib.sha256()
    count = 0
    for row in rows:
        digest.update(row.encode('utf-8'))
        digest.update(b'\n')
        count += 1
    return count, digest.hexdigest()


def inspect_source(conn):
    schema = schema_info(conn)
    tables = []
    for table in schema['tables']:
        count, digest = digest_rows(source_rows(conn, table))
        tables.append({'metadata': table, 'row_count': count, 'content_sha256': digest})
    identity = {'format_version': FORMAT_VERSION, 'schema': schema, 'tables': tables}
    return {**identity, 'snapshot_id': hashlib.sha256(packed(identity).encode()).hexdigest(),
            'row_count': sum(t['row_count'] for t in tables)}


def pg_rows(pg, snapshot_id, table):
    table_name = table["name"]
    # Named server cursor prevents psycopg buffering an entire city in memory.
    with pg.cursor(name='inventory_' + uuid.uuid4().hex) as cursor:
        cursor.itersize = BATCH_SIZE
        cursor.execute('SELECT ordinal,row_json,source_key_json,source_key_sha256 FROM astra_modelling.inventory_rows WHERE snapshot_id=%s AND table_name=%s ORDER BY ordinal', (snapshot_id, table_name))
        expected = 0
        for ordinal, row_json, key_json, key_hash in cursor:
            if ordinal != expected:
                raise ValueError(f'{table_name}: missing or unordered row {expected}')
            expected += 1
            canonical_key = source_key(table, row_json)
            if key_json != canonical_key or key_hash != hashlib.sha256(canonical_key.encode()).hexdigest():
                raise ValueError(f'{table_name}: source key mismatch at row {ordinal}')
            yield row_json


def load_snapshot(pg, snapshot_id):
    row = pg.execute('SELECT format_version,schema_json,row_count FROM astra_modelling.inventory_snapshots WHERE snapshot_id=%s', (snapshot_id,)).fetchone()
    if not row:
        raise ValueError(f'Unknown inventory snapshot {snapshot_id}')
    version, schema_json, total = row
    if version != FORMAT_VERSION:
        raise ValueError(f'Unsupported snapshot format {version}')
    schema = json.loads(schema_json)
    tables = []
    for name, metadata_json, digest, count in pg.execute('SELECT table_name,metadata_json,content_sha256,row_count FROM astra_modelling.inventory_tables WHERE snapshot_id=%s ORDER BY table_name', (snapshot_id,)):
        metadata = json.loads(metadata_json)
        if metadata['name'] != name:
            raise ValueError('Snapshot table metadata mismatch')
        tables.append({'metadata': metadata, 'row_count': count, 'content_sha256': digest})
    identity = {'format_version': version, 'schema': schema, 'tables': tables}
    if hashlib.sha256(packed(identity).encode()).hexdigest() != snapshot_id:
        raise ValueError('Snapshot manifest fingerprint mismatch')
    if total != sum(t['row_count'] for t in tables) or schema['tables'] != [t['metadata'] for t in tables]:
        raise ValueError('Snapshot table manifest incomplete')
    return {**identity, 'snapshot_id': snapshot_id, 'row_count': total}


def verify_stored(pg, snapshot):
    for table in snapshot['tables']:
        count, digest = digest_rows(pg_rows(pg, snapshot['snapshot_id'], table['metadata']))
        if (count, digest) != (table['row_count'], table['content_sha256']):
            raise ValueError(f'Snapshot content mismatch: {table["metadata"]["name"]}')
    return snapshot


def import_snapshot(pg, sqlite_path):
    source = open_source(sqlite_path)
    try:
        snapshot = inspect_source(source)
        sid = snapshot['snapshot_id']
        with pg.transaction():
            pg.execute('SELECT pg_advisory_xact_lock(%s)', (217002,))
            pg.execute(Path(__file__).with_name('inventory-schema.sql').read_text())
        with pg.transaction():
            # Serialise only importers of this exact snapshot, not runnable jobs.
            pg.execute('SELECT pg_advisory_xact_lock(%s)', (int(sid[:15], 16),))
            if pg.execute('SELECT 1 FROM astra_modelling.inventory_snapshots WHERE snapshot_id=%s', (sid,)).fetchone():
                verify_stored(pg, load_snapshot(pg, sid))
                return {'snapshot_id': sid, 'row_count': snapshot['row_count'], 'reused': True}
            pg.execute('INSERT INTO astra_modelling.inventory_snapshots(snapshot_id,format_version,schema_json,source_label,row_count) VALUES (%s,%s,%s,%s,%s)',
                       (sid, FORMAT_VERSION, packed(snapshot['schema']), Path(sqlite_path).name, snapshot['row_count']))
            for table in snapshot['tables']:
                metadata = table['metadata']
                pg.execute('INSERT INTO astra_modelling.inventory_tables(snapshot_id,table_name,metadata_json,content_sha256,row_count) VALUES (%s,%s,%s,%s,%s)',
                           (sid, metadata['name'], packed(metadata), table['content_sha256'], table['row_count']))
                with pg.cursor() as cursor:
                    with cursor.copy('COPY astra_modelling.inventory_rows(snapshot_id,table_name,ordinal,row_json,source_key_json,source_key_sha256) FROM STDIN') as copy:
                        for ordinal, row in enumerate(source_rows(source, metadata)):
                            key = source_key(metadata, row)
                            copy.write_row((sid, metadata['name'], ordinal, row, key, hashlib.sha256(key.encode()).hexdigest()))
            verify_stored(pg, snapshot)
        return {'snapshot_id': sid, 'row_count': snapshot['row_count'], 'reused': False}
    finally:
        source.close()


def restore_sqlite(snapshot, row_provider, destination):
    """Write a new SQLite file, verify logical equality, then atomically publish it."""
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(f'Refusing to overwrite {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + '.' + uuid.uuid4().hex + '.tmp')
    conn = sqlite3.connect(temporary)
    try:
        conn.execute('BEGIN')
        schema = snapshot['schema']
        for kind, _, _, sql in schema['objects']:
            if kind == 'table':
                conn.execute(sql)
        for entry in sorted(snapshot['tables'], key=lambda item: item['metadata']['name'] == 'sqlite_sequence'):
            table = entry['metadata']
            if table['name'] == 'sqlite_sequence':
                # AUTOINCREMENT imports update this implicit table themselves.
                conn.execute('DELETE FROM sqlite_sequence')
            columns = ([table['rowid_alias']] if table['rowid_alias'] else []) + table['columns']
            statement = f'INSERT INTO {quote(table["name"])} ({",".join(quote(c) for c in columns)}) VALUES ({",".join("?" for _ in columns)})'
            digest = hashlib.sha256()
            count = 0
            for row_json in row_provider(table['name']):
                digest.update(row_json.encode('utf-8') + b'\n')
                conn.execute(statement, [decode(v) for v in json.loads(row_json)])
                count += 1
            if (count, digest.hexdigest()) != (entry['row_count'], entry['content_sha256']):
                raise ValueError(f'Snapshot content mismatch: {table["name"]}')
        for kind, _, _, sql in schema['objects']:
            if kind != 'table':
                conn.execute(sql)
        conn.execute(f'PRAGMA user_version={int(schema["user_version"])}')
        conn.execute(f'PRAGMA application_id={int(schema["application_id"])}')
        conn.commit()
        if conn.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
            raise ValueError('Restored SQLite integrity check failed')
        restored = inspect_source(conn)
        if restored['snapshot_id'] != snapshot['snapshot_id']:
            raise ValueError('Restored SQLite schema/content fingerprint mismatch')
        conn.close()
        # Hard-link publication is atomic and cannot clobber a concurrently created file.
        import os
        os.link(temporary, destination)
        temporary.unlink()
        return {'snapshot_id': snapshot['snapshot_id'], 'row_count': snapshot['row_count'], 'sqlite': str(destination)}
    except BaseException:
        conn.close()
        temporary.unlink(missing_ok=True)
        raise


def export_snapshot(pg, snapshot_id, destination):
    with pg.transaction():
        snapshot = load_snapshot(pg, snapshot_id)
        tables = {entry['metadata']['name']: entry['metadata'] for entry in snapshot['tables']}
        return restore_sqlite(snapshot, lambda name: pg_rows(pg, snapshot_id, tables[name]), destination)


def verify_snapshot(pg, snapshot_id, sqlite_path):
    with pg.transaction():
        snapshot = verify_stored(pg, load_snapshot(pg, snapshot_id))
        source = open_source(sqlite_path)
        try:
            local = inspect_source(source)
        finally:
            source.close()
        if local['snapshot_id'] != snapshot_id:
            raise ValueError('SQLite does not match the stored snapshot')
        return {'snapshot_id': snapshot_id, 'row_count': snapshot['row_count'], 'verified': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('import', 'export', 'verify', 'inspect'):
        item = sub.add_parser(command)
        item.add_argument('--sqlite', type=Path, required=True)
        if command in ('export', 'verify'):
            item.add_argument('--snapshot', required=True)
    args = parser.parse_args()
    if args.command == 'inspect':
        source = open_source(args.sqlite)
        try:
            result = inspect_source(source)
            result = {'snapshot_id': result['snapshot_id'], 'row_count': result['row_count'],
                      'tables': {t['metadata']['name']: t['row_count'] for t in result['tables']}}
        finally:
            source.close()
    else:
        from db import connect
        with connect() as pg:
            if args.command == 'import':
                result = import_snapshot(pg, args.sqlite)
            elif args.command == 'export':
                result = export_snapshot(pg, args.snapshot, args.sqlite)
            else:
                result = verify_snapshot(pg, args.snapshot, args.sqlite)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
