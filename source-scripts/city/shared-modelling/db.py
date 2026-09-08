"""Explicit, pinned modelling branch; never falls back to application DATABASE_URL."""
import json
import os
from pathlib import Path
import certifi
import psycopg
from psycopg.conninfo import conninfo_to_dict
from dotenv import dotenv_values

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / 'branch.json').read_text())
ROOT = HERE.parents[2]


def connection_parameters(url):
    if any(os.environ.get(k) for k in ('PGHOSTADDR', 'PGSERVICE', 'PGSERVICEFILE', 'PGOPTIONS')):
        raise ValueError('Refusing libpq environment routing/session overrides')
    if not url:
        raise ValueError('Set MODELLING_DATABASE_URL in environment or private .env.modelling')
    try:
        params = conninfo_to_dict(url)
    except Exception:
        raise ValueError('Invalid modelling connection configuration (credentials withheld)') from None
    host = CONFIG['host']
    if params.get('host') not in (host, host.replace('.c-', '-pooler.c-', 1)):
        raise ValueError('Refusing connection: host is not the pinned astra-modelling branch')
    if params.get('dbname') != CONFIG['database']:
        raise ValueError('Refusing connection: unexpected modelling database')
    if params.get('hostaddr') or params.get('service') or params.get('port', '5432') != '5432':
        raise ValueError('Refusing alternate connection routing')
    # Do not allow connection-string settings to override the branch routing or schema.
    if params.get('options'):
        raise ValueError('Connection options must not override session configuration')
    params.update(port='5432', sslmode='verify-full', sslrootcert=certifi.where(), connect_timeout='15', application_name='astra-modelling')
    return params


def connect():
    env_file = Path(os.environ.get('MODELLING_ENV_FILE', ROOT / '.env.modelling'))
    url = os.environ.get('MODELLING_DATABASE_URL') or dotenv_values(env_file).get('MODELLING_DATABASE_URL')
    params = connection_parameters(url)
    try:
        return psycopg.connect(**params)
    except psycopg.Error as exc:
        raise RuntimeError('Modelling database connection failed; check access and branch configuration. '
                           f'Error type: {type(exc).__name__}') from None


def migrate():
    with connect() as con:
        # Serialise schema changes, not job processing. Never modifies public schema.
        con.execute('SELECT pg_advisory_xact_lock(217001)')
        con.execute((HERE / 'schema.sql').read_text())
    return {'branch': CONFIG['branch_name'], 'branchId': CONFIG['branch_id'], 'schema': CONFIG['schema']}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['check', 'migrate'])
    args = parser.parse_args()
    if args.command == 'migrate':
        print(json.dumps(migrate()))
    else:
        with connect() as con:
            database, version = con.execute('SELECT current_database(),current_setting(\'server_version\')').fetchone()
        print(json.dumps(dict(branch=CONFIG['branch_name'], database=database, version=version)))
