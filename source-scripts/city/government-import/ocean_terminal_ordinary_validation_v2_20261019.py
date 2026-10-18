"""Ordinary private loader and affected-neighbour validation for three original sources."""
from pathlib import Path
import copy,subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ocean-terminal-ordinary-validation-v2-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PAIR=BASE/'government-xl-ocean-terminal-private-ground-v2-20261018';NEAR=BASE/'government-xl-ocean-terminal-current-scope-v1-20261019'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [NEAR]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(PAIR/'selection.json.gz')['rows'];assert len(rows)==1;entries=[];fixes=[]
 for r in rows:
  e=copy.deepcopy(r['candidate']['entry']);raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];path=LOCAL/e['asset'];path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
  if not e.get('sourceTile'):
   with connect() as db:
    db.execute('SET TRANSACTION READ ONLY');sheet,result_sha,native=db.execute('SELECT i.sheet,s.result_sha,s.result FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results s USING(cache_key) WHERE i.cache_key=%s',(r['native']['cacheKey'],)).fetchone()
   assert result_sha==r['native']['resultSha'];matches=[x for x in native['models']if x['modelId']==r['modelId']];assert len(matches)==1 and matches[0]['asset']['sha256']==r['sourceSHA256'];e['sourceTile']=sheet;fixes.append(dict(uid=r['uid'],sourceTile=sheet,cacheKey=r['native']['cacheKey'],resultSHA256=result_sha,sourceSHA256=r['sourceSHA256']))
  entries.append(e)
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=1),area='Private original Ocean Terminal'))
 save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{r['uid']:r['source']for r in rows});save(DOC/'terrain-candidates.json',read(PAIR/'terrain-candidates.json'));save(DOC/'metadata-source-tile.json',dict(fixes=fixes,sourceGeometryChanges=0))
 tool=HERE.parent/'building-batch/validate_candidates.mjs';cmd=['node',str(tool),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
 with(DOC/'validation.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 assert p.returncode in[0,1];save(DOC/'validation-command.json',dict(command=cmd,exitCode=p.returncode));v=read(DOC/'validation.json')
 scope=read(NEAR/'scope.json');assert scope['touchingNativeUids']==[]
 final=module('times_current_neighbour_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms(scope['changedParentExtent']);inputs={str((ROOT/'3d-viewer'/tile).relative_to(ROOT)):digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in forms}
 near=dict(requiredNativeUids=scope['touchingNativeUids'],candidateIds=[r['uid']for r in rows],patches=read(DOC/'terrain-candidates.json'),rows=[dict(building=b,patchIndexes=[0],existingNative=False)for b,_,_ in forms],inputHashes=inputs);save(DOC/'neighbour-inputs.json.gz',near)
 for name in ['check-neighbours.mjs','check-native-neighbours-multi-retained-scoped-v4.mjs']:subprocess.run(['node',str(HERE/name),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True);refs.append(HERE/name)
 n=read(DOC/'neighbour-checks.json');native=read(DOC/'native-neighbour-checks.json');summary=dict(uids=near['candidateIds'],loaderAccepted=v.get('loaderAccepted'),checksPassed=v.get('checksPassed'),exceptions=v.get('exceptions'),ordinaryConcerns=[dict(uid=r['uid'],concerns=r.get('concerns',[]))for r in v['results']],neighbourConcerns=[dict(uid=r['uid'],reasons=r['reasons'])for r in n['rows']if r['reasons']],unresolvedNatives=sorted(set(native['blocked'])-set(native['resolved'])),installationApproved=False);save(DOC/'summary.json',summary);print(summary,flush=True)
 for report in [v,n,native]:
  for p,h in {**report.get('inputHashes',{}),**report.get('hashes',{})}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.append(tool);refs.extend(p for p in LOCAL.rglob('*')if p.is_file());module('pacifica_ordinary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ocean-terminal-ordinary-loader-and-full-neighbours',list(dict.fromkeys(refs)),summary)
if __name__=='__main__':main()
