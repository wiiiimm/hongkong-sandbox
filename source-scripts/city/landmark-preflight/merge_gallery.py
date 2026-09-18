"""Merge disjoint gallery workers and account for every planned landmark and part."""
import hashlib,json,pathlib,argparse
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/landmark-preflight'
def read(p):return json.loads(p.read_bytes())
def combine(expected,workers):
 rows={}
 for report in workers:
  for row in report['landmarks']:
   assert row['id']not in rows,'Duplicate worker landmark: '+row['id'];rows[row['id']]=row
 assert set(rows)==set(expected),'Gallery omits or adds a planned landmark'
 return [rows[key]for key in sorted(rows)]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=4);args=ap.parse_args()
 preflight=read(DOC/'report.json');snapshot=preflight['snapshotId'];base=DOC/'gallery'/snapshot;staged={r['uid']for r in preflight['parts']if r['candidate']};groups=[g for g in preflight['landmarks']if set(g['members'])&staged];workers=[read(base/f'report-{i}of{args.workers}.json')for i in range(1,args.workers+1)];assert workers,'No worker reports'
 assert all(r['snapshotId']==snapshot and r.get('finished')for r in workers),'Workers not finished on the same snapshot';rows=combine([g['id']for g in groups],workers);active=set();inactive=[]
 for row in rows:
  seen=set()
  for view in row['views']:
   path=base/view['file'];assert path.exists(),'Missing screenshot';assert hashlib.sha256(path.read_bytes()).hexdigest()==view['sha256'],'Screenshot hash changed';seen.update(view.get('activeUIDs',[]))
  active.update(seen);missing=sorted(set(row.get('stagedUIDs',[]))-seen)
  if missing:inactive.append({'id':row['id'],'uids':missing,'reason':'Not active in either captured view; review stream/camera/LOD evidence before interpreting appearance.'})
 result={'snapshotId':snapshot,'kind':'automated-evidence-unreviewed','started':min(r['started']for r in workers),'finished':max(r['finished']for r in workers),'landmarks':rows,'errors':[e for r in workers for e in r['errors']],'counts':{'plannedAssemblies':len(groups),'attemptedAssemblies':len(rows),'capturedAssemblies':sum(r['result']=='captured-unreviewed'for r in rows),'failedAssemblies':sum(r['result']=='capture-failed'for r in rows),'geographicSpanHolds':sum(r['result']=='held-geographic-span-over-4km'for r in rows),'cameraClearViews':sum(v.get('cameraCheck',{}).get('clear',False)for r in rows for v in r['views']),'cameraUnresolvedViews':sum(not v.get('cameraCheck',{}).get('clear',False)for r in rows for v in r['views']),'reframedViews':sum(v.get('cameraCheck',{}).get('reframed',False)for r in rows for v in r['views']),'images':sum(len(r['views'])for r in rows),'stagedCandidateParts':len(staged),'activeCandidatePartsAcrossGallery':len(active&staged),'assembliesWithInactiveParts':len(inactive)},'inactiveFindings':inactive,'neverActiveCandidateUIDs':sorted(staged-active),'limits':workers[0]['limits']+[f'{args.workers} disjoint browsers ran concurrently; timings are not FPS benchmarks.','Model activity does not prove unoccluded appearance or full component completeness.']}
 (DOC/'gallery-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['counts']))
if __name__=='__main__':main()
