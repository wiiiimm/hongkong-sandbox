"""Re-use the source seam, rendered terrain and public-path arrival audits."""
import pathlib,sys
from run import module,HERE,DOC,CONFIG
sys.path.insert(0,str(HERE.parent/'mui-wo-models'))
if __name__=='__main__':
 module('shared_source_audit',HERE.parent/'mui-wo-models/audit_sources.py').audit_sources(HERE,DOC,[])
 module('shared_baseline_audit',HERE.parent/'mui-wo-models/compare_baseline.py').compare_baseline(HERE/'building-selection.json.gz',CONFIG['baseline'],'terrain.json',DOC)
 sys.path.insert(0,str(HERE.parent))
 repair=module('shared_arrival_repair',HERE.parent/'repair_arrivals.py');repair.DOC=DOC/'arrival-repairs';repair.main()
