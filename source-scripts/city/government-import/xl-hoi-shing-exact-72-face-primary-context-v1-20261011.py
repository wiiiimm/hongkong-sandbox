"""Primary evidence for an exact buried appendage; no function/support credit."""
import datetime, importlib.util, json, urllib.request, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
BATCH='government-xl-hoi-shing-exact-72-face-primary-context-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PART=DOC.parent/'xl-terrain-recovery-20261011-hoi-shing-72-face-upward-part-context-v1'
UIDS=['landsd/318830:0','landsd/318801:0']
CSUIDS=['3365021126P20180122','3365021124T20180122']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 claim=reservations.claim('hoi-shing-exact-part-primary-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=1800);assert claim['ok'],claim
 try:
  DOC.mkdir(parents=True)
  part=read(PART/'diagnostic.json.gz');assert part['sourceSHA256']=='cb52942f086f38d8d95a346e83538003c90f9aaa772811ac13d3485e1ae27b7f' and len(part['complete72FacePartIds'])==72 and len(part['completeNineRealFailingUpwardFaces'])==9
  oldrefs=[ref(PART/'diagnostic.json.gz'),ref(PART/'result.json')]
  spec=importlib.util.spec_from_file_location('hoi_shing_primary_capture',HERE/'xl-man-fuk-man-oi-primary-relations-20261010.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.DOC=DOC
  where='BuildingCSUID IN ('+','.join("'"+s+"'" for s in CSUIDS)+')'
  primary=m.query(0,where,'exact-current-primary',True);assert len(primary)==2 and {r['attributes']['BuildingCSUID'] for r in primary}==set(CSUIDS)
  relations=m.query(1002,where,'exact-current-structure-relations');ids=sorted({r['attributes']['BuildingStructureID'] for r in relations})
  structures=m.query(1003,'BuildingStructureID IN ('+','.join(map(str,ids))+')','exact-current-structures') if ids else []
  url='https://hos.housingauthority.gov.hk/50A/TreasureHunt/en/hoitat-hoiying.html'
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HongKongSandbox-source-provenance/1.0'}),timeout=60) as response:
   raw=response.read();receipt=dict(url=url,resolvedURL=response.url,status=response.status,responseHeaders=dict(response.headers),retrievedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=digest(raw),bytes=len(raw))
  (DOC/'ha-hoi-tat-hoi-ying-architecture.html').write_bytes(raw);save(DOC/'ha-hoi-tat-hoi-ying-architecture.request.json',receipt)
  plans=[m.fetch_pdf('ha-hoi-tat-barrier-free-202305.pdf','https://www.housingauthority.gov.hk/tc/common/pdf/global-elements/estate-locator/HoiTatEstate-barrier-free-tc.pdf'),m.fetch_pdf('ha-annual-2022-23-environmental-report.pdf','https://www.housingauthority.gov.hk/mini-site/haar2223/common/pdf/8-Chapter-4-Environmental-Report.pdf')]
  import fitz
  for r,name in zip(plans,['ha-hoi-tat-barrier-free-202305.pdf','ha-annual-2022-23-environmental-report.pdf']):
   if not r.get('isPDF'):continue
   d=fitz.open(DOC/name);texts=[]
   for i,page in enumerate(d):
    text=page.get_text();texts.append(dict(page=i+1,text=text))
    if name.startswith('ha-hoi-tat') or 'Hoi Tat' in text or '海達' in text:
     page.get_pixmap(matrix=fitz.Matrix(2,2)).save(DOC/(name+'.page-'+str(i+1)+'.png'))
   save(DOC/(name+'.text.json'),texts)
  for r in oldrefs:assert ref(ROOT/r['path'])==r
  save(DOC/'diagnostic.json',dict(uids=UIDS,csuids=CSUIDS,primary=primary,relations=relations,structures=structures,plans=plans,architecturePage=receipt,exactPartContext=oldrefs,exactPartBounds=part['completePartBounds'],completeNineUpwardFailuresPreserved=True,sourceOnly=True,identityAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,aiGeometryModelling=False,noFunctionInferred=True,qualification='Exact current provider and official HA plan/context acquisition only. The 72-face authored appendage remains unclassified. Generic footbridge/ramp/landscape descriptions do not prove this particular part or excuse its genuine 0.58-0.90m upward-facet burial. No shared-OP support or ownership credit.'))
  print(json.dumps(dict(primary=len(primary),relations=len(relations),structures=len(structures),plans=plans,sourceOnly=True)),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
