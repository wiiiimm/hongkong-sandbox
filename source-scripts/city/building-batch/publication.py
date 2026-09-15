"""Conservative trial selection and publication through the existing guarded publisher."""
import argparse, collections, hashlib, importlib.util, json, pathlib, shutil, sqlite3, sys
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_bytes())
def write(p,d): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def disposition(model, result, building):
    reasons=list(result.get('concerns',[]))
    if result.get('outcome')!='runtime-accepted-placement-unreviewed': reasons.append('validation-exception')
    if building['source_base'] is None or building['source_top'] is None: reasons.append('missing-survey-height-pair')
    elif (abs(model['worldBounds'][0][1]-building['source_base'])>3 or
          abs(model['worldBounds'][1][1]-building['source_top'])>max(5,building['height']*.15)):
        reasons.append('survey-height-disagreement')
    return sorted(set(reasons))
def prepare(root):
    work=root/'source-scripts/city/building-batch/local';source=work/'candidates';out=work/'publication';out.mkdir(exist_ok=True)
    validation=read(source/'validation.json');catalogue=read(source/'catalogue.json')
    # Bind decisions to current viewer/terrain and the actual candidate byte snapshot.
    for path,expected in validation['hashes'].items():
        p=root/path if path.startswith(('3d-viewer/','source-scripts/')) else source/path
        if not p.resolve().is_relative_to(root.resolve()): raise ValueError('Evidence path escapes repository')
        if sha(p)!=expected: raise ValueError('Validation input changed: '+path)
    by_uid={r['uid']:r for r in validation['results']}
    if set(by_uid)!={m['uid'] for m in catalogue['models']}: raise ValueError('Validation membership mismatch')
    db=sqlite3.connect(work/'buildings.sqlite');db.row_factory=sqlite3.Row
    accepted=[];held=[];samples=[]
    try:
        for model in catalogue['models']:
            b=db.execute('SELECT * FROM buildings WHERE uid=? AND active=1',(model['uid'],)).fetchone()
            if b is None: raise ValueError('Missing building '+model['uid'])
            reasons=disposition(model,by_uid[model['uid']],b)
            if reasons:
                held.append(dict(uid=model['uid'],name=b['name'],reasons=reasons,sourceYBounds=[model['worldBounds'][0][1],model['worldBounds'][1][1]],surveyBaseTop=[b['source_base'],b['source_top']],terrain=by_uid[model['uid']].get('terrain'),error=by_uid[model['uid']].get('error')))
                continue
            path=source/model['asset']
            if sha(path)!=model['sha256']: raise ValueError('Candidate bytes changed')
            shutil.copyfile(path,out/model['asset'])
            model=dict(model,priority='detail',placementReviewed=False,placementScreening='tourist-trial-conservative-v1')
            accepted.append(model)
    finally: db.close()
    # Representative architecture, sizes and neighbourhoods, with identical before/after viewpoints.
    sample_ids=['landsd/4447:0','landsd/4020:0','landsd/322270:0','landsd/91840:0','landsd/174153:0','landsd/109666:0','landsd/109672:0','landsd/123869:0','landsd/335416:0','landsd/100139:0']
    selected={m['uid']:m for m in accepted}
    if not all(uid in selected for uid in sample_ids): raise ValueError('Review sample left passing set; revise review deliberately')
    areas=[];fingerprints={}
    for offset in range(0,len(accepted),512):
        part=accepted[offset:offset+512];name=f'catalogue-{offset//512:03d}.json'
        c=dict(catalogue,counts={'packedModels':len(part)},models=part,loadingPolicy='Conservative trial: stream only after runtime verification; retain basic fallback on failures.')
        write(out/name,c);fingerprints[str((out/name).relative_to(root))]=sha(out/name)
        areas.append(dict(area='Central tourist trial',catalogue=str((out/name).relative_to(root)),destination=f'city/data/official-models/tourist-trial-{offset//512:03d}/catalogue.json'))
    report=dict(accepted=len(accepted),held=len(held),compressedBytes=sum(m['bytes'] for m in accepted),heldReasons=dict(collections.Counter(reason for h in held for reason in h['reasons'])),policy={'maxBaseDisagreementMetres':3,'maxTopDisagreementMetres':'max(5, 15% of surveyed height)','terrain':'no sampled validation warnings'},validationSHA256=sha(source/'validation.json'),candidateCatalogueSHA256=sha(source/'catalogue.json'),toolSHA256=sha(pathlib.Path(__file__)),samples=sample_ids,limits=['Screening plus representative browser review; not exhaustive architectural/foundation certification.','All held candidates retain original basic forms; no source height or terrain changes.'])
    write(out/'plan.json',dict(areas=areas));write(out/'screening.json',report);write(out/'held.json',held);write(out/'samples.json',[selected[uid] for uid in sample_ids]);write(out/'guard.json',dict(inputs={str((source/'validation.json').relative_to(root)):sha(source/'validation.json'),**{k:v for k,v in validation['hashes'].items() if k.startswith('3d-viewer/')},**fingerprints},planSHA256=sha(out/'plan.json')))
    return report

def publish(root,apply):
    work=root/'source-scripts/city/building-batch/local/publication';guard=read(work/'guard.json')
    for p,expected in guard['inputs'].items():
        if sha(root/p)!=expected: raise ValueError('Reviewed input changed: '+p)
    if sha(work/'plan.json')!=guard['planSHA256']: raise ValueError('Publication plan changed')
    spec=importlib.util.spec_from_file_location('shared_guarded_publisher',root/'source-scripts/city/island-detail-integration/publish.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.ROOT=root;module.DOC=root/'docs/astra-city/building-batch/visual-trial'
    sys.argv=['publish.py',str((work/'plan.json').relative_to(root))]+(['--apply'] if apply else [])
    module.main()
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','publish']);p.add_argument('--root',type=pathlib.Path,default=ROOT);p.add_argument('--apply',action='store_true');a=p.parse_args()
    if a.command=='prepare':print(json.dumps(prepare(a.root.resolve()),indent=2))
    else:publish(a.root.resolve(),a.apply)
