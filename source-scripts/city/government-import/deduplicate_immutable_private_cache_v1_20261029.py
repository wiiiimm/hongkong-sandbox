"""Hardlink byte-identical old immutable private caches; retain every byte/path.

Only private content-addressed GLBs and completed attribute cache files qualify.
This changes storage allocation, never model geometry or an evidence payload.
Do not rewrite a hardlinked immutable cache in place; create a new path/revision.
"""
import argparse,hashlib,json,os,stat,time,uuid,shutil
from pathlib import Path
from collections import Counter
from run import ROOT,HERE,read,save,digest

def main():
 p=argparse.ArgumentParser();p.add_argument('--scan',required=True);p.add_argument('--report',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
 scan=read(Path(a.scan));assert scan['readOnly']and scan['changes']==0;private=(HERE/'local').resolve();cutoff=time.time()-86400;before=shutil.disk_usage(ROOT).free;actions=[];groups=0
 for group in scan['groups']:
  sha=group['sha256'];size=group['bytes'];paths=[(ROOT/name).resolve()for name in group['paths']];assert len(paths)>1
  for path in paths:
   assert path.is_relative_to(private)and path.is_file()and not(ROOT/str(path.relative_to(ROOT))).is_symlink()
   assert path.name.endswith('.glb.gz')or path.name=='attributes.json.gz'
   st=path.stat();assert stat.S_ISREG(st.st_mode)and st.st_mtime<cutoff and st.st_size==size
   assert digest(path.read_bytes())==sha
   if path.name.endswith('.glb.gz')and len(path.name)==71:assert path.name==sha+'.glb.gz'
  canonical=min(paths,key=lambda path:(path.stat().st_mtime,str(path)));cstat=canonical.stat();groups+=1
  for path in paths:
   old=path.stat()
   if(old.st_dev,old.st_ino)==(cstat.st_dev,cstat.st_ino):continue
   assert old.st_dev==cstat.st_dev
   action=dict(path=str(path.relative_to(ROOT)),canonical=str(canonical.relative_to(ROOT)),sha256=sha,bytes=size,oldDevice=old.st_dev,oldInode=old.st_ino,oldLinks=old.st_nlink)
   if a.apply:
    temp=path.with_name(path.name+'.dedup-'+uuid.uuid4().hex)
    try:os.link(canonical,temp);os.replace(temp,path)
    finally:temp.unlink(missing_ok=True)
    assert digest(path.read_bytes())==sha and(path.stat().st_dev,path.stat().st_ino)==(cstat.st_dev,cstat.st_ino)
   actions.append(action)
  assert all(digest(path.read_bytes())==sha for path in paths)
 after=shutil.disk_usage(ROOT).free
 result=dict(applied=a.apply,allPathsAndBytesPreserved=True,sourceGeometryChanges=0,privateImmutableGroups=groups,replacedDuplicatePaths=len(actions),freeBytesBefore=before,freeBytesAfter=after,observedFreeBytesRecovered=after-before,actions=actions,qualification='All qualifying files predate24h; every canonical and duplicate byte hash revalidated before and after atomic hardlink replacement. Source inputs/public viewer/references/Git objects untouched. Immutable private cache paths must never be rewritten in place; a new revision needs a new path.')
 save(Path(a.report),result);print({k:v for k,v in result.items()if k!='actions'},flush=True)

if __name__=='__main__':main()
