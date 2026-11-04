"""Create explicit source-component placement decisions; preserve architectural/membership gates."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/astra-city/assembly-support-review'
read=lambda p:json.loads(p.read_bytes())
def main():
 report_path=ROOT/sys.argv[sys.argv.index('--report')+1] if '--report' in sys.argv else OUT/'report.json'
 report=read(report_path);preflight=read(ROOT/'docs/astra-city/landmark-preflight/report.json');source={p['uid']:p for p in preflight['parts']};rows={p['uid']:p for p in report['rows']};eligible={u for u,p in rows.items() if not p.get('knownHold') and not p['rimCounts']['noContact'] and not p['rimCounts']['belowTerrain'] and not p['counts']['hidden'] and p['rimCounts']['samples']>=3}
 external_file=ROOT/'source-scripts/city/grounded-model-review/selection.json'
 external={p['uid'] for p in read(external_file)['parts']}|{'landsd/'+str(u)+':0' for u in [168596,205817,279530,310908,283788,186982,226248]}
 if '--base-approved' in sys.argv:external.update(read(ROOT/sys.argv[sys.argv.index('--base-approved')+1])['approvedUids'])
 def usable(c,approved):
  approved=approved|external
  return c['state']=='installed' or c['state']=='surveyed-footprint-fallback' and c['uid'] not in approved or c['state']=='candidate' and c['uid'] in approved
 def supported(p,approved):return all(s['gap']<=2 or any(usable(c,approved) for c in s['contacts']) for s in p['rim'])
 # A monotonic addition can invalidate a previously used fallback; verify the whole set each round.
 approved={u for u in eligible if supported(rows[u],set())}
 for _ in range(len(eligible)+1):
  bad={u for u in approved if not supported(rows[u],approved)}
  if bad:approved-=bad;continue
  additions={u for u in eligible-approved if supported(rows[u],approved|{u}) and all(supported(rows[v],approved|{u}) for v in approved)}
  if not additions:break
  # Add one stable UID to avoid simultaneous replacements invalidating fallback dependencies.
  approved.add(sorted(additions)[0])
 assert all(supported(rows[u],approved) for u in approved)
 decisions=[]
 for uid,p in rows.items():
  sp=source[uid];contacts=[]
  if uid in approved:
   for s in p['rim']:
    if s['gap']<=2:continue
    opts=[c for c in s['contacts'] if usable(c,approved)];best=min(opts,key=lambda c:(c['state']!='installed',c['state']!='surveyed-footprint-fallback',c['distance'],c['uid']));contacts.append(best)
  deps={ (c['uid'],c['state']):c for c in contacts}
  decision={'uid':uid,'modelId':sp['candidate']['modelId'],'buildingCSUID':sp['csuid'],'sha256':sp['candidate']['sha256'],'native1x':True,'sourceIdentityVerifiedByRuntimeLoader':True,'placementApproved':uid in approved,'status':'approved-source-component-placement' if uid in approved else 'held-source-component-placement','architectureAccepted':False,'landmarkMembershipApproved':not bool(sp['identityProposalGroups']),'unapprovedMemberships':sp['identityProposalGroups'],'knownHold':sp['knownHold'],'rimCounts':p['rimCounts'],'supportDependencies':list(deps.values()),'conditions':['Run combined browser/loader/collision validation before publication.','Keep exact surveyed fallback support UIDs in fallback form unless their replacement surfaces are independently verified.','Install candidate support dependencies together.','This decision accepts component source identity and observed lower-rim placement, not whole-landmark architectural completeness.'] if uid in approved else ['Resolve partial/absent lower-rim contact, native terrain discrepancy, source hold or dependency before integrating.'],'publicationApproved':False}
  decisions.append(decision)
 result={'issue':'HKS-214','reportSha256':hashlib.sha256(report_path.read_bytes()).hexdigest(),'reviewer':'Astra support review agent','combinedAdditionalUids':sorted(external),'combinedAdditionalSelectionSha256':hashlib.sha256(external_file.read_bytes()).hexdigest(),'approvedCount':len(approved),'heldCount':len(rows)-len(approved),'approvedUids':sorted(approved),'rows':decisions,'method':'Exact native source loader identity and hash checks; every audited near-minimum native vertex has terrain or actual triangle contact. Conservative stable support dependency closure; no same-CSUID/self support and no estimated fallback heights.','limits':['No model or terrain mutation. Root must run the combined publication/browser guards.','A finite low-rim test is not civil engineering or exhaustive disconnected-mesh stability proof.','Representative browser evidence does not imply every landmark has full architectural acceptance.']}
 output=ROOT/sys.argv[sys.argv.index('--output')+1] if '--output' in sys.argv else OUT/'decisions.json'
 output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'approved':len(approved),'held':len(rows)-len(approved),'uids':sorted(approved)}))
if __name__=='__main__':main()
