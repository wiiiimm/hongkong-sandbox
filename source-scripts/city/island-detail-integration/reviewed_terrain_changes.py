"""Explicit, hash-pinned source corrections to an installed terrain patch."""
import copy,hashlib,json,math
from pathlib import Path

def bounded_overlap_changes(root,entry,old,new,decision):
 """Recompute the Pui O display seam from the unchanged, pinned Mui Wo grid."""
 assert decision['policy']=='bounded-rendered-terrain-overlap-v1'
 assert decision['aiCalls']==decision['modelGeometryChanges']==0
 mui_ref=decision['muiWoTerrain'];mui_path=(root/mui_ref['path']).resolve()
 assert mui_path.is_relative_to(root.resolve())
 raw=mui_path.read_bytes();assert hashlib.sha256(raw).hexdigest()==mui_ref['sha256']
 mui=json.loads(raw)
 assert entry['replaces']['sha256']==decision['puiOOriginalSHA256']
 assert old['w']==new['w']==379 and old['h']==new['h']
 assert old['elev']==new['elev'] and old['vegetation']==new['vegetation']
 assert old.get('patchExclusions',[])==[] and new['patchExclusions']==[[249,0,260,14]]
 assert old['meta']['georef']==new['meta']['georef'] and old['coarseCells']==new['coarseCells']
 expected=copy.deepcopy(old)
 prior=old['renderedElev'];corrected=list(prior);width=old['w']
 assert mui['meta']['georef']['aE']==old['meta']['georef']['aE']==5
 assert mui['meta']['georef']['aN']==old['meta']['georef']['aN']==-5
 dc=int((mui['meta']['georef']['bE']-old['meta']['georef']['bE'])//5)
 dr=int((mui['meta']['georef']['bN']-old['meta']['georef']['bN'])//5)
 assert (dc,dr)==(182,854)
 def mui_y(c,r):
  values=mui.get('renderedElev',mui['elev'])
  value=values[(r+dr)*mui['w']+c-dc]
  return max(1.2,value) if value>0 else -4
 changed={};numeric_changes=0;max_delta=0
 for r in range(19):
  for c in range(245,265):
   i=r*width+c;before=prior[i] if prior[i] is not None else old['elev'][i]
   if r<=14:desired=mui_y(c,r)
   else:
    anchor=mui_y(c,14)-(prior[14*width+c] if prior[14*width+c] is not None else old['elev'][14*width+c])
    desired=before+anchor*(18-r)/4
   alpha=min(1,max(0,(c-245)/4),max(0,(264-c)/4))
   after=round(before+(desired-before)*alpha,6)
   corrected[i]=after
   if after!=prior[i]:changed[i]=i
   if after!=before:numeric_changes+=1;max_delta=max(max_delta,abs(after-before))
 expected['renderedElev']=corrected
 expected['patchExclusions']=[[249,0,260,14]]
 expected['meta']['renderedTransition']['regionalOverlapCorrection']={
  'policy':'Bounded local overlap: Mui Wo source grid owns duplicate cells c=249..259, r=0..13. Pui O rendered heights join its edge within a 95m x 90m envelope; raw DTM unchanged.',
  'muiWoSHA256':mui_ref['sha256'],'puiOOriginalSHA256':entry['replaces']['sha256'],
  'excludedCells':[[249,0,260,14]],'changedRenderedVertices':numeric_changes,
  'maxRenderedHeightAdjustmentM':max_delta,
 }
 assert numeric_changes==decision['changedRenderedVertices']==324
 assert max_delta==decision['maxRenderedHeightAdjustmentM'] and max_delta<=11
 assert expected==new,'Replacement differs from the bounded, reproducible terrain correction'
 return changed

def reviewed_changes(root,entry,old,new):
 review=entry.get('reviewedChanges')
 if not review:return {}
 def read(ref,parse=True):
  path=(root/ref['path']).resolve();assert path.is_relative_to(root.resolve())
  raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==ref['sha256'],'Terrain correction evidence changed'
  return json.loads(raw) if parse else raw
 decision=read(review)
 assert decision['status']=='approved-for-integration' and decision['verticalScale']==1
 assert decision['replacementSHA256']==entry['sha256'] and decision['supersededSHA256']==entry['replaces']['sha256']
 for path,digest in decision['evidenceHashes'].items():read({'path':path,'sha256':digest},parse=False)
 if decision.get('policy')=='bounded-rendered-terrain-overlap-v1':
  return bounded_overlap_changes(root,entry,old,new,decision)
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
