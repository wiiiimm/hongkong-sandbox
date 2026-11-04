"""No-write adverse tests for exact two-original/one-XL installation accounting."""
import copy
import pool_guarded_publish_v1_20261017 as g
s=g.stage
prior=s.read(s.BASE/'government-xl-science-museum-original-installed-v1-20261016/full-xl-current-count.json')
models=s.read(s.HERE/'local/government-xl-sham-shui-po-pool-original-group-browser-v5-20261017/catalogue.json')['models']
p=next(r for r in prior['rows']if r['uid']==s.PODIUM)
next(m for m in models if m['uid']==s.PODIUM)['originalSourceKey']=p['sourceKey']
kw=dict(manifest_sha=prior['manifestSHA256'],snapshot=prior['snapshotId']);delta=g.inventory_delta(prior,models,**kw);assert delta['returnedModels']==2 and delta['expectedFixedXLDelta']==1
cases=[]
def rejects(label,previous,entries,args):
 try:g.inventory_delta(previous,entries,**args)
 except AssertionError:cases.append(label)
 else:raise AssertionError(label+' not rejected')
rejects('stale map',prior,models,{**kw,'manifest_sha':'stale'})
rejects('stale snapshot',prior,models,{**kw,'snapshot':'stale'})
changed=copy.deepcopy(models);changed[0]['sha256']='changed';rejects('changed source',prior,changed,kw)
changed=copy.deepcopy(prior);next(r for r in changed['rows']if r['uid']==s.PODIUM)['installedVerified']=True;rejects('already installed',changed,models,kw)
changed=copy.deepcopy(models);next(m for m in changed if m['uid']==s.PODIUM)['originalSourceKey']='wrong';rejects('wrong source key',prior,changed,kw)
rejects('duplicate model',prior,models+models[:1],kw)
rejects('missing support source',prior,[m for m in models if m['uid']==s.PODIUM],kw)
print(dict(delta=delta,rejected=cases))
