"""Cooperative, cross-batch session leases. Never a filesystem or publication lock."""
import argparse
import json
import os
from pathlib import Path
import uuid

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from db import connect, HERE

LOCK_ID = 217002
DEFAULT_TTL = 900


def normalise(resources):
    result = sorted(set(resources))
    if not result or len(result) > 1000 or any(
        not isinstance(key, str) or not key.strip() or key != key.strip() or len(key) > 300
        for key in result
    ):
        raise ValueError('Provide 1–1000 stable resource keys of 1–300 characters')
    return result


def validate(owner, ttl):
    if not isinstance(owner, str) or not owner.strip() or len(owner) > 200:
        raise ValueError('Explicit session owner is required (maximum 200 characters)')
    if isinstance(ttl, bool) or not isinstance(ttl, int) or not 1 <= ttl <= 3600:
        raise ValueError('TTL must be an integer from 1 to 3600 seconds')


def migrate():
    with connect() as con:
        con.execute('SELECT pg_advisory_xact_lock(%s)', (LOCK_ID,))
        con.execute((HERE / 'reservations.sql').read_text())
    return {'schemaVersion': 2}


def _rows(con, resources):
    return con.execute('''SELECT r.resource,r.token,r.generation,g.owner,g.batch,
        g.heartbeat_at,g.lease_until,g.released_at,
        (g.released_at IS NULL AND g.lease_until>clock_timestamp()) AS active
        FROM astra_modelling.reservations r JOIN astra_modelling.reservation_groups g USING(token)
        WHERE r.resource=ANY(%s) ORDER BY r.resource''', (resources,)).fetchall()


def _event(con, action, owner, token, resources, previous, reason=None):
    # Only ownership metadata; never model results, environment values or credentials.
    old = [{key: str(row[key]) if row[key] is not None else None
            for key in ('resource', 'token', 'generation', 'owner', 'lease_until')} for row in previous]
    con.execute('''INSERT INTO astra_modelling.reservation_events
        (action,actor,token,resources,reason,previous) VALUES(%s,%s,%s,%s,%s,%s)''',
        (action, owner, token, resources, reason, Jsonb(old)))


def claim(owner, resources, ttl=DEFAULT_TTL, batch=None, *, expected_tokens=None, reason=None):
    """Claim all keys or none. expected_tokens enables explicit compare-and-swap takeover."""
    resources = normalise(resources)
    validate(owner, ttl)
    override = expected_tokens is not None
    if override and (not isinstance(reason, str) or not reason.strip() or len(reason) > 1000):
        raise ValueError('Takeover requires an explicit reason (maximum 1000 characters)')
    if override and set(expected_tokens) != set(resources):
        raise ValueError('Expected tokens must cover exactly the requested resource keys')
    with connect() as con:
        con.row_factory = dict_row
        # Serialises only short reservation metadata transactions, never modelling work.
        # A fixed lock makes new-row conflicts and overlapping groups atomic without deadlocks.
        con.execute('SELECT pg_advisory_xact_lock(%s)', (LOCK_ID,))
        previous = _rows(con, resources)
        observed = {key: None for key in resources}
        observed.update({row['resource']: str(row['token']) for row in previous})
        if override and observed != expected_tokens:
            return {'ok': False, 'error': 'ownership-changed', 'current': previous,
                    'expectedTokens': observed}
        conflicts = [row for row in previous if row['active']]
        if conflicts and not override:
            return {'ok': False, 'error': 'reserved', 'conflicts': conflicts}
        token = uuid.uuid4()
        group = con.execute('''INSERT INTO astra_modelling.reservation_groups
            (token,owner,batch,resources,lease_until) VALUES(%s,%s,%s,%s,
            clock_timestamp()+make_interval(secs=>%s)) RETURNING *''',
            (token, owner, batch, resources, ttl)).fetchone()
        for resource in resources:
            con.execute('''INSERT INTO astra_modelling.reservations(resource,token) VALUES(%s,%s)
                ON CONFLICT(resource) DO UPDATE SET token=EXCLUDED.token,
                generation=nextval('astra_modelling.reservation_generation')''', (resource, token))
        _event(con, 'takeover' if override else ('reclaim' if previous else 'claim'),
               owner, token, resources, previous, reason)
        group['generations'] = {row['resource']: row['generation'] for row in _rows(con, resources)}
        return {'ok': True, 'reservation': group}


def takeover(owner, resources, expected_tokens, reason, ttl=DEFAULT_TTL, batch=None):
    return claim(owner, resources, ttl, batch, expected_tokens=expected_tokens, reason=reason)


