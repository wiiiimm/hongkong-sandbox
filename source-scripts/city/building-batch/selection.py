"""Versioned footprint selections over the local inventory. Requires existing Shapely."""
import argparse
import html
import json
import pathlib
import sqlite3
import time
from shapely.geometry import Polygon, box
from shapely import make_valid
from inventory import digest, encode

SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS footprint_bounds USING rtree(id,min_x,max_x,min_z,max_z);
CREATE TABLE IF NOT EXISTS selection_sets(name TEXT PRIMARY KEY,config_json TEXT NOT NULL,
 config_sha256 TEXT NOT NULL,inventory_sha256 TEXT NOT NULL,summary_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS selection_members(name TEXT NOT NULL,uid TEXT NOT NULL,
 reasons_json TEXT NOT NULL,priority INTEGER NOT NULL,PRIMARY KEY(name,uid));
"""


def shape(rings):
    geom = Polygon(rings[0], rings[1:])
    # Only the intersection geometry is repaired; stored source rings are untouched.
    return geom if geom.is_valid else make_valid(geom)


def select(database, config):
    started = time.monotonic()
    con = sqlite3.connect(database)
    con.row_factory = sqlite3.Row
    try:
        con.executescript(SCHEMA)
        con.execute('BEGIN IMMEDIATE')
        generation = con.execute("SELECT value FROM settings WHERE key='source_manifest_sha256'").fetchone()[0]
        # Fingerprint every tile as well: the manifest need not change when bytes do.
        generation = digest(encode([generation, [tuple(r) for r in con.execute('SELECT path,sha256 FROM inputs ORDER BY path')]]).encode())
        previous = con.execute("SELECT value FROM settings WHERE key='bounds_generation'").fetchone()
        if not previous or previous[0] != generation:
            con.execute('DELETE FROM footprint_bounds')
            for row in con.execute('SELECT rowid,rings_json FROM buildings WHERE active=1'):
                rings = json.loads(row['rings_json'])
                points = [p for ring in rings for p in ring]
                xs, zs = zip(*points)
                con.execute('INSERT INTO footprint_bounds VALUES(?,?,?,?,?)',
                            (row['rowid'], min(xs), max(xs), min(zs), max(zs)))
            con.execute("INSERT OR REPLACE INTO settings VALUES('bounds_generation',?)", (generation,))
        membership, areas, problems, geometries = {}, [], [], {}
        def add(uid, reason, priority):
            entry = membership.setdefault(uid, {'reasons': [], 'priority': 0})
            if reason not in entry['reasons']:
                entry['reasons'].append(reason)
            entry['priority'] = max(priority, entry['priority'])

        for area in config['areas']:
            if 'section' in area:
                row = con.execute('SELECT definition_json FROM sections WHERE id=?', (area['section'],)).fetchone()
                if not row:
                    raise ValueError('Unknown review section: '+area['section'])
                s = json.loads(row[0])
                from shapely.ops import unary_union
                region = unary_union([shape(p['rings']) for p in s['polygons']])
            else:
                bounds = area['bounds']
                if len(bounds) != 4 or not all(isinstance(v, (int, float)) for v in bounds) or bounds[0] >= bounds[2] or bounds[1] >= bounds[3]:
                    raise ValueError('Invalid area bounds')
                region = box(*bounds)
            xmin, zmin, xmax, zmax = region.bounds
            candidates = con.execute('''SELECT b.* FROM footprint_bounds r JOIN buildings b ON b.rowid=r.id
              WHERE b.active=1 AND r.max_x>=? AND r.min_x<=? AND r.max_z>=? AND r.min_z<=? ORDER BY b.uid''',
                                     (xmin, xmax, zmin, zmax)).fetchall()
            matched = []
            for b in candidates:
                geom = shape(json.loads(b['rings_json']))
                if not geom.intersects(region):
                    continue
                add(b['uid'], 'area:'+area['id'], area.get('priority', 1))
                geometries[b['uid']] = dict(b)
                matched.append(b['uid'])
            areas.append(dict(id=area['id'], title=area['title'], bounds=list(region.bounds),
                              shape=region.__geo_interface__, count=len(matched), uids=matched))
        landmark_results = []
        for landmark in config.get('landmarks', []):
            matched = []
            for expected in landmark['records']:
                b = con.execute('SELECT * FROM buildings WHERE uid=? AND active=1', (expected['uid'],)).fetchone()
                if not b or b['object_id'] != expected['objectId'] or b['csuid'] != expected['csuid'] or b['name'].casefold() != expected['name'].casefold():
                    problems.append(dict(landmark=landmark['id'], uid=expected['uid'], reason='identity-missing-or-changed'))
                    continue
                add(b['uid'], 'landmark:'+landmark['id'], 10)
                geometries[b['uid']] = dict(b)
                matched.append(b['uid'])
            landmark_results.append(dict(id=landmark['id'], title=landmark['title'], matched=matched,
                                         expected=len(landmark['records'])))
        if not membership:
            raise ValueError('Selection is empty')
        summary = dict(name=config['name'], configSHA256=digest(encode(config).encode()),
                       inventorySHA256=generation, buildings=len(membership), areas=areas,
                       landmarks=landmark_results, exceptions=problems,
                       membershipSHA256=digest(encode(sorted(membership)).encode()))
        con.execute('DELETE FROM selection_members WHERE name=?', (config['name'],))
        con.executemany('INSERT INTO selection_members VALUES(?,?,?,?)',
                        [(config['name'], uid, encode(info['reasons']), info['priority']) for uid, info in sorted(membership.items())])
        con.execute('INSERT OR REPLACE INTO selection_sets VALUES(?,?,?,?,?)',
                    (config['name'], encode(config), summary['configSHA256'], generation, encode(summary)))
        con.commit()
        summary['seconds'] = round(time.monotonic()-started, 2)
        return summary, geometries
    except BaseException:
        con.rollback()
        raise
    finally:
        con.close()


def review_html(summary, buildings):
    panels = []
    for area in summary['areas']:
        x0, z0, x1, z1 = area['bounds']
        scale = 560/max(x1-x0, z1-z0)
        def ring_path(r):
            return 'M'+' L'.join(f'{(p[0]-x0)*scale:.2f},{(p[1]-z0)*scale:.2f}' for p in r)+' Z'
        paths = []
        landmarks = {uid for l in summary['landmarks'] for uid in l['matched']}
        for uid in area['uids']:
            b = buildings[uid]
            colour = '#c6502f' if uid in landmarks else '#246d65' if b['embedded'] else '#82928f'
            paths.append(f'<path fill="{colour}" fill-rule="evenodd" d="'+
                         ' '.join(ring_path(r) for r in json.loads(b['rings_json']))+
                         '"><title>'+html.escape(b['name']+' · '+uid)+'</title></path>')
        # Outline the actual section polygon, not merely its bounding rectangle.
        shape_data = area['shape']
        polys = [shape_data['coordinates']] if shape_data['type'] == 'Polygon' else shape_data['coordinates']
        outline = ' '.join(ring_path(r) for poly in polys for r in poly)
        panels.append('<section><h2>'+html.escape(area['title'])+f'</h2><p>{area["count"]:,} intersecting forms</p>'+
                      '<svg viewBox="0 0 560 560" role="img" aria-label="Building selection plan">'+''.join(paths)+
                      f'<path d="{outline}" fill="none" stroke="#222" stroke-width="1"/></svg></section>')
    return '''<!doctype html><meta charset="utf-8"><title>Astra tourist trial selection</title>
<style>body{font:16px system-ui;background:#f5f5ef;color:#263d38;margin:24px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}section{background:white;padding:16px}svg{width:100%;max-height:560px}path:hover{fill:#ffba48}h2{font-size:19px}</style>
<h1>Tourist trial · building selection</h1><p>Local grid plan, north up. Red: flagged landmark; green: embedded detail; grey: other forms (including progressive detail). Hover for names and IDs. Boundaries are project trial areas, not official neighbourhoods. This is a membership review, not a 3D quality approval.</p><main>'''+''.join(panels)+'</main><pre>'+html.escape(encode(summary['exceptions']))+'</pre>'


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', type=pathlib.Path, default=pathlib.Path(__file__).parent/'local/buildings.sqlite')
    p.add_argument('--config', type=pathlib.Path, default=pathlib.Path(__file__).parent/'tourist-trial.json')
    p.add_argument('--out', type=pathlib.Path, default=pathlib.Path(__file__).parent/'local/trial')
    args = p.parse_args()
    result, buildings = select(args.db, json.loads(args.config.read_text()))
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/'selection.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    (args.out/'selection.html').write_text(review_html(result, buildings))
    print(encode({k: v for k, v in result.items() if k not in ('areas', 'landmarks')}))
