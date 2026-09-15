"""Select the verified 11-component estate assembly from retained government packs."""
import json,hashlib,shutil,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent;read=lambda p:json.loads(p.read_bytes())
rows=read(HERE/'selected-sources.json');out=HERE/'candidates';out.mkdir(exist_ok=True);models=[]
c=sqlite3.connect('file:'+str(ROOT/'source-scripts/city/building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
for row in rows:
 cat=read(HERE/'local'/row['sheet']/'converted/catalogue.json');uid=row['model']['matching']['viewerMatches'][0]['uid'];m=next(x for x in cat['models']if x['uid']==uid);b=c.execute('select * from buildings where uid=?',(uid,)).fetchone();assert b and m['buildingCSUID']==b['csuid']
 source=HERE/'local'/row['sheet']/'converted'/m['asset'];assert hashlib.sha256(source.read_bytes()).hexdigest()==m['sha256'];destination=out/m['asset'];destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
 m['label']=b['name'];m['priority']='landmark';m['sourceIdentityReviewed']=True;m['identityReviewApproved']=True;m['reviewIssue']='HKS-226'
 if uid not in ('landsd/324574:0','landsd/105379:0'):m['supportDependencies']=[{'uid':'landsd/105379:0','state':'candidate'}]
 models.append(m)
cat.update(area='Whampoa Garden Sites 8 and 12',counts={'packedModels':len(models)},models=models)
(out/'catalogue.json').write_text(json.dumps(cat,indent=2)+'\n');(out/'catalogue-index.json').write_text(json.dumps({'catalogues':['catalogue.json'],'models':len(models)}))
plan={'areas':[{'area':'Whampoa Garden Site 8 and Site 12','catalogue':str((out/'catalogue.json').relative_to(ROOT)),'destination':'city/data/official-models/whampoa-estates-high/catalogue.json'}]};(HERE/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
print('Staged',len(models),'native source components',sum(m['bytes']for m in models),'bytes')
