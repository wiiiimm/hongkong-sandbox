"""Read-only current-landmark closure inventory; no backups, downloads or uploads."""
import collections,datetime,json,os,pathlib,sqlite3,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=pathlib.Path(__file__).resolve().parent
rows={}
def read(path):return json.loads(path.read_bytes())
def add(path,category,rebuildability,profile='portable-working-closure',expected=None):
 path=path if isinstance(path,pathlib.Path)else ROOT/path
 lexical=path.absolute();key=str(lexical.relative_to(ROOT)) if lexical.is_relative_to(ROOT)else str(lexical)
 link=path.is_symlink();exists=path.exists();resolved=path.resolve()
 row=rows.setdefault(key,dict(path=key,exists=exists,bytes=path.stat().st_size if exists and path.is_file()else 0,kind='symlink'if link else'file'if exists and path.is_file()else'directory'if exists else'missing',categories=[],rebuildability=[],profiles=[],expectedSHA256=None))
 for field,value in [('categories',category),('rebuildability',rebuildability),('profiles',profile)]:
  if value not in row[field]:row[field].append(value)
 if expected:row['expectedSHA256']=expected
 if resolved!=lexical:row.update(resolvedOutsideCheckout=not resolved.is_relative_to(ROOT),resolvedTarget=str(resolved.relative_to(ROOT))if resolved.is_relative_to(ROOT)else str(resolved))
 if link:row.update(linkTarget=os.readlink(path),resolvedOutsideCheckout=not resolved.is_relative_to(ROOT),resolvedTarget=str(resolved.relative_to(ROOT))if resolved.is_relative_to(ROOT)else str(resolved))
 return row

def tree(path,category,rebuildability,profile='portable-working-closure'):
 path=path if isinstance(path,pathlib.Path)else ROOT/path
 if not path.exists():add(path,category,rebuildability,profile);return
 for parent,dirs,files in os.walk(path,followlinks=False):
  dirs[:]=[d for d in dirs if d!='__pycache__']
  for name in files+[d for d in dirs if(pathlib.Path(parent)/d).is_symlink()]:add(pathlib.Path(parent)/name,category,rebuildability,profile)

pin=read(ROOT/'source-scripts/city/landmark-preflight/snapshot.json');snapshot=ROOT/'source-scripts/city/landmark-preflight/snapshots'/pin['id']
cat=read(ROOT/'source-scripts/city/landmark-identity/prepared/catalogue.json');uids={m['uid']for m in cat['models']}
db=ROOT/'source-scripts/city/building-batch/local/buildings.sqlite'
assert not pathlib.Path(str(db)+'-wal').exists(),'Active WAL requires a coherent online backup before inventory'
add(db,'sqlite-working-ledger','Online SQLite backup required; retain job/selection provenance. Rebuilding inventory does not recover job history.')
c=sqlite3.connect('file:'+str(db)+'?mode=ro&immutable=1',uri=True);c.row_factory=sqlite3.Row
counts={name:c.execute('SELECT count(*) FROM '+name).fetchone()[0]for name in ['buildings','inputs','models','selection_sets','selection_members','batch_jobs','batch_job_sets','batch_plans']}
for row in c.execute('SELECT path,sha256 FROM inputs'):add(ROOT/'3d-viewer'/row['path'],'database-input','Restore from matching Git commit or versioned runtime asset snapshot.',expected=row['sha256'])
jobs=c.execute("SELECT j.uid,j.payload FROM batch_jobs j JOIN batch_job_sets s ON s.id=j.id WHERE s.name='landmark-identity-hks212-preparation-v2:cached-models'").fetchall()
source_manifests=set()
for job in jobs:
 if job['uid']not in uids:continue
 candidate=json.loads(job['payload']).get('candidate')
 if not candidate:continue
 path=ROOT/candidate['manifest'];canonical=path.resolve();source_manifests.add(canonical)
 add(canonical,'selected-model-source-manifest','Restore or restage retained compact source ZIP with pinned footprint selection and decoder.')
 for name,digest in candidate['spec']['sourceHashes'].items():add(canonical.parent/name,'selected-model-native-member','Rebuild byte-identically from retained compact ZIP; optional when restaging tooling is available.',expected=digest)
c.close()
for path in source_manifests:
 # Retain original compact source evidence when in the conventional source/staged layout.
 if path.parent.parent.name=='staged':
  source=path.parent.parent.parent/'sources'/path.parent.name
  for name in ['download.json','head.json','state.json','zip-directory.bin',path.parent.name+'.zip']:
   if(source/name).exists():add(source/name,'selected-model-source-cache','Native archive evidence; retain to avoid revised/removed upstream data.')
  official=path.parent.parent.parent/'official-selection.json.gz'
  if official.exists():add(official,'pinned-footprint-selection','Regenerable only from exact footprint snapshot and selected IDs; missing file blocks existing staging.')
terrain=read(ROOT/'docs/astra-city/landmark-preflight/terrain-inputs.json')
for source in terrain['nativeSources']:
 add(ROOT/source['manifest'],'terrain-native-manifest','Restage exact native ZIP through pinned decoder.',expected=source['manifestSha256'])
 for item in source['files']:add(ROOT/item['path'],'terrain-native-member','Restage byte-identical geometry from native ZIP; derived glTF strips photo references only.',expected=item['sha256'])
