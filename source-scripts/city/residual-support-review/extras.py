import json,pathlib,sys,uuid,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residual-support-review';sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
read=lambda p:json.loads(p.read_bytes())
for p in ['/tmp/astra-residual-visual-lease.json','/tmp/astra-residual-estimates-lease.json']:
 r=read(pathlib.Path(p)); reservations.heartbeat(r)
r=reservations.claim('residual-extras-'+str(uuid.uuid4()),['building:landsd/179500:0','building:landsd/272501:0'],batch='HKS-214-residual-neighbours');assert r['ok'],r;pathlib.Path('/tmp/astra-residual-extras-lease.json').write_text(json.dumps(r['reservation'],default=str))
cat=read(ROOT/'source-scripts/city/landmark-identity-followup/candidates/catalogue.json');folder=HERE/'extras';folder.mkdir(exist_ok=True)
for m in cat['models']:
 m['priority']='landmark';shutil.copyfile(ROOT/'source-scripts/city/landmark-identity-followup/candidates'/m['asset'],folder/m['asset'])
(folder/'catalogue.json').write_text(json.dumps(cat,indent=2)+'\n');(HERE/'extras-selection.json').write_text(json.dumps({'snapshot':'11a25ce297101f9e','parts':[{'uid':m['uid'],'name':m['label']}for m in cat['models']]},indent=2)+'\n')
s=(HERE/'browser.mjs').read_text().replace('visual-selection.json','extras-selection.json').replace("base='source-scripts/city/residual-support-review/candidates/'","base='source-scripts/city/residual-support-review/extras/'").replace('residual-support-review/framing/','residual-support-review/extras-framing/');(HERE/'extras-browser.generated.mjs').write_text(s)
print('Claimed two extras; renewed main and estimates')
