"""Unexecuted full-scope actual BASIC extent counterexamples."""
import copy,unittest,struct,base64,hashlib
import southside_actual_basic_extent_gate_v2_20261012 as h
def geometry(row,lo=100.0):
 values=[lo,2,lo,lo+1,2,lo,lo,3,lo+1];row.update(modelMatrixUniformFloat32=h.IDENTITY[:],completeStreamBytesBase64={},completeIndexBytesBase64=base64.b64encode(struct.pack('<III',0,1,2)).decode());row['completeIndexSHA256']=hashlib.sha256(struct.pack('<III',0,1,2)).hexdigest()
 fields=['positionAttributeSHA256','actualLiteralSHA256','explicitLeftAssociatedF32SHA256','explicitBalancedF32SHA256']
 for mode,key in zip(h.MODES,fields):
  raw=struct.pack('<'+('f'if mode==h.MODES[0]else'd')*len(values),*values);row['completeStreamBytesBase64'][mode]=base64.b64encode(raw).decode();row[key]=hashlib.sha256(raw).hexdigest();row['boundsByArithmetic'][mode]=[[lo,2,lo],[lo+1,3,lo+1]]
 return row
def fixture():
 forms={f'landsd/{i+1}:0':dict(uid=f'landsd/{i+1}:0',base=2)for i in range(1238)};rows=[]
 for uid,form in forms.items():
  rows.append(geometry(dict(uid=uid,currentForm=form,classification='actual-production-BASIC',wholeUnusedPositionVerticesIncluded=True,identityWorldMatrix=h.IDENTITY[:],completePositionVertices=3,completeIndexedFaces=1,positionAttributeSHA256='a'*64,completeIndexSHA256='a'*64,actualLiteralSHA256='a'*64,explicitLeftAssociatedF32SHA256='a'*64,explicitBalancedF32SHA256='a'*64,boundsByArithmetic={m:[[100,2,100],[101,3,101]]for m in h.MODES})))
 proof=dict(schema='southside-complete-actual-basic-extents-v1',inputSHA256='b'*64,startAndEndInputsVerified=True,providerOriginalGovernmentMeshClaim=False,modelGeometryChanges=0,terrainGeometryChanges=0,domainBounds=[[0,0,0],[10,0,10]],completeScannedForms=1238,rows=rows)
 return proof,forms,dict(excluded=[],nominated=[]),proof['domainBounds'],'b'*64
class Tests(unittest.TestCase):
 def test_01_full_scope_strict_disjoint(self):self.assertEqual(len(h.validate(*fixture())['completeExclusionRecords']),1238)
 def test_02_touch_any_mode_remains(self):
  x=fixture();geometry(x[0]['rows'][0],10.0);self.assertEqual(h.validate(*x)['affectedUIDs'],['landsd/1:0'])
 def test_03_next_float32_gap_is_not_touch(self):
  x=fixture();geometry(x[0]['rows'][0],10.00000095367431640625)
  self.assertFalse(h.validate(*x)['affectedUIDs'])
 def test_04_empty_geometry_retained(self):
  x=fixture();x[0]['rows'][0].update(completePositionVertices=0,completeIndexedFaces=0,boundsByArithmetic=None);self.assertEqual(h.validate(*x)['affectedUIDs'],['landsd/1:0'])
 def test_05_scope_or_pose_tampering_rejected(self):
  for defect in ['omission','duplicate','form','matrix','unused','missingmode','inputsha','positionbytes','uniformmatrix']:
   with self.subTest(defect=defect):
    x=fixture();p=x[0];r=p['rows'][0]
    if defect=='omission':p['rows'].pop()
    elif defect=='duplicate':p['rows'][-1]=copy.deepcopy(r)
    elif defect=='form':r['currentForm']={**r['currentForm'],'base':3}
    elif defect=='matrix':r['identityWorldMatrix'][12]=1
    elif defect=='unused':r['wholeUnusedPositionVerticesIncluded']=False
    elif defect=='missingmode':r['boundsByArithmetic'].pop(h.MODES[0])
    elif defect=='inputsha':p['inputSHA256']='c'*64
    elif defect=='positionbytes':r['completeStreamBytesBase64'][h.MODES[0]]=base64.b64encode(struct.pack('<fff',0,0,0)).decode()
    else:r['modelMatrixUniformFloat32'][12]=1
    self.assertRaises(AssertionError,h.validate,*x)
 def test_06_native_only_exact_bound_scope(self):
  x=fixture();r=x[0]['rows'][0];r['classification']='installed-native-already-exactly-bound';self.assertRaises(AssertionError,h.validate,*x);x[2]['excluded']=[dict(uid=r['uid'])];self.assertEqual(len(h.validate(*x)['completeExclusionRecords']),1238)
 def test_07_affected_and_original46_keys_preserved(self):
  x=fixture();geometry(x[0]['rows'][0],10.0);a=h.validate(*x);original=[h.form_key(u)for u in x[1]]+['terrain-parent:p'];protected=original[10:56];r=h.resources(original,x[1],protected,a);self.assertEqual(len(r),48);self.assertTrue(set(protected)<=set(r));self.assertIn('building:landsd/1:0',r)
 def test_08_guard_not_enlarged(self):
  x=fixture();a=dict(affectedUIDs=list(x[1]));self.assertRaises(AssertionError,h.resources,[h.form_key(u)for u in x[1]],x[1],[],a)
if __name__=='__main__':unittest.main(verbosity=2)