add(ROOT/terrain['dtm']['path'],'archival-dtm','Retain source; not substituted by current terrain meshes.',expected=terrain['dtm'].get('sha256'))
add('source-scripts/city/landsd-territory/landsd-hong-kong-source.geojson.gz','official-footprint-source','Retain exact revision for matching/selection; new upstream revision is not interchangeable.')
# Preserve every acquisition checkpoint needed to prove source absence and held identities.
for plan in [ROOT/'source-scripts/city/landmark-acquisition/plan.json']+list((ROOT/'source-scripts/city/landmark-acquisition/batches').glob('*/batch.json')):
 base=plan.parent
 for p in base.glob('*.json'):add(p,'acquisition-pinned-metadata','Tracked evidence, restored from matching Git commit.')
 add(base/'official-selection.json.gz','pinned-footprint-selection','Ignored and required by stage; not recreated when a tracked plan already exists.')
 for source in (base/'sources').glob('*'):
  for name in ['download.json','head.json','state.json','zip-directory.bin',source.name+'.zip']:
   if(source/name).exists():add(source/name,'acquisition-source-cache','Retain compact native ZIP and complete directory/provenance; offline member extraction can rebuild duplicates.')
  # Members are duplicate native material; list explicitly without making them essential to a compact package.
  if(source/'members').exists():tree(source/'members','duplicate-extracted-source-member','Byte-identical extraction from compact ZIP; omit from compact package.','rebuildable-cache')
 tree(base/'staged','acquisition-staged-cache','Rebuild from exact compact source ZIP plus pinned footprint selection and decoder.','rebuildable-cache')
tree(ROOT/'source-scripts/city/landmark-identity/prepared','prepared-candidates','Retain for exact current review; rebuild requires database, source manifests, tools and complete inputs.')
tree(snapshot,'pinned-preflight-snapshot','Retain immutable snapshot and candidate assets; fresh capture may produce a different snapshot ID.')
for name in ['source-scripts/city/landmark-identity/staged','source-scripts/city/landmark-identity/reference-cache']:
 tree(name,'adapter-links'if name.endswith('/staged')else'identity-reference-evidence','Recreate relative links after restoring native sources.'if name.endswith('/staged')else'Retain cited cached reference evidence; remote pages may change.','rebuildable-cache'if name.endswith('/staged')else'portable-working-closure')
# Legacy comparison used explicitly by stage_proposals.summaries().
add('source-scripts/city/landmark-bulk/compact/catalogue.json','prior-comparison-catalogue','Ignored dependency of stage summaries; retain original comparison catalogue.')
for path,digest in pin['cpuValidationInputHashes'].items():add(ROOT/path,'validation-hash-input','Must match pinned validation; do not refresh runtime independently.',expected=digest)
# Administrative/runtime paths are instructions, not portable payloads.
for path in [ROOT/'.git',ROOT/'CLAUDE.md',ROOT/'3d-viewer/city/node_modules',pathlib.Path('/private/tmp/astra-city-venv'),pathlib.Path('/Users/williamli/.nvm/versions/node/v24.17.0/bin/node'),pathlib.Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')]:
 add(path,'device-runtime-or-link','Recreate Git checkout, Python/Node dependencies and browser locally; do not archive host administrative/runtime directories.','exclude')
paths=[row['path']for row in rows.values()if not pathlib.Path(row['path']).is_absolute()]
tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
for row in rows.values():
 row['gitTracked']=row['path']in tracked
 if 'exclude'not in row['profiles']:row['profiles'].append('unmodified-cli-restore')
# Unique bytes by canonical file content path; profile totals are alternative views, not additive.
summary={}
for profile in ['portable-working-closure','rebuildable-cache','unmodified-cli-restore','exclude']:
 subset=[r for r in rows.values()if profile in r['profiles']and r['kind']=='file']
 summary[profile]={'files':len(subset),'bytes':sum(r['bytes']for r in subset),'untrackedBytes':sum(r['bytes']for r in subset if not r['gitTracked']),'missing':sum(not r['exists']for r in rows.values()if profile in r['profiles'])}
out={'issue':'HKS-215','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'gitCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'snapshotId':pin['id'],'candidateModels':len(uids),'terrainFlaggedModels':terrain['flaggedModels'],'terrainMissingSheets':terrain['missingNativeSheets'],'sqliteReadOnly':True,'sqliteTables':counts,'summary':summary,'rows':sorted(rows.values(),key=lambda r:r['path']),'limits':['Inventory only; no data copied, SQLite backup created, network requests, upload or secret inspection.','expectedSHA256 is existing evidence when available; creation of an upload manifest must hash all actual packaged bytes.','Profiles overlap and totals must not be added; duplicate extracted bytes can be rebuilt from native ZIPs.','Portable working closure needs offline extraction/restaging before existing full acquisition verifiers; unmodified-cli-restore also includes duplicate member/stage caches.','Current gallery output is actively produced and intentionally excluded from this stable closure.']}
(OUT/'cache-inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['snapshotId','candidateModels','sqliteTables','summary']},indent=2))
