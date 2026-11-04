"""Repair only candidate edges between exact, already installed source actors.

This is a metadata proof, never source/identity/physical acceptance. Existing
fallback/legacy relations, all geometry, poses, source fields and graph edges
are retained. No review state is changed or installation credit granted.
"""
import copy
import re

def proposal(catalogues,reviews,forms,assets):
    entries={}
    for path,cat in catalogues.items():
        for e in cat['models']:
            assert e['uid'] not in entries,'Duplicate runtime UID'
            entries[e['uid']]=(e,path)
    changes=[];unresolved=[];after=copy.deepcopy(catalogues)
    def actor(uid):
        assert uid in entries,'Missing native actor'
        e,path=entries[uid]
        assert reviews.get(uid)==('installed-verified',e['sha256']),'Not installed with exact reviewed bytes'
        assert assets.get(uid)==dict(sha256=e['sha256'],bytes=e['bytes']),'Source asset binding changed'
        f=forms[uid];assert f['uid']==uid and f['buildingCSUID']==e['buildingCSUID'],'Current stable identity changed'
        if 'objectId' in e:assert str(f['objectId'])==str(e['objectId']),'Current original object ID changed'
        return e
    for uid,(e,path) in entries.items():
        for i,d in enumerate(e.get('supportDependencies',[])):
            if not isinstance(d,dict) or d.get('state')!='candidate':
                if not isinstance(d,dict) or d.get('state')!='installed':unresolved.append(dict(uid=uid,dependencyIndex=i,dependency=d,reason='Existing fallback or legacy relation retained; no native installation inferred'))
                continue
            assert re.fullmatch(r'landsd/\d+:0',d['uid']) and d['uid']!=uid,'Invalid/self dependency'
            own=actor(uid);support=actor(d['uid']);csuid=support['buildingCSUID']
            assert d.get('csuid',csuid)==csuid,'Existing CSUID changed'
            assert d.get('sha256',support['sha256'])==support['sha256'],'Existing support hash changed'
            new=copy.deepcopy(d);new['state']='installed';new['csuid']=csuid
            entry=next(x for x in after[path]['models'] if x['uid']==uid)
            entry['supportDependencies'][i]=new
            changes.append(dict(uid=uid,supportUID=d['uid'],catalogue=path,dependencyIndex=i,before=d,after=new,ownSourceSHA256=own['sha256'],supportSourceSHA256=support['sha256']))
    # Existing exact edge directions must remain acyclic; metadata cannot turn
    # an invalid support graph into an accepted one or introduce a new edge.
    graph={uid:[d['uid'] for d in e.get('supportDependencies',[]) if isinstance(d,dict) and d.get('state') in ('candidate','installed')] for uid,(e,_) in entries.items()}
    active=set();done=set()
    def visit(uid):
        assert uid not in active,'Cyclic dependency'
        if uid in done:return
        active.add(uid)
        for other in graph.get(uid,[]):visit(other)
        active.remove(uid);done.add(uid)
    for uid in graph:visit(uid)
    return dict(catalogues=after,changes=changes,retainedRelations=unresolved,newlyInstalled=0,sourceGeometryChanges=0,reviewStateChanges=0,identityAcceptance=False,physicalAcceptance=False)

def verify(before,after,reviews,forms,assets):
    expected=proposal(before,reviews,forms,assets)
    assert after==expected['catalogues'],'Unapproved catalogue/source/pose/edge change'
    return expected
