"""Exact-object fallback transport for the authorised non-main Astra branch.
Never rewrites commits, forces a reference, changes local refs or touches main.
"""
import base64,datetime,json,re,subprocess,time
from pathlib import Path
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city')
REPO='repos/wiiiimm/hongkong-sandbox';BRANCH='codex/astra-hong-kong-city'
LOG=Path('/tmp/astra-exact-git-api-delivery-20261104-result.json')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def api(path,data=None):
    command=['gh','api',REPO+path]
    if data is not None:command+=['--method','POST','--input','-']
    for attempt in range(3):
        cp=subprocess.run(command,input=None if data is None else json.dumps(data),capture_output=True,text=True,cwd=ROOT,timeout=120)
        if cp.returncode==0:return json.loads(cp.stdout)
        if attempt==2:raise RuntimeError('GitHub API operation failed: '+path+' '+cp.stderr[-350:])
        time.sleep(2+attempt*3)
def person(value):
    m=re.fullmatch(r'(.*) <([^<>]+)> (\d+) ([+-]\d{4})',value);assert m
    name,email,stamp,offset=m.groups();minutes=(int(offset[1:3])*60+int(offset[3:]))*(1 if offset[0]=='+'else-1)
    date=datetime.datetime.fromtimestamp(int(stamp),datetime.timezone(datetime.timedelta(minutes=minutes))).isoformat(timespec='seconds')
    return dict(name=name,email=email,date=date)
def main():
    assert git('branch','--show-current').decode().strip()==BRANCH
    target=git('rev-parse','HEAD').decode().strip();base=api('/git/ref/heads/'+BRANCH)['object']['sha']
    if base==target:print('Already delivered exact commit '+target,flush=True);return
    assert subprocess.run(['git','merge-base','--is-ancestor',base,target],cwd=ROOT).returncode==0
    commits=git('rev-list','--reverse',base+'..'+target).decode().splitlines();assert 1<=len(commits)<=3
    prior=base;uploaded=set();steps=[];print('Exact commits to transfer: '+str(len(commits)),flush=True)
    for commit in commits:
        raw=git('cat-file','commit',commit);headers,message=raw.split(b'\n\n',1);lines=[line.split(' ',1)for line in headers.decode().splitlines()]
        assert all(k in ['tree','parent','author','committer']for k,v in lines)and sum(k=='parent'for k,v in lines)==1
        h=dict(lines);assert h['parent']==prior
        names=git('diff-tree','--no-commit-id','--name-only','--no-renames','-r','-z',prior,commit).decode().rstrip('\0').split('\0');assert names and len(names)<=250
        entries=[]
        for index,path in enumerate(names,1):
            assert not any(x.startswith('.env')or x in ['.git','.aws']for x in Path(path).parts)
            value=git('ls-tree','-z',commit,'--',path)
            if not value:entries.append(dict(path=path,mode='100644',type='blob',sha=None));continue
            declaration,found=value.rstrip(b'\0').split(b'\t',1);mode,kind,sha=declaration.decode().split();assert found.decode()==path and kind=='blob'and mode in ['100644','100755','120000']
            if sha not in uploaded:
                blob=git('cat-file','blob',sha);assert len(blob)<25_000_000
                result=api('/git/blobs',dict(content=base64.b64encode(blob).decode(),encoding='base64'));assert result['sha']==sha,'Blob identity changed';uploaded.add(sha);time.sleep(1.0)
            entries.append(dict(path=path,mode=mode,type=kind,sha=sha))
            if index%10==0:print(commit[:10]+' blobs '+str(index)+'/'+str(len(names)),flush=True)
        tree=api('/git/trees',dict(base_tree=git('rev-parse',prior+'^{tree}').decode().strip(),tree=entries));assert tree['sha']==h['tree'],'Tree identity changed: do not update branch'
        created=api('/git/commits',dict(message=message.decode(),tree=h['tree'],parents=[prior],author=person(h['author']),committer=person(h['committer'])))
        assert created['sha']==commit,'Commit identity changed: do not update branch. Got '+created['sha']+' expected '+commit
        steps.append(dict(commit=commit,tree=h['tree'],files=len(entries)));prior=commit;print('Verified exact commit '+commit,flush=True)
    assert prior==target and api('/git/ref/heads/'+BRANCH)['object']['sha']==base,'Remote branch moved; never overwrite'
    cp=subprocess.run(['gh','api',REPO+'/git/refs/heads/'+BRANCH,'--method','PATCH','--input','-'],input=json.dumps(dict(sha=target,force=False)),capture_output=True,text=True,cwd=ROOT,timeout=120)
    assert cp.returncode==0,cp.stderr[-350:];updated=json.loads(cp.stdout);assert updated['object']['sha']==target
    final=api('/git/ref/heads/'+BRANCH);assert final['object']['sha']==target
    LOG.write_text(json.dumps(dict(passed=True,branch=BRANCH,previous=base,commit=target,exactOriginalCommits=steps,force=False,localRefsChanged=False),indent=2)+'\n');print('DELIVERED EXACT NON-FORCED HEAD '+target,flush=True)
if __name__=='__main__':main()
