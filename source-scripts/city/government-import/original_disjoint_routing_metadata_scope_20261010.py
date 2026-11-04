"""Typed archival boundaries for disjoint current terrain routing provenance.

The full routing asset and measured bounds remain mandatory numeric references.
Only acquisition metadata nested in the independently frozen manifest entry is
nonrecursive. This grants no physical, identity or installation acceptance.
"""
import hashlib,json,math

def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def boundaries(preflight,manifest):
 rows=preflight['completeCurrentTerrainRouting'];entries=manifest['terrainPatches'];assert len(rows)==len(entries)
 b=preflight['immutableTerrainProposal']['bounds'];assert len(b)==4 and all(math.isfinite(x) for x in b) and b[0]<b[2] and b[1]<b[3]
 result=[]
 for i,(row,entry) in enumerate(zip(rows,entries)):
  assert row['entry']==entry,'Frozen routing entry differs from authoritative manifest'
  assert row['asset']['path']=='3d-viewer/'+entry['url'] and entry['url'].startswith('city/data/') and '..' not in entry['url'].split('/')
  assert isinstance(row['asset']['sha256'],str) and len(row['asset']['sha256'])==64 and all(c in '0123456789abcdef' for c in row['asset']['sha256'])
  bounds=row['testedBounds'];assert bounds,'No measured complete routing bounds'
  for other in bounds:
   assert len(other)==4 and all(math.isfinite(x) for x in other) and other[0]<=other[2] and other[1]<=other[3]
   assert other[2]<b[0] or other[0]>b[2] or other[3]<b[1] or other[1]>b[3],'Routing terrain touches source proposal'
  if 'source' in entry:
   result.append(dict(pointer=f'/completeCurrentTerrainRouting/{i}/entry/source',canonicalSHA256=canonical(entry['source']),qualification='Archived provider/acquisition provenance copied exactly from frozen manifest entry. Its current terrain asset bytes and complete strictly disjoint routing bounds remain fully replayed.'))
 return result

def subtree(value,pointer):
 assert pointer.startswith('/')
 for key in pointer.split('/')[1:]:value=value[int(key)] if isinstance(value,list) else value[key.replace('~1','/').replace('~0','~')]
 return value

def verify_boundaries(preflight,manifest,declared):
 expected=boundaries(preflight,manifest);assert declared==expected
 for row in declared:assert canonical(subtree(preflight,row['pointer']))==row['canonicalSHA256']
 return {row['pointer'] for row in declared}
