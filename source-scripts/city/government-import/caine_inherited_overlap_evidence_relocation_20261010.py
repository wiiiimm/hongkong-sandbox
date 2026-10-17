"""Exact inherited audit-path relocation, with no terrain-field exemption.

Every one of the original nine ordered child dictionaries must stay identical
except four explicit audit evidencePath strings. Each old/new referenced file
must exist inside the worktree and contain identical bytes with the original
unchanged SHA256. No other metadata or numeric differences are accepted.
"""
import copy
from run import ROOT,read,digest
EXPECTED={4:'support-exact-tin-232907-0',6:'government-native-239367-0',7:'government-native-122298-0',8:'government-native-304714-0'}
PREFIX='docs/astra-city/government-import/government-xl-terrain-recovery-unnamed-268032-nested-original-pair-current-physical-v5-20261010/'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify(old,new):
 assert len(old['patches'])==9 and len(new['patches'])==10
 expected=copy.deepcopy(old['patches']);records=[];refs=[]
 for i,identifier in EXPECTED.items():
  a=old['patches'][i];b=new['patches'][i];assert a['id']==b['id']==identifier
  previous=a['nativeMesh']['sourceOverlap'];current=b['nativeMesh']['sourceOverlap']
  assert current['evidencePath']==PREFIX+'inherited-'+identifier+'-native-overlap.json'
  assert current['evidenceSHA256']==previous['evidenceSHA256']
  p=(ROOT/previous['evidencePath']).resolve();q=(ROOT/current['evidencePath']).resolve()
  assert p.is_relative_to(ROOT) and q.is_relative_to(ROOT) and p.is_file() and q.is_file()
  raw=p.read_bytes();assert raw==q.read_bytes() and digest(raw)==previous['evidenceSHA256']
  expected[i]['nativeMesh']['sourceOverlap']['evidencePath']=current['evidencePath']
  records.append(dict(child=i,id=identifier,originalAudit=ref(p),relocatedAudit=ref(q),identicalAuditBytes=True))
  refs.extend([ref(p),ref(q)])
 assert new['patches'][:9]==expected,'An inherited child changed beyond the four exact audit-path relocations'
 for key in ['w','h','cell','coarseCells','elev','renderedElev','vegetation','hydro']:
  assert new.get(key)==old.get(key)
 assert new['meta']['georef']==old['meta']['georef']
 return dict(contract='caine-exact-four-inherited-audit-path-relocations-v1',preservedOrderedOriginalChildren=9,sourceGeometryChanges=0,allInheritedNumericAndOtherMetadataFieldsExactlyEqual=True,relocations=records,evidenceRefs=refs+[ref(__import__('pathlib').Path(__file__))])
