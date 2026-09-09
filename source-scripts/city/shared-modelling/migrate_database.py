"""HKS-223: restore a private source backup into an empty modelling schema and verify every row.

Credentials and PostgreSQL logs stay in the owner-only migration directory.
This command never drops a schema or switches the active worker connection.
"""
import argparse,hashlib,json,os,pathlib,subprocess,sys,time,traceback
import certifi,psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict

SCHEMA='astra_modelling'

def params(folder,side):
    value=json.loads((folder/f'{side}-connection.json').read_text())['MODELLING_DATABASE_URL']
    p=conninfo_to_dict(value)
    expected=json.loads((folder/('source-branch.json' if side=='source' else 'destination-inspection.json')).read_text())
    if p.get('host')!=expected['host'] or p.get('dbname')!=expected['database'] or any(p.get(k) for k in ('hostaddr','service','options')) or '-pooler.' in p['host']:
        raise ValueError('Connection does not match the verified direct endpoint')
    p.update(sslmode='verify-full',sslrootcert=certifi.where(),connect_timeout=15,application_name='astra-database-migration')
    return p

def check_identity(con,expected):
    row=con.execute("SELECT current_database(),current_setting('neon.project_id',true),current_setting('neon.branch_id',true)").fetchone()
    if row!=(expected['database'],expected.get('project_id',expected.get('projectId')),expected.get('branch_id',expected.get('branchId'))):
        raise ValueError('Server-reported destination/source identity differs')

def tables(con,schema):
    return [r[0] for r in con.execute('SELECT tablename FROM pg_tables WHERE schemaname=%s ORDER BY tablename',(schema,))]

def configure_snapshot(con):
    con.execute("SET LOCAL TIME ZONE 'UTC'")
    con.execute("SET LOCAL DateStyle='ISO, YMD'")
    con.execute('SET LOCAL extra_float_digits=3')
    con.execute("SET LOCAL work_mem='32MB'")

def fingerprints(con,schema):
    result={}
    for name in tables(con,schema):
        query=sql.SQL('''WITH rows AS MATERIALIZED (
            SELECT encode(sha256(convert_to(to_jsonb(t)::text,'UTF8')),'hex') AS h FROM {}.{} t)
            SELECT count(*),encode(sha256(convert_to(coalesce(string_agg(h,'' ORDER BY h),''),'UTF8')),'hex') FROM rows''').format(sql.Identifier(schema),sql.Identifier(name))
        count,digest=con.execute(query).fetchone()
        result[name]={'rows':count,'sha256SortedRowHashes':digest}
        print(json.dumps({'verifiedTable':name,'rows':count}),flush=True)
    return result

def sequences(con):
    result={}
    for (name,) in con.execute('SELECT sequencename FROM pg_sequences WHERE schemaname=%s ORDER BY sequencename',(SCHEMA,)).fetchall():
        result[name]=list(con.execute(sql.SQL('SELECT last_value,is_called FROM {}.{}').format(sql.Identifier(SCHEMA),sql.Identifier(name))).fetchone())
    return result

def write(folder,name,value):
    path=folder/name
    with path.open('w') as out:json.dump(value,out,indent=2);out.write('\n')
    path.chmod(0o600)