def status(resources=None, owner=None):
    with connect() as con:
        con.row_factory = dict_row
        # Snapshot serialises with claims so expectedTokens describes a consistent set.
        con.execute('SELECT pg_advisory_xact_lock(%s)', (LOCK_ID,))
        if resources is None:
            resources = [r['resource'] for r in con.execute('''SELECT r.resource
                FROM astra_modelling.reservations r JOIN astra_modelling.reservation_groups g USING(token)
                WHERE (%s::text IS NULL OR g.owner=%s) ORDER BY r.resource''', (owner, owner))]
        else:
            resources = normalise(resources)
        rows = _rows(con, resources)
        expected = {key: None for key in resources}
        expected.update({row['resource']: str(row['token']) for row in rows})
        return {'resources': rows, 'expectedTokens': expected}


def _current(con, reservation):
    token = uuid.UUID(str(reservation['token']))
    group = con.execute('''SELECT *, (released_at IS NULL AND lease_until>clock_timestamp()) AS active
        FROM astra_modelling.reservation_groups WHERE token=%s AND owner=%s''',
        (token, reservation['owner'])).fetchone()
    if not group or not group['active']:
        return None
    rows = _rows(con, group['resources'])
    if len(rows) != len(group['resources']) or any(row['token'] != token for row in rows):
        return None
    return group


def owns(reservation):
    with connect() as con:
        con.row_factory = dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)', (LOCK_ID,))
        return _current(con, reservation) is not None


def heartbeat(reservation, ttl=DEFAULT_TTL):
    validate(reservation['owner'], ttl)
    with connect() as con:
        con.row_factory = dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)', (LOCK_ID,))
        group = _current(con, reservation)
        if not group:
            return {'ok': False, 'error': 'lease-lost'}
        row = con.execute('''UPDATE astra_modelling.reservation_groups SET
            heartbeat_at=clock_timestamp(),lease_until=clock_timestamp()+make_interval(secs=>%s)
            WHERE token=%s AND lease_until>clock_timestamp() RETURNING *''',
            (ttl, group['token'])).fetchone()
        return {'ok': row is not None, 'reservation': row} if row else {'ok': False, 'error': 'lease-lost'}


def release(reservation):
    with connect() as con:
        con.row_factory = dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)', (LOCK_ID,))
        group = _current(con, reservation)
        if not group:
            return {'ok': False, 'error': 'lease-lost'}
        changed = con.execute('''UPDATE astra_modelling.reservation_groups SET released_at=clock_timestamp()
            WHERE token=%s AND lease_until>clock_timestamp() RETURNING token''', (group['token'],)).fetchone()
        if not changed:
            return {'ok': False, 'error': 'lease-lost'}
        _event(con, 'release', group['owner'], group['token'], group['resources'], [])
        return {'ok': True}


def _save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_text(json.dumps(value, default=str, indent=2) + '\n')
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('migrate')
    for command in ('claim', 'takeover'):
        p = sub.add_parser(command)
        p.add_argument('--owner', required=True)
        p.add_argument('--resource', action='append', required=True)
        p.add_argument('--ttl', type=int, default=DEFAULT_TTL)
        p.add_argument('--batch', help='Descriptive only; does not isolate reservations')
        p.add_argument('--lease-file', type=Path, required=True)
        if command == 'takeover':
            p.add_argument('--expected-file', type=Path, required=True)
            p.add_argument('--reason', required=True)
    p = sub.add_parser('status')
    p.add_argument('--resource', action='append')
    p.add_argument('--owner')
    p.add_argument('--output', type=Path)
    for command in ('heartbeat', 'release', 'check'):
        p = sub.add_parser(command)
        p.add_argument('--lease-file', type=Path, required=True)
        if command == 'heartbeat':
            p.add_argument('--ttl', type=int, default=DEFAULT_TTL)
    args = parser.parse_args()
    if args.command == 'migrate':
        result = migrate()
    elif args.command == 'status':
        result = status(args.resource, args.owner)
        if args.output:
            _save(args.output, result)
    elif args.command in ('claim', 'takeover'):
        # Never overwrite an existing lease receipt; use another path or deliberately remove it.
        if args.lease_file.exists():
            parser.error('Lease file exists; choose a new session receipt path')
        kwargs = {}
        if args.command == 'takeover':
            kwargs = dict(expected_tokens=json.loads(args.expected_file.read_text())['expectedTokens'], reason=args.reason)
        result = claim(args.owner, args.resource, args.ttl, args.batch, **kwargs)
        if result['ok']:
            _save(args.lease_file, result['reservation'])
    else:
        reservation = json.loads(args.lease_file.read_text())
        if args.command == 'check':
            result = {'ok': owns(reservation)}
        else:
            result = globals()[args.command](reservation, args.ttl) if args.command == 'heartbeat' else release(reservation)
    print(json.dumps(result, default=str, indent=2))
    return 0 if result.get('ok', True) else 2


if __name__ == '__main__':
    raise SystemExit(main())
