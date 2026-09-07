"""Merge source-led discovery lists with explicit aliases, without model writes."""
import json,pathlib,re,unicodedata
HERE=pathlib.Path(__file__).resolve().parent
read=lambda p:json.loads((HERE/p).read_text())
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).lower().replace('centre','center'))
def main():
 base=read('curated.json');more=read('additional-guides.json');tall=read('tallest-source.json');items=base['landmarks']+more['landmarks'];byid={r['id']:r for r in items};assert len(byid)==len(items)
 aliases={norm(r['name']):r['id'] for r in items}
 explicit={'ifc':['Two International Finance Centre','One International Finance Centre'],'bank-of-china':['Bank of China Tower'],'hsbc':['HSBC Main Building'],'lippo-centre':['Lippo Centre Tower1','Lippo Centre Tower2','Lippo Centre Tower 1','Lippo Centre Tower 2','Lippo Centre I','Lippo Centre II'],'victoria-towers':['The Victoria Towers Tower 1','The Victoria Towers Tower 2','The Victoria Towers Tower 3','The Victoria Towers I','The Victoria Towers II','The Victoria Towers III','The Victoria Towers1','The Victoria Towers2','The Victoria Towers3','Victoria Towers 1','Victoria Towers 2','Victoria Towers 3'],'harbourside':['The Harbourside'],'hkcec':['Hong Kong Convention and Exhibition Centre'],'icc':['International Commerce Centre'],'cheung-kong-centre':['Cheung Kong Center'],'four-seasons-hotel':['Four Seasons Hotel Hong Kong','Four Seasons Hotel'],'four-seasons-place':['Four Seasons Place'],'hysan-place':['Hysan Place'],'central-plaza':['Central Plaza'],'one-island-east':['One Island East']}
 for ident,names in explicit.items():
  for n in names:aliases[norm(n)]=ident
 matched=0
 for row in tall['records']:
  key=norm(row['name']);ident=aliases.get(key)
  if ident:matched+=1;item=byid[ident]
  else:
   ident='tall-'+re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',row['name']).lower()).strip('-');assert ident not in byid
   item={'id':ident,'name':row['name'],'origin':'wikipedia-tallest-2026-09-07','kind':'building-or-tower-group','inventoryNamePatterns':[row['name'].lower(),row['name'].lower().replace('centre','center')],'sources':[],'status':'queued-identity-and-component-review','modelAcquisition':'not-run','note':'Source table may group several towers. Resolve every source component and verify current status before modelling.'};items.append(item);byid[ident]=item;aliases[key]=ident
  if row['source'] not in item['sources']:item['sources'].append(row['source'])
  item.setdefault('discoveryMeasurements',[]).append(row)
  if row['sourceWarnings']:item.setdefault('sourceWarnings',[]).extend(row['sourceWarnings'])
 for item in items:
  item['sources']=list(dict.fromkeys(item['sources']))
  if item.get('sourceWarnings'):item['sourceWarnings']=sorted(set(item['sourceWarnings']))
 base.update(landmarks=items,sources=base['sources']+more['sources']+[{'url':tall['source'],'role':'180 factual table rows; duplicate/source-state conflicts preserved. Not every35-floor building.'}],featureTargets=more['featureTargets'],summary={'registryEntries':len(items),'curatedOriginalAndCultural':10,'artchitectoursAdditions':14,'additionalGuideEntries':len(more['landmarks']),'tallestTableRows':tall['count'],'tallestUniqueNames':tall['uniqueNames'],'tallestNewEntries':0,'tallestRowsMergedToExistingOrDuplicate':matched,'interiorVenueEntries':sum(i.get('kind')=='interior-venue' for i in items),'separateFeatureTargets':len(more['featureTargets'])})
 base['summary']['tallestNewEntries']=sum(i['origin']=='wikipedia-tallest-2026-09-07' for i in items)
 base['notes']+=tall['notes'];base['excludedSourceTables']=tall['excludedTables'];(HERE/'landmarks.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n');print(json.dumps(base['summary']))
if __name__=='__main__':main()
