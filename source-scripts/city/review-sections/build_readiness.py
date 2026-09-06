"""Publish conservative section-level evidence, independently of import totals."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
GATES=['ground','buildings','routes','exploration','presentation','provenance']
def build():
 checklist=(ROOT/'docs/astra-city/SECTION-CHECKLIST.md').read_text()
 ids=re.findall(r'^- \[[ xX]\] \*\*(\d{2}\.\d+)\*\*',checklist,re.M)
 assert len(ids)==len(set(ids))==132
 active={**{id:['HKS-193'] for id in ['01.1','01.2','01.3','01.4','02.1','02.2']},'10.6':['HKS-192','HKS-167'],'10.7':['HKS-171'],'10.10':['HKS-170'],**{id:['HKS-191'] for id in ['11.3','11.5','12.6']}}
 parent={**{f'{i:02}':'HKS-124' for i in range(1,5)},**{f'{i:02}':'HKS-125' for i in range(5,10)},'10':'HKS-122','11':'HKS-126','12':'HKS-126','13':'HKS-127','14':'HKS-127','15':'HKS-127','16':'HKS-126','17':'HKS-126','18':'HKS-128'}
 overrides={**{f'10.{i}':'HKS-123' for i in range(12,17)},'14.8':'HKS-123','11.6':'HKS-122','11.7':'HKS-122'}
 sections=[]
 for id in ids:
  row={'id':id,'phase':'active' if id in active else 'base','issues':active.get(id,[overrides.get(id,parent[id.split('.')[0]])]),'blockers':[],'note':'Base mapping and local arrival checks are available. Detailed review across this whole section is pending.','checks':{k:{'state':'partial' if k in ['buildings','routes','exploration','provenance'] else 'pending','scope':'local','evidence':[],'note':'Imported coverage and saved arrival checks do not verify this whole section.'} for k in GATES}}
  if id=='10.10':
   row['note']='Tai O village channels, five source bridge models and a 607 m public walk are verified. North-west Lantau villages and individual house stilts/private decks still need review.'
   row['blockers']=['Wider north-west Lantau review remains outstanding.']
   for k in GATES:row['checks'][k]={'state':'partial','scope':'local','evidence':[{'commit':'5494ad6','path':'docs/astra-city/tai-o-completion/README.md'}],'note':'Verified Tai O village slice; the wider numbered section is not fully reviewed.'}
  elif id=='10.6':
   row['note']='Mui Wo has 1,327 detailed government models, finer terrain, ten source infrastructure meshes and a verified 4.137 km public walk. Thirteen partial terrain conflicts and wider local detail remain open.'
   for k in GATES:row['checks'][k]={'state':'partial','scope':'local','evidence':[{'commit':'9a33045','path':'docs/astra-city/mui-wo-completion/README.md'}],'note':'Verified Mui Wo village/route slice; this is not whole-section acceptance.'}
  elif id=='10.7':
   row['note']='Pui O now has 681 progressive original models and a source 5 m terrain patch. A 555 m beach route is verified in both directions. Desktop/mobile, night, picking, flight and Retry checks pass. Wetland/channel, village connections and wider Chi Ma Wan review remain open.'
   for k in GATES:row['checks'][k]={'state':'partial','scope':'local','evidence':[{'commit':'7281071','path':'docs/astra-city/pui-o-completion/README.md'}],'note':'Verified Pui O model/terrain and beach-route slice, not whole-section acceptance.'}
  elif id in ['11.3','11.5','12.6']:
   row['note']='Tsing Ma and Ting Kau original bridge models, corrected source foundation terrain, source/cable picking and under-span flight pass browser review. Cable detail remains illustrative; wider coastal and bridge-approach work remains open.'
   row['blockers']=['Wider coastlines, settlements and bridge approaches still require review.']
  elif id in active:row['note']='37 Central–Wan Chai–Sheung Wan source models are integrated with progressive mobile budgets. Model picking/night/collision browser checks pass; continuous public routes, stairs and wider architectural detail remain open.'
  sections.append(row)
 data={'schemaVersion':1,'updatedAt':'2026-09-07','basis':'Section-level review evidence; live committed work only. A completed local route or an import alone does not complete a section.','policy':{'ready':'All six gates verified across the whole section, with evidence and no open blockers.','close':'At least four gates verified across the whole section, including ground and buildings, with evidence and no open blockers.'},'sections':sections}
 (ROOT/'3d-viewer/city/data/section-readiness.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
 return data
if __name__=='__main__':print('Published',len(build()['sections']),'section review records')
