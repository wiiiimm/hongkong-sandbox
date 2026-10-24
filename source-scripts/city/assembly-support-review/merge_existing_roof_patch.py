"""Preserve the installed roof correction exactly while extending its western strip."""
import json,hashlib
from pathlib import Path
import terrain_patches as t
ROOT=t.ROOT;HERE=t.HERE;OUT=t.OUT
read=t.read;sha=t.sha
def main():
 proposed=HERE/'terrain-patches/support-native-244779-0.json';installed=ROOT/'3d-viewer/city/data/roof-review-226248-0.json';p=read(proposed);old=read(installed);g=p['meta']['georef'];og=old['meta']['georef'];assert g['aE']==og['aE']==1 and g['aN']==og['aN']==-1
 xoffset=round(og['bE']-g['bE']);zoffset=round(g['bN']-og['bN']);assert xoffset>10 and zoffset==0 and old['h']==p['h'] and xoffset+old['w']==p['w'];original=list(p['renderedElev']);count=0
 for r in range(p['h']):
  edge=old['renderedElev'][r*old['w']]
  for c in range(p['w']):
   i=r*p['w']+c
   if c>=xoffset:
    j=r*old['w']+c-xoffset;p['elev'][i]=old['elev'][j];p['renderedElev'][i]=old['renderedElev'][j];p['vegetation'][i]=old['vegetation'][j];count+=1
   elif xoffset-c<10:
    alpha=(xoffset-c)/10;y=original[i]*alpha+edge*(1-alpha)
    if p['elev'][i]>0:p['elev'][i]=round(y,6);p['renderedElev'][i]=round(y,6)
 p['meta']['replacesExistingManifestPatches']=['city/data/roof-review-226248-0.json'];p['meta']['preservedExistingPatch']={'url':'city/data/roof-review-226248-0.json','sha256':sha(installed),'nodesCopiedExactly':count,'transition':'10m western strip blends to exact installed child boundary; installed rectangle unchanged.'}
 for r in range(old['h']):
  for c in range(old['w']):
   a=r*old['w']+c;b=r*p['w']+c+xoffset;assert p['elev'][b]==old['elev'][a] and p['renderedElev'][b]==old['renderedElev'][a]
 proposed.write_text(json.dumps(p,separators=(',',':'))+'\n');bundle=read(OUT/'terrain-patches.json');report=read(OUT/'report.json');source=next(r for r in report['rows'] if r['uid']=='landsd/244779:0');sampler=t.fine.DemSampler(p,rendered=True);gaps=[r['position'][1]-sampler.ground(r['position'][0],r['position'][2]) for r in source['rim']]
 for b in bundle['bundles']:
  for c in b['patches']:
   if c['path']==str(proposed.relative_to(ROOT)):c['sha256']=sha(proposed);c['replacesExistingManifestPatches']=['city/data/roof-review-226248-0.json'];c['preservedExistingSha256']=sha(installed)
 for check in bundle['checks']:
  if check['patch']==str(proposed.relative_to(ROOT)):
   check['rows']=[{'uid':'landsd/244779:0','samples':len(gaps),'within2m':sum(abs(v)<=2 for v in gaps),'gapRange':[min(gaps),max(gaps)]}];check['eligibleForBrowserValidation']=all(abs(v)<=2 for v in gaps);check['preservedExistingPatch']=p['meta']['preservedExistingPatch']
 (OUT/'terrain-patches.json').write_text(json.dumps(bundle,indent=2)+'\n');print(json.dumps({'copiedExactNodes':count,'rimSamples':len(gaps),'within2m':sum(abs(v)<=2 for v in gaps),'gapRange':[min(gaps),max(gaps)]}))
if __name__=='__main__':main()
