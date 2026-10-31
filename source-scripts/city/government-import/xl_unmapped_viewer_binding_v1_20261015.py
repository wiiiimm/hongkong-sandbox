"""Bind recovered source candidates through CSUID; retain all geometric differences."""
from pathlib import Path
from shapely.geometry import Polygon, GeometryCollection
from shapely.ops import unary_union
from run import ROOT, read, save, digest
BASE=ROOT/'docs/astra-city/government-import'
OUT=BASE/'government-xl-unmapped-two-primary-evidence-v1-20261015'
QUERY=BASE/'government-xl-unmapped-full-bounds-provider-v1-20261015'
REC=BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015'
TARGETS={'B360171738601063C0':['3601317392P20240826'],'B365201779201063C0':['3652217790P20230217','3654517794T20231129']}
def ref(p): return {'path':str(p.relative_to(ROOT)), 'sha256':digest(p.read_bytes())}
def polygon(rings,provider=False):
 p=GeometryCollection()
 for ring in rings:
  q=Polygon([(x-834500,816500-y)for x,y,*_ in ring] if provider else ring)
  assert q.is_valid
  p=p.symmetric_difference(q)
 assert p.is_valid
 return p

def main():
 refs=[ref(Path(__file__)),ref(ROOT/'3d-viewer/city/data/manifest.json')]
 forms={}
 for tile in ('0_-1','1_-1'):
  p=ROOT/f'3d-viewer/city/data/tiles/{tile}.json';refs.append(ref(p))
  for b in read(p)['buildings']:
   if b.get('buildingCSUID')in sum(TARGETS.values(),[]):
    assert b['buildingCSUID']not in forms; forms[b['buildingCSUID']]=b
 recovered={r['modelId']:r for r in read(REC/'recovery.json')['rows']}
 contexts=read(BASE/'government-xl-unmapped-original-projection-context-v1-20261015/context.json')['rows']
 rows=[]
 for model,ids in TARGETS.items():
  source=recovered[model];refs.append(source['asset']);qp=QUERY/(model+'.json');refs.append(ref(qp));provider={f['attributes']['BuildingCSUID']:f for f in read(qp)['features']}
  ctx=next(r for r in contexts if r['sourceKey']==source['sourceKey']);bindings=[]
  for csuid in ids:
   f=forms[csuid];p=provider[csuid];a=polygon(f['rings']);b=polygon(p['geometry']['rings'],True)
   bindings.append({'csuid':csuid,'viewerUID':f['uid'],'providerObjectId':p['attributes']['OBJECTID'],'viewerForm':f,'symmetricDifferenceM2':a.symmetric_difference(b).area,'intersectionOverUnion':a.intersection(b).area/a.union(b).area,'projectionMeasurement':next(c for c in ctx['candidates']if c['CSUID']==csuid)})
  rows.append({'modelId':model,'sourceKey':source['sourceKey'],'sourceSHA256':source['sourceSHA256'],'bindings':bindings,'identityAccepted':False,'installationApproved':False,'nextAction':'Replay full current identity and placement against these CSUID-bound forms; retain historical subtype change and source excess as explicit review evidence.'})
 for p in OUT.iterdir():
  if p.is_file()and p.name!='viewer-bindings.json':refs.append(ref(p))
 for r in refs:assert ref(ROOT/r['path'])==r
 save(OUT/'viewer-bindings.json',{'rows':rows,'evidenceRefs':refs,'newlyInstalled':0,'sourceGeometryChanges':0,'qualification':'Candidate routing only. Neither approximate footprint agreement nor photos alone grant installation approval.'})
 print([(r['modelId'],[(b['viewerUID'],b['symmetricDifferenceM2'],b['intersectionOverUnion'])for b in r['bindings']])for r in rows])
if __name__=='__main__':main()
