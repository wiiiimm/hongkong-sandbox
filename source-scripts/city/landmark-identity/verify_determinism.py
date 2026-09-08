"""Recompute identity evidence in memory without replacing the pinned staging inputs."""
import contextlib,hashlib,io,json
import resolve
original=resolve.read(resolve.HERE/'report.json');overlay=resolve.read(resolve.HERE/'proposed-overlay.json');outputs={}
resolve.write=lambda path,value:outputs.setdefault(path,value)
with contextlib.redirect_stdout(io.StringIO()):resolve.main()
repeat=outputs[resolve.HERE/'report.json'];new_overlay=outputs[resolve.HERE/'proposed-overlay.json']
for report in [original,repeat]:report.pop('seconds',None)
assert original==repeat and overlay==new_overlay
encoded=json.dumps(new_overlay,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
assert encoded.encode()==(resolve.HERE/'proposed-overlay.json').read_bytes()
result=dict(passed=True,identicalReportExcludingRuntime=True,byteIdenticalOverlay=True,overlaySHA256=hashlib.sha256(encoded.encode()).hexdigest(),method='Recompute in memory; pinned report/catalogue untouched')
(resolve.HERE/'determinism.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
