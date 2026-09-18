"""HKS-207: source-specific acceptance around the shared atomic publisher."""
import argparse, hashlib, importlib.util, json, pathlib, shutil, sys
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]; DOC=ROOT/'docs/astra-city/cultural-landmarks'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
CONTEXT={
 'landsd/209787:0':'Studio foundations mostly align: median clearance0.078m. Three low edge points near x1104,z-777 span a depression also in native TIN. Retain geometry and local terrain; small edge gap is a recorded source limitation.',
 'landsd/77406:0':'Raised restaurant supported by actual podium triangles:718/860 interior rays,677within1m. Do not lower source geometry to bare terrain.',
 'landsd/72491:0':'Exact GeoRefNo and footprint overlap; irregular podium centroid29.506m exception reviewed explicitly. Only53/4152 unique vertices exceed0.5m local terrain burial. Native podium/substructures retained.',
 'landsd/123119:0':'Gallery native substructure below ground:3/2507 vertices exceed0.5m burial; full building is visible. Preserve source geometry.',
 'landsd/252061:0':'Native dome roof26.488m HKPD retained despite footprint survey top13m. Suppress invented procedural windows on opaque dome; source materials retained.',
 'landsd/252854:0':'Native west-wing roof21.067m HKPD retained despite footprint survey top13m. Survey metadata retained separately.',
 'landsd/211702:0':'Auditoria Building is the main Cultural Centre roof. Suppress invented procedural windows on opaque auditorium shell; original source materials retained.'
}
def prepare():
 source=HERE/'compact';out=HERE/'approved';out.mkdir(exist_ok=True)
 cat=read(source/'catalogue.json');v=read(source/'validation.json');rows={r['uid']:r for r in v['results']};guard={}
 for m in cat['models']:
  r=rows[m['uid']];assert r['outcome']=='runtime-accepted-placement-unreviewed'
  if r['concerns']:assert m['uid'] in CONTEXT,m['uid']
  assert sha(source/m['asset'])==m['sha256'];dest=out/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/m['asset'],dest)
  m.update(priority='landmark',placementReviewed=True,placementScreening='cultural-landmark-source-context-v1',contextReview=CONTEXT.get(m['uid'],'Exact source identity, native geometry and browser placement reviewed.'))
  if m['uid'] in ('landsd/211702:0','landsd/252061:0'):m['proceduralWindows']=False
 assert len(cat['models'])==10
 cat.update(kind='official-model-catalogue');write(out/'catalogue.json',cat);write(out/'catalogue-index.json',{'models':10,'catalogues':['catalogue.json']})
 plan={'areas':[{'area':'Space Museum and Cultural Centre','catalogue':str((out/'catalogue.json').relative_to(ROOT)),'destination':'city/data/official-models/cultural-landmarks/catalogue.json'}]};write(HERE/'plan.json',plan)
 for p,h in v['hashes'].items():
  if p.startswith('3d-viewer/'):guard[p]=sha(ROOT/p)
 for name in ['report.json','canopy-audit.json','support-context.json','studio-terrain-exception.json','approved/catalogue.json','plan.json','compact/validation.json']:
  p=HERE/name;guard[str(p.relative_to(ROOT))]=sha(p)
 write(HERE/'guard.json',guard)
 write(DOC/'screening.json',{'models':10,'context':CONTEXT,'heldCanopies':6,'terrainAltered':False,'verticalScale':1,'proceduralWindowsDisabled':['landsd/211702:0','landsd/252061:0']})
 print('Prepared10 reviewed models; unchanged native heights and terrain.')
def publish(apply):
 for p,h in read(HERE/'guard.json').items():assert sha(ROOT/p)==h,'Reviewed input changed: '+p
 spec=importlib.util.spec_from_file_location('publisher',HERE.parent/'island-detail-integration/publish.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ROOT=ROOT;m.DOC=DOC
 sys.argv=['publish.py',str((HERE/'plan.json').relative_to(ROOT))]+(['--apply'] if apply else []);m.main()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('step',choices=['prepare','publish']);p.add_argument('--apply',action='store_true');a=p.parse_args();prepare() if a.step=='prepare' else publish(a.apply)
