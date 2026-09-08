"""Build an acyclic source-contact closure and stage unchanged native assets for review."""
import json,pathlib,hashlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residual-support-review';read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report=read(DOC/'support-terrain.json');parts={p['uid']:p for p in read(HERE/'input.json')['parts']};rows={r['uid']:r for r in report['rows']};eligible={u for u,r in rows.items()if not r['knownHold'] and not r['counts']['hidden'] and not r['rimCounts']['belowTerrain'] and not r['rimCounts']['noContact'] and r['rimCounts']['samples']>=3};approved={};order=[]
def dependencies(uid):
 pending={i:p for i,p in enumerate(rows[uid]['rim'])if p['gap']>2};result=[]
 while pending:
  choices={}
  for i,p in pending.items():
   for c in p['contacts']:
    usable=c['state']=='installed' or c['state']=='candidate' and c['uid']in approved or c['state']=='surveyed-footprint-fallback' and c['uid']not in eligible
    if usable:
     key=(c['uid'],c['state']);choices.setdefault(key,{'contact':c,'points':set()})['points'].add(i)
  if not choices:return None
  chosen=min(choices.values(),key=lambda x:(-len(x['points']),x['contact']['state']=='surveyed-footprint-fallback',x['contact']['uid']));result.append(chosen['contact']);pending={i:p for i,p in pending.items()if i not in chosen['points']}
 return result
while True:
 added=False
 for uid in sorted(eligible-set(approved)):
  deps=dependencies(uid)
  if deps is not None:approved[uid]=deps;order.append(uid);added=True
 if not added:break
sources={m['uid']:m for m in read(DOC/'native-meshes.json')['rows']};folder=HERE/'candidates';folder.mkdir(exist_ok=True);models=[]
for uid in order:
 p=parts[uid];m=dict(p['candidate']);src=pathlib.Path(sources[uid]['sourcePath']);assert sha(src)==m['sha256'];shutil.copyfile(src,folder/m['asset']);m.update(priority='landmark',supportDependencies=approved[uid]);models.append(m)
cat=read(ROOT/'source-scripts/city/residential-support-review/support-catalogue.json');cat['models']=models;cat['counts']['packedModels']=len(models);(folder/'catalogue.json').write_text(json.dumps(cat,indent=2)+'\n');(HERE/'visual-selection.json').write_text(json.dumps({'snapshot':'11a25ce297101f9e','parts':[{'uid':u,'name':parts[u]['name'],'landmarks':parts[u]['landmarkIds']}for u in order]},indent=2)+'\n');(DOC/'decisions.json').write_text(json.dumps({'issue':'HKS-214','approvedForVisual':order,'held':sorted(set(parts)-set(approved)),'supportDependencies':approved,'method':'Greedy exact-contact cover using installed, already ordered candidate, or deliberately retained ineligible fallback support only. Candidate edges always point to an earlier source component; incidental mutual seams cannot create cycles. Visual and architectural acceptance pending.'},indent=2)+'\n');print(json.dumps({'staged':len(models),'held':len(parts)-len(models),'uids':order}))
