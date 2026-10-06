"""Run a separately receipted current original inside an unchanged composite parent.

All original identity, source receipt, contact, foundation, neighbour and runtime
gates remain required. This creates candidates only, never installs models.
"""
import argparse, json, subprocess, sys, uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
import importlib.util
spec=importlib.util.spec_from_file_location('indexed',HERE/'xl-current-revision-terrain-continuation.py')
indexed=importlib.util.module_from_spec(spec);spec.loader.exec_module(indexed)

def main():
    p=argparse.ArgumentParser();p.add_argument('--uid',required=True);p.add_argument('--batch',required=True)
    p.add_argument('--base',required=True);p.add_argument('--parent',required=True);p.add_argument('--owned',action='store_true')
    args=p.parse_args();assert Path(args.batch).name==args.batch and args.batch.startswith('government-xl-')
    doc=ROOT/'docs/astra-city/government-import'/args.batch;local=HERE/'local'/args.batch
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    assert args.parent in {r['url'] for r in manifest['terrainPatches']}
    old=read(ROOT/'3d-viewer'/args.parent);assert old.get('patches') and not old.get('nativeMesh')
    if args.owned:
        assert reservations.owns(read(local/'reservation.json'))
        save(doc/'nested-parent-routing.json',{'parentURL':args.parent,'parentSHA256':digest((ROOT/'3d-viewer'/args.parent).read_bytes()),
             'runnerSHA256':digest(Path(__file__).read_bytes()),'modelGeometryChanges':0,'scriptExternalAICalls':0})
        original=indexed.module
        def configured(name,filename):
            value=original(name,filename)
            if filename=='xl-cell-contact-resolution.py':
                value.PARENT_URL=args.parent
                value.NESTED_PARENT=True
            return value
        indexed.module=configured;indexed.owned(args,doc,local);return
    assert not doc.exists(),'Fresh continuation only'
    context=next(r for r in read(ROOT/args.base/'context.json.gz')['rows'] if r['uid']==args.uid)
    source=indexed.module('retained_context','xl-final-script-pass.py')
    row=next(r for r in read(ROOT/args.base/'check-selection.json.gz')['rows'] if r['uid']==args.uid)
    lo,hi=row['native']['model']['worldBounds'];scope={args.uid}|{u for child in old['patches'] for u in child.get('meta',{}).get('targetUids',[])}
    scope.update(b['uid'] for b,_,_ in source.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]))
    resources=[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)]
    resources+=['terrain-patch:'+args.uid,'terrain-surface:'+args.parent]
    claim=reservations.claim('codex-xl-nested-'+str(uuid.uuid4()),resources,batch=args.batch);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),
        '--',sys.executable,__file__,'--uid',args.uid,'--batch',args.batch,'--base',args.base,'--parent',args.parent,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
