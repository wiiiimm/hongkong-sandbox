"""Validate only two explicit installed dependency metadata corrections."""
import copy
EXPECTED={'landsd/263590:0':('landsd/232907:0','3402214912P20060312'),'landsd/268032:0':('landsd/101781:0','3373315774P20190430')}
def corrected(entry,support):
 out=copy.deepcopy(entry);uid=entry['uid'];assert uid in EXPECTED
 dependency,csuid=EXPECTED[uid];assert support['uid']==dependency and support['buildingCSUID']==csuid
 assert entry['supportDependencies']==[dict(entry['supportDependencies'][0])]
 d=out['supportDependencies'][0];assert d['uid']==dependency and d['state']=='candidate'
 assert d.get('csuid',csuid)==csuid
 if 'sha256' in d:assert d['sha256']==support['sha256']
 d['state']='installed';d['csuid']=csuid
 return out
def verify(before,after,support):
 assert after==corrected(before,support),'Unapproved metadata/source/edge change'
 assert before['uid']==after['uid'] and before['sha256']==after['sha256']
 return True
