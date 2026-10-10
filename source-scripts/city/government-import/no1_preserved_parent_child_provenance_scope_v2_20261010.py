"""Metadata-only old acquisition provenance; all actual child numerics stay recursive."""
import copy,hashlib,json,math
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def boundaries(candidate,parent,*,expected_parent_sha,current_parent_sha,evidence_equal):
 assert expected_parent_sha==current_parent_sha and len(expected_parent_sha)==64
 assert len(parent['patches'])==8 and len(candidate['patches'])==9
 for key in ['w','h','cell','coarseCells','elev','renderedElev','vegetation','hydro']:assert candidate.get(key)==parent.get(key)
 assert candidate['meta']['georef']==parent['meta']['georef'];out=[]
 for i,(child,old) in enumerate(zip(candidate['patches'][:8],parent['patches'])):
  a,b=copy.deepcopy(child),copy.deepcopy(old)
  for c in [a,b]:
   overlap=c.get('nativeMesh',{}).get('sourceOverlap',{})
   if 'evidencePath' in overlap:overlap['evidencePath']=None
  assert a==b,'Existing child numerical/state record changed'
  one=child.get('nativeMesh',{}).get('sourceOverlap',{}).get('evidencePath');two=old.get('nativeMesh',{}).get('sourceOverlap',{}).get('evidencePath')
  if one!=two:assert one and two and evidence_equal(one,two),'Relocated prior evidence differs'
  assert child['meta']['source']==old['meta']['source'] and child['meta']['targetUids']==old['meta']['targetUids']
  if child.get('nativeMesh'):
   numeric=child['nativeMesh'];kind='indexed-native-mesh'
  else:
   assert i==1 and child.get('id')=='support-native-93890-0' and child['meta']['targetUids']==['landsd/93890:0'],'Only pinned existing93890 grid child is allowed'
   assert child['w']==121 and child['h']==116 and child['cell']==1
   for key in ['elev','renderedElev','vegetation']:
    assert len(child[key])==child['w']*child['h'] and all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in child[key])
   numeric={k:v for k,v in child.items() if k!='meta'};kind='exact-preserved-existing-93890-grid'
  out.append(dict(pointer='/patches/'+str(i)+'/meta/source',canonicalSHA256=canonical(child['meta']['source']),kind='exact-existing-parent-child-acquisition-provenance-only',parentSHA256=expected_parent_sha,childWholeRecordSHA256=canonical(child),actualChildNumericStateSHA256=canonical(numeric),actualChildNumericKind=kind,currentNativeBeforeAfterProofStillRequired=True))
 return out
