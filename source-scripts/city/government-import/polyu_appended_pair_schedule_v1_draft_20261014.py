"""Only schedules complete STRtree hits; no geometry or acceptance arithmetic."""
def schedule(query_ids,all_ids,left,right,prefix):
 assert len(left)==len(right)and query_ids==sorted(set(query_ids))and all_ids==sorted(set(all_ids))
 assert all(i>=prefix for i in query_ids)
 pairs=[]
 for a,b in zip(left,right):
  a,b=int(a),int(b);assert 0<=a<len(query_ids)and 0<=b<len(all_ids)
  i,j=all_ids[b],query_ids[a]
  if i<j:pairs.append((i,j))
 assert len(pairs)==len(set(pairs)), 'duplicate same index-pair in actual STRtree result'
 assert all(0<=i<j and j>=prefix for i,j in pairs)
 return sorted(pairs)
