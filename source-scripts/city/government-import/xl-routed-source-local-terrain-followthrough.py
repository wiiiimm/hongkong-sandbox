"""Continue exact owned government identity with multiple disjoint retained native patches and full physical gates."""
import argparse, json, subprocess, sys, uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
import importlib.util
spec=importlib.util.spec_from_file_location('indexed',HERE/'xl-routed-source-local-indexed-terrain.py')
indexed=importlib.util.module_from_spec(spec);spec.loader.exec_module(indexed)

def main():
    p=argparse.ArgumentParser();p.add_argument('--uid',required=True);p.add_argument('--batch',required=True)
    p.add_argument('--base',required=True);p.add_argument('--retained',required=True,action='append');p.add_argument('--owned',action='store_true')
    p.add_argument('--allow-basic-targets',action='store_true',help='Retain declared basic forms with basic-neighbour gates; full native checks remain required for actual installed models')
    p.add_argument('--model-regions-only',action='store_true',help='Candidate preserving exact old terrain at declared native meshes; original TIN elsewhere must pass all existing neighbour gates')
    args=p.parse_args();assert Path(args.batch).name==args.batch and args.batch.startswith('government-xl-')
    doc=ROOT/'docs/astra-city/government-import'/args.batch;local=HERE/'local'/args.batch
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    assert len(args.retained)>=2 and len(set(args.retained))==len(args.retained)
    old_patches=[]
    for url in args.retained:
        assert url in {r['url'] for r in manifest['terrainPatches']}
        old=read(ROOT/'3d-viewer'/url);assert old.get('nativeMesh') and not old.get('patches')
        old_patches.append(old)
    if args.owned:
        assert reservations.owns(read(local/'reservation.json'))
        save(doc/'retained-routing.json',{'retainedParents':[{'url':url,'sha256':digest((ROOT/'3d-viewer'/url).read_bytes())} for url in args.retained],
             'runnerSHA256':digest(Path(__file__).read_bytes()),'modelGeometryChanges':0,'scriptExternalAICalls':0})
        original=indexed.module
        def configured(name,filename):
            value=original(name,filename)
            if filename=='xl-routed-source-local-contact-resolution.py':
                value.RETAIN_NATIVE_URLS=args.retained
                value.ALLOW_BASIC_TERRAIN_TARGETS=args.allow_basic_targets
                value.RETAIN_NATIVE_MODEL_REGIONS_ONLY=args.model_regions_only
            return value
        indexed.module=configured;indexed.owned(args,doc,local);return
    assert not doc.exists(),'Fresh continuation only'
    context=next(r for r in read(ROOT/args.base/'context.json.gz')['rows'] if r['uid']==args.uid)
    source=indexed.module('retained_context','xl-final-script-pass.py')
    row=next(r for r in read(ROOT/args.base/'check-selection.json.gz')['rows'] if r['uid']==args.uid)
    lo,hi=row['native']['model']['worldBounds'];scope={args.uid}
    from shapely.geometry import box
    import native_patch_resolution as patches
    bounds=[lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]
    for i,old in enumerate(old_patches):
        scope.update(old['meta']['targetUids'])
        b=patches._patch_bounds(old);bounds=[min(bounds[0],b[0]),min(bounds[1],b[1]),max(bounds[2],b[2]),max(bounds[3],b[3])]
        for other in old_patches[i+1:]:assert box(*b).intersection(box(*patches._patch_bounds(other))).area<1e-8, 'Overlapping retained parents'
    terrain=indexed.module('multi_retained_terrain','xl-second-pass.py')
    parent=read(ROOT/'3d-viewer/city/data/terrain.json')
    cells=terrain.resolution.rectangle_for([[bounds[0],0,bounds[1]],[bounds[2],0,bounds[3]]],parent)
    bounds=terrain.resolution.extent(cells,parent)
    scope.update(b['uid'] for b,_,_ in source.load_forms(bounds))
    resources=[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)]
    resources+=['terrain-patch:'+args.uid]+['terrain-surface:'+url for url in args.retained]
    claim=reservations.claim('codex-xl-owned-retained-'+str(uuid.uuid4()),resources,batch=args.batch);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),
        '--',sys.executable,__file__,'--uid',args.uid,'--batch',args.batch,'--base',args.base,*[part for url in args.retained for part in ['--retained',url]],
        *(['--allow-basic-targets'] if args.allow_basic_targets else []),
        *(['--model-regions-only'] if args.model_regions_only else []),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
