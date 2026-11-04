"""Exact stable pairwise parity audit; existing frozen identity data is untouched."""
import importlib.util,json,warnings
import shapely
from run import ROOT,HERE,read,save,digest
from science_attached_open_canopy_identity_20261009 import DOC as PRIMARY,UID,RELATED
BATCH='government-xl-science-current-ring-union-audit-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;INPUT=ROOT/'docs/astra-city/government-import/government-xl-science-attached-open-canopy-current-identity-20261009'
def compare(rings,label):
 polygons=[shapely.Polygon(r) for r in rings];stable=shapely.GeometryCollection()
 for p in polygons:stable=stable.symmetric_difference(p)
 with warnings.catch_warnings():
  warnings.simplefilter('ignore',DeprecationWarning);legacy=shapely.symmetric_difference_all(polygons)
 return {'label':label,'rings':len(rings),'stablePairwiseValid':stable.is_valid,'legacyEqualsStablePairwise':legacy.equals(stable),'symmetricDifferenceAreaM2':legacy.symmetric_difference(stable).area,'legacyAreaM2':legacy.area,'stableAreaM2':stable.area,'completeRingSHA256':digest(json.dumps(rings,separators=(',',':')).encode())}
def main():
 assert not DOC.exists();rows=[];inputs=[]
 p=INPUT/'all-current-forms.json.gz';inputs.append(p)
 for form in read(p)['forms']:rows.append(compare(form['rings'],'current:'+form['uid']))
 for uid in [UID,RELATED]:
  p=PRIMARY/(uid.split('/')[1].replace(':','-')+'-building.json');inputs.append(p);rings=[[(x-834500,816500-y) for x,y in r] for r in read(p)['features'][0]['geometry']['rings']];rows.append(compare(rings,'primary:'+uid))
 # A meaningful future guard illustrates the problematic >2 parity case without changing any geometry.
 synthetic=[[(0,0),(4,0),(4,4),(0,4),(0,0)],[(1,1),(3,1),(3,3),(1,3),(1,1)],[(1.5,1.5),(2.5,1.5),(2.5,2.5),(1.5,2.5),(1.5,1.5)]];synthetic_result=compare(synthetic,'synthetic-three-nested-parity-rings')
 save(DOC/'exact-ring-equivalence.json',{'rows':rows,'allActualEquivalent':all(r['legacyEqualsStablePairwise'] and r['symmetricDifferenceAreaM2']==0 and r['stablePairwiseValid'] for r in rows),'syntheticDiagnosticOnly':synthetic_result,'identityAccepted':False,'sourceGeometryChanges':0,'qualified':'Every complete exact current/primary ring set checked; frozen v1 is unchanged. The stable fold is only a diagnostic here; synthetic rings never contribute identity or spatial credit.'})
 spec=importlib.util.spec_from_file_location('science_ring_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.freeze(BATCH,'exact-current-primary-ring-parity-equivalence-v1',[HERE/'xl-science-current-ring-union-audit-20261009.py',HERE/'science_attached_open_canopy_identity_20261009.py',*inputs],{'uids':[UID,RELATED],'identityAccepted':False,'allActualRingSetsEquivalent':all(r['legacyEqualsStablePairwise'] and r['symmetricDifferenceAreaM2']==0 and r['stablePairwiseValid'] for r in rows),'actualRingSets':len(rows),'multiRingCurrentForms':sum(r['rings']>1 for r in rows if r['label'].startswith('current:')),'nextStep':'Retain frozen v1 replay only for these exact checked current/primary ring sets; use stable pairwise fold in a separately bound revision for any new ring inputs.'})
 print(json.dumps({'actualRingSets':len(rows),'allActualEquivalent':all(r['legacyEqualsStablePairwise'] for r in rows),'synthetic':synthetic_result}),flush=True)
if __name__=='__main__':main()
