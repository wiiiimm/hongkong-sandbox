"""Publish conservative section-level evidence, independently of import totals."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
GATES=['ground','buildings','routes','exploration','presentation','provenance']
def build():
 checklist=(ROOT/'docs/astra-city/SECTION-CHECKLIST.md').read_text()
 ids=re.findall(r'^- \[[ xX]\] \*\*(\d{2}\.\d+)\*\*',checklist,re.M)
 assert len(ids)==len(set(ids))==132
 active={'01.1':['HKS-193'],'01.2':['HKS-193'],'01.3':['HKS-193'],'10.6':['HKS-192','HKS-167'],'10.10':['HKS-170'],'11.5':['HKS-191']}
 parent={**{f'{i:02}':'HKS-124' for i in range(1,5)},**{f'{i:02}':'HKS-125' for i in range(5,10)},'10':'HKS-122','11':'HKS-126','12':'HKS-126','13':'HKS-127','14':'HKS-127','15':'HKS-127','16':'HKS-126','17':'HKS-126','18':'HKS-128'}
 overrides={**{f'10.{i}':'HKS-123' for i in range(12,17)},'14.8':'HKS-123','11.6':'HKS-122','11.7':'HKS-122'}
 sections=[]
 for id in ids:
  row={'id':id,'phase':'active' if id in active else 'base','issues':active.get(id,[overrides.get(id,parent[id.split('.')[0]])]),'blockers':[],'note':'Base mapping and local arrival checks are available. Detailed review across this whole section is pending.','checks':{k:{'state':'partial' if k in ['buildings','routes','exploration','provenance'] else 'pending','scope':'local','evidence':[],'note':'Imported coverage and saved arrival checks do not verify this whole section.'} for k in GATES}}
  if id=='10.10':
   row['note']='Tai O village channels, five source bridge models and a 607 m public walk are verified. North-west Lantau villages and individual house stilts/private decks still need review.'
   row['blockers']=['Wider north-west Lantau review remains outstanding.']
   for k in GATES:row['checks'][k]={'state':'partial','scope':'local','evidence':[{'commit':'5494ad6','path':'docs/astra-city/tai-o-completion/README.md'}],'note':'Verified Tai O village slice; the wider numbered section is not fully reviewed.'}
  elif id=='10.6':row['note']='Mui Wo has 1,327 detailed government models. Terrain, estuaries and connected village routes are under review; staged fixes await live browser acceptance.'
  elif id=='11.5':row['note']='Tsing Ma source bridge models and terrain corrections are staged. Live integration, Ma Wan and the wider bridge approaches still need review.'
  elif id.startswith('01.') and id in active:row['note']='Central source models, terrain and pedestrian connections are under review. Detailed model imports are being prepared for mobile performance.'
  sections.append(row)
 data={'schemaVersion':1,'updatedAt':'2026-09-07','basis':'Section-level review evidence; live committed work only. A completed local route or an import alone does not complete a section.','policy':{'ready':'All six gates verified across the whole section, with evidence and no open blockers.','close':'At least four gates verified across the whole section, including ground and buildings, with evidence and no open blockers.'},'sections':sections}
 (ROOT/'3d-viewer/city/data/section-readiness.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
 return data
if __name__=='__main__':print('Published',len(build()['sections']),'section review records')
