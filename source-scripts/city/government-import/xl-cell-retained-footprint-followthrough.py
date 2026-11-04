"""Candidate-only explicit-cell retained terrain; complete physical gates unchanged."""
import argparse, json, subprocess, sys, uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
import importlib.util
spec=importlib.util.spec_from_file_location('indexed',HERE/'xl-cell-indexed-terrain-continuation.py')
indexed=importlib.util.module_from_spec(spec);spec.loader.exec_module(indexed)
indexed.TERRAIN_PIPELINE_PATH=HERE/'xl-cell-retained-footprint-contact.py'

def main():
    p=argparse.ArgumentParser();p.add_argument('--uid',required=True);p.add_argument('--batch',required=True)
    p.add_argument('--base',required=True);p.add_argument('--retained',required=True);p.add_argument('--owned',action='store_true')
    p.add_argument('--cells',required=True,help='Explicit root coarse cells c0,r0,c1,r1; full source 10 m transition and retained coverage required')
    p.add_argument('--allow-basic-targets',action='store_true',help='Retain declared basic forms with basic-neighbour gates; full native checks remain required for actual installed models')
    p.add_argument('--model-regions-only',action='store_true',help='Candidate preserving exact old terrain at declared native meshes; original TIN elsewhere must pass all existing neighbour gates')
    args=p.parse_args();assert Path(args.batch).name==args.batch and args.batch.startswith('government-xl-')
    doc=ROOT/'docs/astra-city/government-import'/args.batch;local=HERE/'local'/args.batch
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    assert args.retained in {r['url'] for r in manifest['terrainPatches']}
    old=read(ROOT/'3d-viewer'/args.retained);assert old.get('nativeMesh') and not old.get('patches')
    if args.owned:
        assert reservations.owns(read(local/'reservation.json'))
        save(doc/'retained-routing.json',{'retainedURL':args.retained,'retainedSHA256':digest((ROOT/'3d-viewer'/args.retained).read_bytes()),
             'runnerSHA256':digest(Path(__file__).read_bytes()),'explicitCells':[int(c) for c in args.cells.split(',')],'candidatePreparationOnly':True,'modelGeometryChanges':0,'scriptExternalAICalls':0})
        original=indexed.module
        def configured(name,filename):
            value=original(name,'xl-cell-retained-footprint-contact.py' if filename=='xl-cell-contact-resolution.py' else filename)
            if filename=='xl-cell-contact-resolution.py':
                value.RETAIN_NATIVE_URL=args.retained
                value.EXPLICIT_CELLS=[int(c) for c in args.cells.split(',')]
                value.ALLOW_BASIC_TERRAIN_TARGETS=args.allow_basic_targets
                value.RETAIN_NATIVE_MODEL_REGIONS_ONLY=args.model_regions_only
            return value
        indexed.module=configured;indexed.owned(args,doc,local);return
    assert not doc.exists(),'Fresh continuation only'
    context=next(r for r in read(ROOT/args.base/'context.json.gz')['rows'] if r['uid']==args.uid)
    source=indexed.module('retained_context','xl-final-script-pass.py')
    row=next(r for r in read(ROOT/args.base/'check-selection.json.gz')['rows'] if r['uid']==args.uid)
    lo,hi=row['native']['model']['worldBounds'];scope={args.uid,*old['meta']['targetUids']}
    scope.update(b['uid'] for b,_,_ in source.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]))
    resources=[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)]
    resources+=['terrain-patch:'+args.uid,'terrain-surface:'+args.retained]
    claim=reservations.claim('codex-xl-owned-retained-'+str(uuid.uuid4()),resources,batch=args.batch);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),
        '--',sys.executable,__file__,'--uid',args.uid,'--batch',args.batch,'--base',args.base,'--retained',args.retained,'--cells',args.cells,
        *(['--allow-basic-targets'] if args.allow_basic_targets else []),
        *(['--model-regions-only'] if args.model_regions_only else []),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
