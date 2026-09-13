"""Restore checksum-verified cached sheet bundles; no government requests."""
import json,sys,os,tarfile,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent;sys.path.insert(0,str(HERE.parent/'landmark-resume'))
from r2_snapshot import R2Store,verify_object,digest
from dotenv import dotenv_values
p=argparse.ArgumentParser();p.add_argument('--env-file',type=Path,required=True);args=p.parse_args()
for k,v in dotenv_values(args.env_file).items():
 if k.startswith('R2_') and v:os.environ[k]=v
store=R2Store('hk-sandbox-assets');rows=json.loads((HERE/'selected-sources.json').read_text());sheets={r['sheet']:r['artifacts'][0]for r in rows}
for sheet,a in sheets.items():
 out=HERE/'local'/sheet;out.mkdir(parents=True,exist_ok=True);archive=out/'retained.tar.gz'
 if not archive.exists() or digest(archive)!=a['sha256']:verify_object(store,a['key'],a['sha256'],a['bytes'],archive)
 with tarfile.open(archive,'r:gz') as tar:
  names=[m.name for m in tar if m.isfile()];print(sheet,a['bytes'],names[:14])
  # Extraction is bounded to regular relative members. Source originals stay in the archive.
  for m in tar.getmembers():
   path=Path(m.name)
   if not m.isfile() or path.is_absolute() or '..' in path.parts or '\\' in m.name:continue
   if m.name.startswith('original/'):continue
   target=out/path;target.parent.mkdir(parents=True,exist_ok=True)
   with tar.extractfile(m) as src:target.write_bytes(src.read())
