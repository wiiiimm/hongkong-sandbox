"""Stage approved placement subset for browser review and root-only publication."""
import json,hashlib,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;OUT=ROOT/'docs/astra-city/assembly-support-review'
def main():
 suffix='-terrain' if '--terrain' in sys.argv else ''
 d=json.loads((OUT/('decisions'+('-terrain-variant' if suffix else '')+'.json')).read_text());uidset=set(d['approvedUids']);decisions={r['uid']:r for r in d['rows']};report=json.loads((ROOT/'docs/astra-city/landmark-preflight/report.json').read_text());pin=ROOT/'source-scripts/city/landmark-preflight/snapshots'/report['snapshotId'];c=json.loads((pin/'catalogue.json').read_text());c['models']=[m for m in c['models'] if m['uid'] in uidset];assert len(c['models'])==len(uidset)
 folder=HERE/('approved'+suffix);folder.mkdir(exist_ok=True)
 for m in c['models']:
  source=pin/'assets'/m['asset'];assert hashlib.sha256(source.read_bytes()).hexdigest()==m['sha256'];shutil.copyfile(source,folder/m['asset']);m['placementReviewed']=True;m['placementReview']='Exact UID/CSUID and native source geometry verified; actual low-rim source/fallback roof contact with explicit support dependencies.';m['supportDependencies']=decisions[m['uid']]['supportDependencies'];m['landmarkMembershipApproved']=decisions[m['uid']]['landmarkMembershipApproved'];m['wholeLandmarkAccepted']=False
 c['counts']['packedModels']=len(c['models']);(folder/'catalogue.json').write_text(json.dumps(c,indent=2)+'\n');(folder/'catalogue-index.json').write_text(json.dumps({'models':len(c['models']),'catalogues':['catalogue.json']})+'\n')
 plan={'areas':[{'area':'source-component-support-review','catalogue':str((folder/'catalogue.json').relative_to(ROOT)),'destination':'city/data/official-models/support-review-20260909'+suffix+'/catalogue.json'}]};(HERE/('plan'+suffix+'.json')).write_text(json.dumps(plan,indent=2)+'\n');(HERE/('selection'+suffix+'.json')).write_text(json.dumps({'snapshot':report['snapshotId'],'parts':[{'uid':p['uid'],'name':p['name'],'landmarks':p['landmarkIds']} for p in report['parts'] if p['uid'] in uidset]},indent=2)+'\n')
 print(json.dumps({'staged':len(c['models']),'sourceBytes':sum(m['bytes'] for m in c['models']),'published':False}))
if __name__=='__main__':main()
