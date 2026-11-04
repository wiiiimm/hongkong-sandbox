"""Fresh authoritative named Block H/platform context; no identity or support credit."""
import importlib.util,json,subprocess,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
BATCH='government-xl-man-hei-man-fuk-primary-platform-context-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
UIDS=['landsd/75694:0','landsd/266062:0'];CSUIDS=['3639519467T20050430','3644619608P20050726']
def main():
 assert not DOC.exists();claim=reservations.claim('man-hei-primary-'+str(uuid.uuid4()),['building:landsd/75694:0'],batch=BATCH,ttl=1800);assert claim['ok'],claim
 try:
  DOC.mkdir(parents=True);spec=importlib.util.spec_from_file_location('readonly_primary_capture',HERE/'xl-man-fuk-man-oi-primary-relations-20261010.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.DOC=DOC
  primary=m.query(0,'BuildingCSUID IN ('+','.join("'"+s+"'" for s in CSUIDS)+')','exact-current-primary',True);assert {r['attributes']['BuildingCSUID'] for r in primary}==set(CSUIDS) and len(primary)==2
  rel=m.query(1002,'BuildingCSUID IN ('+','.join("'"+s+"'" for s in CSUIDS)+')','exact-current-structure-relations');ids=sorted({r['attributes']['BuildingStructureID'] for r in rel});structures=m.query(1003,'BuildingStructureID IN ('+','.join(map(str,ids))+')','exact-current-structures') if ids else []
  pdf=m.fetch_pdf('ha-man-hei-block-h.pdf','https://www.housingauthority.gov.hk/hdw/content/static/file/b5/residential/plans/chunmancourt_bH.pdf');assert pdf.get('isPDF') and pdf.get('status')==200,pdf
  import fitz
  d=fitz.open(DOC/'ha-man-hei-block-h.pdf');text=[]
  for i,page in enumerate(d):
   text.append({'page':i+1,'text':page.get_text()});page.get_pixmap(matrix=fitz.Matrix(3,3)).save(DOC/('ha-man-hei-block-h.pdf.page-'+str(i+1)+'.png'))
  save(DOC/'ha-man-hei-block-h.pdf.text.json',text)
  save(DOC/'diagnostic.json',{'uids':UIDS,'csuids':CSUIDS,'primary':primary,'relations':rel,'structures':structures,'plan':pdf,'identityAccepted':False,'supportCredit':False,'physicalAccepted':False,'sourceGeometryChanges':0,'qualification':'Fresh current provider Tower/Podium and specifically named Housing Authority Block H plan. Related platform is read-only while parent owns physical work. Same estate/name alone provides no relationship, complete floor filling, legal ownership or load-bearing credit.'});print({'primary':len(primary),'relations':len(rel),'pages':len(d)},flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
