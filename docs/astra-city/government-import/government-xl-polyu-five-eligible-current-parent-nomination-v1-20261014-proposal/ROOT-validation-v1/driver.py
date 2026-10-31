from pathlib import Path
from fractions import Fraction
import sys,json,hashlib,subprocess,gzip
import numpy as np
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city')
HERE=ROOT/'source-scripts/city/government-import'
sys.path.insert(0,str(HERE))
import polyu_five_eligible_current_parent_nomination_v1_20261014 as caller
DOC=caller.PROPOSAL/'ROOT-validation-v1';assert not DOC.exists();DOC.mkdir()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
prep=json.loads((caller.PROPOSAL/'actual-readonly-preparation.json').read_text());assert prep['passed'] and prep['caller']==ref(Path(caller.__file__))
tests=subprocess.run([sys.executable,'-m','unittest','-v',caller.TEST],cwd=HERE,capture_output=True)
(DOC/'tests.log').write_bytes(tests.stdout+tests.stderr);assert tests.returncode==0
pins,receipt,result,masks,base,patch,raw,lineage,parents,resources=caller.load()
checked=0
for face,record in zip(raw,lineage):
 actual=np.asarray([[float(Fraction(v)) for v in point] for point in record['exactProposedPoints']],dtype='<f4').astype('<f8')
 assert actual.tobytes()==face.tobytes();checked+=1
assert checked==3214 and len(resources)==51
assert not caller.DOC.exists() and not caller.LOCAL.exists()
summary={'passed':True,'caller':ref(Path(caller.__file__)),'helper':ref(HERE/'polyu_five_mask_source_plane_partition_v1_20261014.py'),'testLog':ref(DOC/'tests.log'),'testExitCode':tests.returncode,'all3214SavedRationalStringPackedIdentitiesVerified':True,'canonicalResources':len(resources),'eligibleMaskOccurrences':len(masks),'noProductionMaskPartitionCalculation':True,'noDBLeaseOrAcceptance':True}
(DOC/'summary.json').write_text(json.dumps(summary,sort_keys=True)+'\n');print(json.dumps(summary))
