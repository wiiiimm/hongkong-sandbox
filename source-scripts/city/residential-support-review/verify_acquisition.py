"""Run unchanged acquisition verifier against each local support batch."""
import importlib.util,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residential-support-review'
for name,work,out,cap in [('lohas',HERE,DOC,10_000_000),('omitted',HERE/'omitted-support',DOC/'omitted-support',150_000_000)]:
 s=importlib.util.spec_from_file_location('verify_'+name,ROOT/'source-scripts/city/landmark-acquisition/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v);v.a.HERE=work;v.a.DOCS=out;v.a.configure_batch=lambda *_:{'capBytes':cap};sys.argv=[__file__];assert not v.main()
