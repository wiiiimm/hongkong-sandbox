"""Advance eligible failed primary stages through existing deterministic terrain routes."""
import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from terrain_diagnostic_resolution import resolve_global_bottom_warning


def retained_url(result):
    for reason in result['reasons']:
        prefix='terrain-construction-guard:'
        if not reason.startswith(prefix):continue
        try:value=ast.literal_eval(reason[len(prefix):])
        except (ValueError,SyntaxError):continue
        if isinstance(value,tuple) and len(value)==2 and value[0]=='Requires retained native patch handling' and isinstance(value[1],list) and len(value[1])==1:
            return value[1][0]
    return None


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',required=True);p.add_argument('--primary',required=True);p.add_argument('--batch',required=True)
    args=p.parse_args();assert Path(args.batch).name==args.batch and args.batch.startswith('government-xl-')
    base=(ROOT/args.base).resolve();primary=(ROOT/args.primary).resolve()
    assert base.is_relative_to(ROOT) and primary.is_relative_to(ROOT)
    rows=read(primary/'commands.json')['rows']
    assert 1<=len(rows)<=200 and len({r['uid'] for r in rows})==len(rows)
    unresolved=[{'uid':r['uid'],'batch':r['batch'],'returncode':r['returncode'],
                 'reason':'Primary command did not produce a complete verified result'}
                for r in rows if r['returncode']!=0 or not r['result']]
    doc=ROOT/'docs/astra-city/government-import'/args.batch;local=HERE/'local'/args.batch
    assert not doc.exists(),'Completed follow-up evidence is immutable'
    local.mkdir(parents=True,exist_ok=True);outcomes=[]
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');urls={r['url'] for r in manifest['terrainPatches']}
    for row in rows:
        if row['returncode']!=0 or not row['result']:continue
        result=row['result'];uid=row['uid'];previous=ROOT/'docs/astra-city/government-import'/row['batch']
        url=retained_url(result);command=None;route=None
        child=args.batch+'-'+uid.split('/')[1].replace(':','-')
        if url:
            assert url in urls,'Reported retained terrain is no longer current'
            parent=read(ROOT/'3d-viewer'/url)
            if parent.get('nativeMesh') and not parent.get('patches'):
                route='retained-native'
                command=[sys.executable,str(HERE/'xl-retained-terrain-followthrough.py'),'--uid',uid,'--batch',child,
                    '--base',args.base,'--retained',url,'--allow-basic-targets']
            elif parent.get('patches') and not parent.get('nativeMesh'):
                route='nested-grid'
                command=[sys.executable,str(HERE/'xl-nested-terrain-followthrough.py'),'--uid',uid,'--batch',child,
                    '--base',args.base,'--parent',url]
        elif (previous/'terrain-candidates.json').exists():
            terrain=read(previous/'terrain-candidates.json')[0]
            # This rule can preserve only disjoint basic footprints against the
            # root parent. Native/grid replacements retain their separate gates.
            patch=read(ROOT/terrain['path'])
            assert digest((ROOT/terrain['path']).read_bytes())==terrain['sha256']
            root_parent=(patch.get('meta',{}).get('parentTerrain')=='city/data/terrain.json'
                         and patch['meta'].get('parentSha256')==digest((ROOT/'3d-viewer/city/data/terrain.json').read_bytes()))
            if (not terrain.get('replaces') and patch.get('nativeMesh') and not patch.get('patches')
                    and root_parent and (previous/'native-neighbour-checks.json').exists()):
                source=read(previous/'selection.json.gz')['rows'][0]
                # Read existing derived geometry for routing only; the child
                # reacquires complete scope and reconstructs/checks source bytes.
                geometry=read(HERE/'local'/row['batch']/'runtime-geometry.json.gz')
                for path,sha in geometry['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
                original=next(r for r in geometry['rows'] if r['uid']==uid)
                assert original['sourceSHA256']==source['sourceSHA256']
                triangles=np.asarray(original['position']).reshape(-1,3)[np.asarray(original['index']).reshape(-1,3)]
                projection=shapely.union_all(shapely.polygons(triangles[:,:,[0,2]]))
                inputs={r['building']['uid']:r for r in read(previous/'neighbour-inputs.json.gz')['rows']}
                resolved=set(read(previous/'native-neighbour-checks.json')['resolved'])
                failed=read(previous/'neighbour-checks.json')['rows']
                disjoint=[]
                for check in failed:
                    if not check['reasons'] or check['uid'] in resolved:continue
                    neighbour=inputs[check['uid']];b=neighbour['building']
                    area=Polygon(b['rings'][0],b['rings'][1:]).buffer(.01,join_style='mitre').intersection(projection).area
                    if not neighbour['existingNative'] and area<1e-8:disjoint.append(check['uid'])
                if disjoint:
                    route='disjoint-basic-parent'
                    command=[sys.executable,str(HERE/'xl-disjoint-parent-preservation.py'),'--previous',str(previous.relative_to(ROOT)),'--batch',child]
        if command is None and (previous/'foundation.json').exists():
            resolution=resolve_global_bottom_warning(
                read(previous/'validation.json')['results'][0],
                read(previous/'metrics.json')['rows'][0],
                read(previous/'foundation.json')['rows'][0])
            if resolution['resolved'] and set(result['reasons'])<=set(resolution['resolved']):
                route='complete-foundation-diagnostic-recheck'
                command=[sys.executable,str(HERE/'xl-recheck-candidate-evidence.py'),
                         '--previous',str(previous.relative_to(ROOT)),'--batch',child]
        if command is None:continue
        print(json.dumps({'starting':uid,'route':route,'child':child}),flush=True)
        log=local/(child+'.log')
        with log.open('w') as output:proc=subprocess.run(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT)
        target=ROOT/'docs/astra-city/government-import'/child
        latest=read(target/'result.json') if (target/'result.json').exists() else None
        outcomes.append({'uid':uid,'name':row['name'],'batch':child,'route':route,'command':command,'returncode':proc.returncode,
                         'log':str(log.relative_to(ROOT)),'result':latest})
        save(doc/'working-commands.json',{'batch':args.batch,'rows':outcomes})
        print(json.dumps({'completed':uid,'route':route,'returncode':proc.returncode,'reasons':latest and latest['reasons']}),flush=True)
    save(doc/'commands.json',{'batch':args.batch,'rows':outcomes,'primarySources':len(rows),'unresolvedPrimaryCommands':unresolved,'newlyInstalled':0,
        'scriptExternalAICalls':0,'qualification':'Existing guarded terrain routes only. Construction/support failures remain explicit. No publication or source-geometry changes.'})


if __name__=='__main__':main()
