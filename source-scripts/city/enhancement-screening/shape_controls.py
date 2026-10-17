"""Construct comparison test inputs from existing installed landmarks, without modelling."""
import argparse
import gzip
import json
from pathlib import Path
import subprocess
from shape_prepare import ROOT, HERE, read, save
from shape_metrics import compare

# Existing user-recognised landmarks; these are regression controls, not new reviews.
CONTROLS={'landsd/318723:0':'Kai Tak Stadium','landsd/244915:0':'Two IFC','landsd/89275:0':'HSBC',
          'landsd/77406:0':'Cultural Centre','landsd/252854:0':'Space Museum component A',
          'landsd/211468:0':'Space Museum component B','landsd/252061:0':'Space Museum component C'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=HERE/'local/controls');p.add_argument('--report',type=Path,default=ROOT/'docs/astra-city/enhancement-screening/shape-pilot-1000/landmark-controls.json');a=p.parse_args()
    m=read(ROOT/'3d-viewer/city/data/manifest.json');entries={};buildings={}
    for url in m['officialModelCatalogues']:
        c=read(ROOT/'3d-viewer'/url)
        for e in c['models']:
            if e['uid'] in CONTROLS:entries[e['uid']]={'entry':{**e,'rootTranslation':c['rootTranslation']},'path':str(((ROOT/'3d-viewer'/url).parent/e['asset']).resolve())}
    for tile in m['tiles']:
        for b in read(ROOT/'3d-viewer'/tile['url'])['buildings']:
            if b['uid'] in CONTROLS:buildings[b['uid']]=b
    rows=[]
    for uid,label in CONTROLS.items():
        if uid not in entries or uid not in buildings:raise ValueError('Missing landmark control '+uid)
        b=dict(buildings[uid]);b.pop('modelGeometry',None)
        rows.append({'uid':uid,'building':b,'candidate':entries[uid],'currentNative':None})
    a.out.mkdir(parents=True,exist_ok=True);save(a.out/'inputs.json',{'rows':rows})
    subprocess.run(['node',str(HERE/'shape_geometry.mjs'),str(a.out/'inputs.json'),str(a.out/'geometry')],check=True,cwd=ROOT)
    index=read(a.out/'geometry/index.json');results=[]
    for row in index['rows']:
        if row.get('error'):raise ValueError(row['error'])
        d=json.loads(gzip.decompress((a.out/'geometry'/row['file']).read_bytes()));metrics=compare(d['current'],d['candidate'])
        results.append({'uid':row['uid'],'name':CONTROLS[row['uid']],'test':'existing-fallback-versus-installed-original','comparison':metrics['comparison'],'metrics':metrics,'geometryFile':row['file']})
    # Kai Tak is an explicit user-approved positive control from the prior port.
    kai=next(r for r in results if r['uid']=='landsd/318723:0')
    assert kai['comparison']=='material-difference','Kai Tak roof regression'
    save(a.report,{'results':results,'aiCalls':0,'modelChanges':0,'qualification':'Regression comparisons use existing geometry. Only the prior Kai Tak approval is a labelled positive; other components are diagnostic controls, not fresh architectural judgements.'})
    print(json.dumps([{k:r[k] for k in ['uid','name','comparison']} for r in results]))

if __name__=='__main__':main()
