"""Exact binding of the two separately accepted proofs, without schema coercion."""
UIDS={'landsd/231645:0','landsd/239465:0'}
def verify(replayed,stored,uid,policy):
 assert uid in UIDS and isinstance(stored,dict) and set(stored)=={'rows'}
 rows=stored['rows'];assert isinstance(rows,list) and len(rows)==2
 assert {p['uid'] for p in rows}==UIDS and len({p['uid'] for p in rows})==2
 assert all(p['passed'] and p['reasons']==[] and p['policy']==policy for p in rows)
 expected=next(p for p in rows if p['uid']==uid)
 assert replayed['uid']==uid and replayed==expected,'Positive identity proof changed'
 return replayed
