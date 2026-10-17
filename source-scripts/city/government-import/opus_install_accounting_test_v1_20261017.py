"""No-write adverse tests for exact three-original/one-XL installation accounting."""
import copy
import opus_guarded_publish_v1_20261017 as g
s=g.stage
prior=s.read(s.PREVIOUS)
models=s.read(s.STAGE/'catalogue.json')['models']
kw=dict(manifest_sha=prior['manifestSHA256'],snapshot=prior['snapshotId']);delta=g.inventory_delta(prior,models,**kw);assert delta['returnedModels']==3 and delta['expectedFixedXLDelta']==1
cases=[]
def rejects(label,previous,entries,args):
 try:g.inventory_delta(previous,entries,**args)
 except AssertionError:cases.append(label)
 else:raise AssertionError(label+' not rejected')
rejects('stale map',prior,models,{**kw,'manifest_sha':'stale'})
rejects('stale snapshot',prior,models,{**kw,'snapshot':'stale'})
changed=copy.deepcopy(models);changed[0]['sha256']='changed';rejects('changed source',prior,changed,kw)
changed=copy.deepcopy(prior);next(r for r in changed['rows']if r['uid']==s.TOWER)['installedVerified']=True;rejects('already installed',changed,models,kw)
changed=copy.deepcopy(models);next(m for m in changed if m['uid']==s.TOWER)['originalSourceKey']='wrong';rejects('wrong source key',prior,changed,kw)
rejects('duplicate model',prior,models+models[:1],kw)
rejects('missing support source',prior,[m for m in models if m['uid']==s.TOWER],kw)
print(dict(delta=delta,rejected=cases))