def migrate(folder,pg_bin):
    os.umask(0o077)
    if folder.stat().st_mode&0o077:raise ValueError('Migration folder must be owner-only')
    archive=folder/'source.dump';receipt=json.loads((folder/'receipt.json').read_text())
    with archive.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
    if actual!=receipt['backupSHA256']:raise ValueError('Source backup checksum mismatch')
    source=params(folder,'source');destination=params(folder,'destination')
    if source['host']==destination['host']:raise ValueError('Source and destination must differ')
    src_identity=json.loads((folder/'source-branch.json').read_text());dst_identity=json.loads((folder/'destination-inspection.json').read_text())
    toc=subprocess.run([str(pg_bin/'pg_restore'),'--list',str(archive)],check=True,capture_output=True,text=True).stdout
    selected=[line for line in toc.splitlines() if line and not line.startswith(';') and (' SCHEMA - '+SCHEMA+' ' in line or ' '+SCHEMA+' ' in line)]
    if not any(' SCHEMA - '+SCHEMA+' ' in line for line in selected):raise ValueError('Backup must include the modelling schema definition')
    toc_path=folder/'restore.list';toc_path.write_text('\n'.join(selected)+'\n')
    started=time.time()
    with psycopg.connect(**source) as src,psycopg.connect(**destination) as dst:
        check_identity(src,src_identity);check_identity(dst,dst_identity)
        if dst.execute('SELECT 1 FROM pg_namespace WHERE nspname=%s',(SCHEMA,)).fetchone():raise ValueError('Destination modelling schema already exists; refusing overwrite')
        destination_other_tables=dst.execute("SELECT schemaname,tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY 1,2").fetchall()
        dst.commit()
        names=tables(src,SCHEMA)
        # Hold writes to source modelling tables during reconciliation and restore.
        src.execute(sql.SQL('LOCK TABLE {} IN SHARE MODE').format(sql.SQL(',').join(sql.Identifier(SCHEMA,n) for n in names)))
        if src.execute("SELECT count(*) FROM astra_modelling.jobs WHERE status='running' AND lease_until>clock_timestamp()").fetchone()[0]:raise ValueError('Active source jobs must finish before migration')
        configure_snapshot(src)
        source_rows=fingerprints(src,SCHEMA);source_sequences=sequences(src)
        write(folder,'source-fingerprints.json',{'tables':source_rows,'sequences':source_sequences})
        # Existing Neon Auth data is outside the selected archive entries.
        env={k:v for k,v in os.environ.items() if not k.startswith('PG')}
        for key,target in {'host':'PGHOST','dbname':'PGDATABASE','user':'PGUSER','password':'PGPASSWORD','port':'PGPORT','sslmode':'PGSSLMODE','sslrootcert':'PGSSLROOTCERT'}.items():
            if key in destination:env[target]=destination[key]
        env['PGAPPNAME']='astra-migration-restore'
        with (folder/'restore.log').open('wb') as log:
            completed=subprocess.run([str(pg_bin/'pg_restore'),'--use-list',str(toc_path),'--no-owner','--no-privileges','--exit-on-error','--single-transaction','--dbname',destination['dbname'],str(archive)],env=env,stdout=log,stderr=log)
        if completed.returncode:raise RuntimeError('Restore failed; transaction rolled back; inspect private restore log')
        print(json.dumps({'restoreCommitted':True,'schema':SCHEMA}),flush=True)
        configure_snapshot(dst);destination_rows=fingerprints(dst,SCHEMA);destination_sequences=sequences(dst)
        if destination_rows!=source_rows or destination_sequences!=source_sequences:raise ValueError('Restored row contents or sequences differ; active connection remains unchanged')
        other_after=dst.execute("SELECT schemaname,tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema',%s) ORDER BY 1,2",(SCHEMA,)).fetchall()
        if other_after!=destination_other_tables:raise ValueError('Non-modelling table inventory changed')
        report={'issue':'HKS-223','source':src_identity,'destination':dst_identity,'backupSHA256':actual,'backupBytes':archive.stat().st_size,'tables':source_rows,'sequences':source_sequences,'allTableContentsMatch':True,'allSequencesMatch':True,'nonModellingTablesPreserved':True,'restoredTables':len(source_rows),'restoredRows':sum(r['rows'] for r in source_rows.values()),'elapsedSeconds':round(time.time()-started,3),'activeConnectionSwitched':False}
        write(folder,'migration-verification.json',report)
        print(json.dumps({k:report[k] for k in ('restoredTables','restoredRows','allTableContentsMatch','allSequencesMatch','nonModellingTablesPreserved','elapsedSeconds','activeConnectionSwitched')}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--private-dir',type=pathlib.Path,required=True);p.add_argument('--pg-bin',type=pathlib.Path,default=pathlib.Path('/opt/homebrew/opt/libpq/bin'));a=p.parse_args()
    try:migrate(a.private_dir,a.pg_bin)
    except Exception:
        with (a.private_dir/'migration-error.log').open('w') as f:traceback.print_exc(file=f)
        raise SystemExit('Migration did not complete; private diagnostic retained; active connection not changed') from None
