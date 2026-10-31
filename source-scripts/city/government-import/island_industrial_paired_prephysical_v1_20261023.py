"""Run the unchanged four-world prephysical suite for three explicit originals."""
import subprocess,sys
from pathlib import Path
from run import ROOT,HERE,save

BASE=ROOT/'docs/astra-city/government-import'
RUNTIME='government-xl-island-industrial-paired-current-runtime-v1-20261023'
ATTRIBUTES='government-xl-island-industrial-three-original-attributes-v1-20261023'

def main():
    out=BASE/'government-xl-island-industrial-paired-prephysical-sequence-v1-20261023'
    assert not out.exists();out.mkdir()
    rows=[]
    for key in ['20270','159422','269430']:
        batch='government-xl-island-industrial-paired-prephysical-'+key+'-v1-20261023'
        command=[sys.executable,str(HERE/'selected_original_prephysical_suite_v4_20261023.py'),'--batch',batch,'--runtime',RUNTIME,'--uid','landsd/'+key+':0','--attributes',ATTRIBUTES]
        with(out/(key+'.log')).open('w')as log:
            result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        rows.append(dict(uid='landsd/'+key+':0',batch=batch,exitCode=result.returncode))
        save(out/'progress.json',dict(rows=rows,installationApproved=False))
        print(rows[-1],flush=True)
    save(out/'terminal.json',dict(rows=rows,installationApproved=False,qualification='Supervisor exit codes only; each child receipt contains actual phase results and failures. No acceptance inferred from supervisor success.'))

if __name__=='__main__':main()
