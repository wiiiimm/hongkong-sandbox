"""Process two explicit positive original-TIN candidates through complete gates.

Publication remains sequential. Original source/neighbor/browser checks decide
acceptance. An installation emits a commit-required marker for image inspection;
the next independent candidate continues. No modelling AI or Git staging.
"""
import json
import subprocess
import sys
from run import ROOT, read, save
DIR=ROOT/'source-scripts/city/government-import'
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-orchards-complete-contact-followthrough-20261007'
ROWS=[{'uid':'landsd/254621:0','name':'The Orchards Tower 1','base':'government-xl-sustained-131-inputs-20261006','source':'government-xl-two-ground-tin-followthrough-20261007-254621-0-common'}]

def main():
    doc=BASE/BATCH;local=DIR/'local'/BATCH;assert not doc.exists();local.mkdir(parents=True)
    preview=read(BASE/'government-xl-refreshed-current-tin-preview-20261007/result.json')
    positives={r['uid'] for r in preview['rows'] if r['highestOriginalTINPositive']}
    assert all(r['uid'] in positives for r in ROWS)
    outcomes=[]
    for i,row in enumerate(ROWS):
        uid=row['uid'];token=uid.split('/')[1].replace(':','-');batch=BATCH+'-'+token;outcome={**row,'steps':[],'installed':False}
        save(doc/'working-commands.json',{'finished':outcomes,'running':row,'queued':len(ROWS)-i-1,'publication':False,'scriptExternalAICalls':0})
        print(json.dumps({'starting':row}),flush=True)
        def phase(label,script,argv,locked):
            current=batch+'-'+label;command=[sys.executable,str(DIR/script),'--batch',current,*argv]
            if locked:command=['flock',str(DIR/'local/runtime-publication.lock'),*command]
            log=local/(token+'-'+label+'.log')
            with log.open('w') as stream:status=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT).returncode
            path=BASE/current;result=read(path/'result.json') if (path/'result.json').exists() else None
            outcome['steps'].append({'batch':current,'command':command,'returncode':status,'result':result,'log':str(log.relative_to(ROOT))})
            return result,path
        result,physical=phase('contact','xl-footprint-contact-installation-recheck.py',['--base',str((BASE/row['base']).relative_to(ROOT)),'--previous',str((BASE/row['source']).relative_to(ROOT))],True)
        if result and result['reasons'] and all(r.startswith('terrain-regresses-neighbour:') for r in result['reasons']):
            result,physical=phase('preserved','xl-root-footprint-contact-preservation.py',['--uid',uid,'--base',str((BASE/row['base']).relative_to(ROOT)),'--previous',str(physical.relative_to(ROOT))],True)
        if result and result['scriptChecksPassed']:
            result,installed=phase('installed','xl-explicit-footprint-contact-root-install.py',['--uid',uid,'--base',str((BASE/row['base']).relative_to(ROOT)),'--source',str(physical.relative_to(ROOT))],False)
            outcome['installed']=bool(result and result.get('installedUids')==[uid] and result.get('passed'))
            if outcome['installed']:save(doc/('commit-required-'+token+'.json'),{'uid':uid,'installation':str(installed.relative_to(ROOT)),'requiresExportedImageInspection':True})
        outcomes.append(outcome);print(json.dumps({'finished':uid,'installed':outcome['installed'],'reasons':result.get('reasons',[]) if result else ['command-failure-see-log']}),flush=True)
    save(doc/'commands.json',{'rows':outcomes,'newlyInstalled':sum(r['installed'] for r in outcomes),'activeWorkers':0,'queuedFollowups':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'qualification':'Explicit two-source current original-TIN continuation. Full unchanged original acceptance and publication gates; continue the wider active goal after this checkpoint.'})

if __name__=='__main__':main()
