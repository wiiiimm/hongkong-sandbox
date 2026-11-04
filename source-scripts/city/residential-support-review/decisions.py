"""Conservative closure of exact source support dependencies; no publication."""
import pathlib,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residential-support-review'
read=lambda p:json.loads(p.read_bytes())
def main():
 report=read(DOC/'combined-support.json');source={p['uid']:p for p in read(HERE/'review-input.json')['parts']};rows={r['uid']:r for r in report['rows']};assert set(source)==set(rows);manifest=read(ROOT/'3d-viewer/city/data/manifest.json');installed={m['uid']for url in manifest['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
 eligible={u for u,p in rows.items()if not p['knownHold'] and p['rimCounts']['noContact']==0 and p['rimCounts']['belowTerrain']==0 and p['counts']['hidden']==0 and p['rimCounts']['samples']>=3}
 def usable(c,accepted):return c['state']=='installed' or c['state']=='candidate' and c['uid']in accepted or c['state']=='surveyed-footprint-fallback' and c['uid']not in accepted|installed
 def supported(uid,accepted):return all(s['gap']<=2 or any(usable(c,accepted)for c in s['contacts'])for s in rows[uid]['rim'])
 approved={u for u in eligible if supported(u,set())}
 for _ in range(len(eligible)*2+1):
  invalid={u for u in approved if not supported(u,approved)}
  if invalid:approved-=invalid;continue
  additions={u for u in eligible-approved if supported(u,approved|{u}) and all(supported(v,approved|{u})for v in approved)}
  if not additions:break
  approved.add(sorted(additions)[0])
 assert all(supported(u,approved)for u in approved);decisions=[]
 for uid,r in rows.items():
  p=source[uid];deps={}
  if uid in approved:
   for point in r['rim']:
    if point['gap']<=2:continue
    possible=[c for c in point['contacts']if usable(c,approved)];assert possible
    c=min(possible,key=lambda c:(c['state']!='installed',c['state']!='surveyed-footprint-fallback',c['distance'],c['uid']));deps[(c['uid'],c['state'])]=c
  decisions.append({'uid':uid,'name':p['name'],'modelId':p['candidate']['modelId'],'buildingCSUID':p['csuid'],'sha256':p['candidate']['sha256'],'placementApproved':uid in approved,'status':'source-supported-awaiting-visual-review'if uid in approved else 'held-source-support-or-terrain','rimCounts':r['rimCounts'],'projectedHiddenSamples':r['counts']['hidden'],'supportDependencies':list(deps.values()),'landmarkMembershipApproved':not bool(p['identityProposalGroups']),'unapprovedMemberships':p['identityProposalGroups'],'architectureAccepted':False,'publicationApproved':False,'requiresLOHASTerrain':uid in {'landsd/54170:0','landsd/100073:0','landsd/149982:0','landsd/150499:0'}})
 result={'issue':'HKS-214','version':1,'inputReportSHA256':hashlib.sha256((DOC/'combined-support.json').read_bytes()).hexdigest(),'approvedCount':len(approved),'heldCount':len(rows)-len(approved),'approvedUids':sorted(approved),'rows':decisions,'installedContextUIDs':sorted(installed),'qualification':'Exact source contact dependency closure only. All accepted model components and retained fallback dependencies must remain together. Finite seam tests do not prove full architectural authenticity or every disconnected mesh. Full-scene and isolated browser review is mandatory before approval; no runtime writes.'};(DOC/'decisions.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'sourceSupported':len(approved),'held':len(rows)-len(approved),'newSupported':sum(u in{p['uid']for p in read(HERE/'supplemental-preflight.json')['parts']if p['candidate']}for u in approved)}))
if __name__=='__main__':main()
