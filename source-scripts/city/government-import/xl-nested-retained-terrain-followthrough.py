"""Replace one overlapping native terrain child while retaining all source/native gates."""
import argparse
import importlib.util
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations


def load(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('uid','batch','base','parent','child'):p.add_argument('--'+name,required=True)
    p.add_argument('--owned',action='store_true',help=argparse.SUPPRESS);args=p.parse_args()
    assert Path(args.batch).name==args.batch and args.batch.startswith('government-xl-')
    assert (ROOT/args.base).resolve().is_relative_to(ROOT)
    doc=ROOT/'docs/astra-city/government-import'/args.batch;local=HERE/'local'/args.batch
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    assert args.parent in {r['url'] for r in manifest['terrainPatches']}
    old=read(ROOT/'3d-viewer'/args.parent);assert old.get('patches') and not old.get('nativeMesh')
    children=[c for c in old['patches'] if c['id']==args.child];assert len(children)==1
    child=children[0];assert child.get('nativeMesh') and not child.get('patches')
    if args.owned:
        assert reservations.owns(read(local/'reservation.json'))
        save(doc/'nested-child-routing.json',{'parentURL':args.parent,'parentSHA256':digest((ROOT/'3d-viewer'/args.parent).read_bytes()),
            'retainedChildId':args.child,'retainedChildSHA256':digest(json.dumps(child,sort_keys=True,separators=(',',':')).encode()),
            'runnerSHA256':digest(Path(__file__).read_bytes()),
            'contactPipelineSHA256':digest((HERE/'xl-nested-retained-contact.py').read_bytes()),
            'baselinePipelineSHA256':digest((HERE/'xl-contact-resolution-20261005.py').read_bytes()),
            'modelGeometryChanges':0,'scriptExternalAICalls':0,'publication':False})
        indexed=load('nested_retained_indexed','xl-indexed-terrain-continuation.py')
        original=indexed.module
        def configured(name,file):
            if file=='xl-contact-resolution-20261005.py':
                value=original(name,'xl-nested-retained-contact.py')
                value.PARENT_URL=args.parent;value.NESTED_PARENT=True
                value.RETAIN_NESTED_CHILD_ID=args.child;value.ALLOW_BASIC_TERRAIN_TARGETS=True
                return value
            return original(name,file)
        indexed.module=configured
        indexed.TERRAIN_PIPELINE_PATH=HERE/'xl-nested-retained-contact.py'
        indexed.owned(args,doc,local);return
    assert not doc.exists(),'Fresh continuation only; completed evidence is immutable'
    row=next(r for r in read(ROOT/args.base/'check-selection.json.gz')['rows'] if r['uid']==args.uid)
    second=load('nested_retained_bounds','xl-second-pass.py')
    cells=second.resolution.rectangle_for(row['native']['model']['worldBounds'],old)
    c=child['coarseCells'];cells=[max(0,min(cells[0],c[0])),max(0,min(cells[1],c[1])),
                               min(old['w']-1,max(cells[2],c[2])),min(old['h']-1,max(cells[3],c[3]))]
    bounds=second.resolution.extent(cells,old)
    source=load('nested_retained_context','xl-final-script-pass.py')
    scope={args.uid}|{u for c in old['patches'] for u in c.get('meta',{}).get('targetUids',[])}
    scope.update(b['uid'] for b,_,_ in source.load_forms(bounds))
    resources=[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)]
    resources+=['terrain-patch:'+args.uid,'terrain-surface:'+args.parent]
    claim=reservations.claim('codex-xl-nested-retained-'+str(uuid.uuid4()),resources,batch=args.batch);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),
        '--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)


if __name__=='__main__':main()
