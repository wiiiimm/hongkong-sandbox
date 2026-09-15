"""Explicit, hash-pinned source corrections to an installed terrain patch."""
import hashlib,json,math
from pathlib import Path

def reviewed_changes(root,entry,old,new):
 review=entry.get('reviewedChanges')
 if not review:return {}
 def read(ref):
  path=(root/ref['path']).resolve();assert path.is_relative_to(root.resolve())
  raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==ref['sha256'],'Terrain correction evidence changed'
  return json.loads(raw)
 decision=read(review)
 assert decision['status']=='approved-for-integration' and decision['verticalScale']==1
 assert decision['replacementSHA256']==entry['sha256'] and decision['supersededSHA256']==entry['replaces']['sha256']
 for path,digest in decision['evidenceHashes'].items():read({'path':path,'sha256':digest})
 evidence=read(decision['changedNodeEvidence']);expected=['oldIndex','replacementIndex','x','z','oldElevation','oldRenderedElevation','newElevation','newRenderedElevation','sourceTIN']
 assert evidence['columns']==expected,'Unrecognised correction evidence columns'
 result={};seen=set();g=new['meta']['georef']
 for row in evidence['rows']:
  i,j,x,z,oe,ore,ne,nre,source=row
  assert type(j) is int and 0<=j<len(new['elev']) and j not in seen;seen.add(j)
  assert all(isinstance(v,(int,float)) and math.isfinite(v) for v in [x,z,ne,nre,source])
  assert abs(x-(g['bE']+(j%new['w'])*g['aE']-834500))<1e-6 and abs(z-(816500-g['bN']-(j//new['w'])*g['aN']))<1e-6
  assert ne==new['elev'][j] and nre==new.get('renderedElev',new['elev'])[j]
  assert abs(ne-source)<1e-5 and abs(nre-source)<1e-5 and source>1.2,'Correction must retain positive surveyed native land'
  if i is not None:
   assert type(i) is int and 0<=i<len(old['elev']) and i not in result
   assert old['elev'][i]==oe and old.get('renderedElev',old['elev'])[i]==ore
   assert oe==0 and ore==-4,'Only explicitly reviewed masked-land correction is supported'
   result[i]=j
 return result
