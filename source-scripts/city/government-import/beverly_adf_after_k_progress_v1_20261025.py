"""Save all current Beverly follow-up evidence and exact actionable holds in Neon."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-adf-after-k-progress-v1-20261025'

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];completed=[]
 prefixes=['government-xl-beverly-'+x+'-after-k-'for x in ['ad','f','adf','fe','f-e','a-e','e','255539','255541','256334','256142']]
 for folder in sorted(BASE.iterdir()):
  if folder.name==BATCH or not any(folder.name.startswith(p)for p in prefixes)or not(folder/'result.json').is_file():continue
  r,_=authenticate(folder);refs.append(folder/'result.json');completed.append(dict(batch=folder.name,jobId=r['jobId']))
 def take(batch,name):
  _,pins=authenticate(BASE/batch);refs.append(BASE/batch/'result.json');path=BASE/batch/name;assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 installed='government-xl-beverly-k-finite-original-original-installed-v2-20261025';receipt,_=authenticate(BASE/installed);refs.append(BASE/installed/'result.json');assert receipt['fullXLCurrentCounts']==dict(total=521,installedVerified=379,remaining=142)and receipt['completeCurrentCatalogueModels']==6955
 exact=take('government-xl-after-beverly-k-unfinished-exact-source-inventory-v1-20261025','summary.json');assert exact['unfinished']==142 and exact['unmatchedViewerUIDs']==2
 adf=take('government-xl-beverly-adf-after-k-finite-evidence-v1-20261025','summary.json');fe=take('government-xl-beverly-fe-after-k-finite-evidence-v1-20261025','summary.json');assert adf['verifiedFinitePaths']==452 and fe['verifiedFinitePaths']==448
 roles=take('government-xl-beverly-fe-after-k-pair-roles-v1-20261025','summary.json');assert all(r['contactCount']==34 and r['roles']['transverse-surface-crossing']==15 for r in roles['rows'])
 images=[]
 for uid in ['256334','256142']:
  batch='government-xl-beverly-'+uid+'-after-k-source-views-v1-20261025';_,pins=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
  for name in ['whole-source-plan.png','whole-source-perspectives.png']:
   path=BASE/batch/name;key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==pins[key];refs.append(path);images.append(dict(path=key,sha256=pins[key]))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==exact['currentManifestSHA256'];refs.append(manifest)
 result=dict(uids=['landsd/255539:0','landsd/255541:0','landsd/256334:0','landsd/256142:0'],currentManifestSHA256=digest(manifest.read_bytes()),installedXL=379,unfinishedXL=142,totalFixedXL=521,currentNativeActors=6955,newlyInstalled=0,installationApproved=False,physicalAcceptance=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,humanDecisionRequired=False,state='held-for-compute',completed=completed,wholeOriginalDiagramsActuallyViewedByRoot=images,sourceViewObservation='ROOT opened all4individual F/E plan/perspective exports. Both complete original towers retain continuous bodies,facades,balconies and roofs. These are source-only diagnostic diagrams, not private/live browser acceptance.',
 rawFailuresPreserved=['Canonical BASIC checks stayfalse for A/D/F/E. No-vertical-support and support-above-rim failures are not renamed canonical passes. Separate roof-only finite paths are replayed within original.5m/1mm limits.', 'Raw coarse global-height bound staysfalse forF (and anyother reported mode); exact complete continuous contexts bind to byte-identical original/literal/twoFloat32 geometry. No geometryorheight change.', 'Initial unfiltered finite paths included actualpodiumside contacts and failed the stronger flatroof terminal predicate. New roof-only search retains allrawcontacts and passes unchanged endpoint predicate. No failedpath/limit waived.', 'No-vertical-support rawrecords omit gap ratherthanproviding a numericvalue; V2 accepts absence/null only and rejects invented numericgaps. Elevencontracttests pass.', 'Original mixed-cache A/D/F/E selector rejected beforeoutput. Existing guardunchanged; F-onlysamecache selection plus recoveredE succeeds.', 'D genericidentity remainsfalse: target coverage0.9342413622, maxsourceextent2.230392m. ExactCSUID/ObjectID andcompleteGeoRefcellmatch remain positive; no boundedidentityapprovalyet.', 'F versuscurrentBASIC256142 has69surfacecontacts,7.479824m2projectedoverlap. Recovered exactEoriginal doesnot erase this historicalcheck. Completeoriginal F/E pair has34contacts including15transverse crossings inall4worlds; theseare NOTcollision-clear or sourcecorruption conclusions.'],
 remainingWork=[
  'Priority F/E unit: review15original transverse joints using exactlocus/source-role/primary records and actual sourceviews. Bothidentitychecks pass;19458immutablefaces,emptyinstallednative scope,complete terraincoverage andall448roofpaths are ready. Finish currentnoncandidate neighbour interpretation, retaining allrawcurrentBASICandpair contacts.',
  'Use a separately tested positive finiteV2 admission path for multiple originals/empty nativecontext. Preserve alloldcanonical/publisherguards andtypedP233218 BASIC lifetime. Require completeform leases and candidatepair proof; neverlabelcanonicalfalseastrue. No production optimisation.',
  'Run private desktop/mobile day/night source previews,actuallyopenallindividualexports,then boundedsource/physicalreview. Qualify,commitpushBEFORE guardedinstallation;freshliveexports/full6955oldassets/521/globalBASIC+manifest readback,inventoryrefresh,commitpush. F/E wouldadd2actors butonly1fixedXL(F); E8527faces isL companion,notadditionalXLcredit.',
  'A next: exactidentitypass,allfourfoundations/coveragepass,40roofpaths replay. Preserve fullA/E256136native35contacts/5tinyroof-area pairs(pairareasum0.0029117603m2),A/K255543zero contacts,andcurrententryflags. Requires source/native role andprivate/live guardedacceptance.',
  'D next: exactwholeGeoRefcell andstableIDmatch butfootprintcoveragefailure unresolved. Inspect completeoriginal/primarysurvey shape,uncoveredtarget and0.955m2projectionover70279(current actualsurfacecontacts0); do nottrim/move sourceorinventidentityapproval.196roofpaths andfourworldfoundationspass.',
  'P233218 mustremainBASICandunsuppressed, including existing installedK255543dependency; doNOTimport/replacePwithoutdependent revalidation. Keep all142fixedunfinishedsourcekeys andbothnullUIDkeys. No human/AIgeometry decisionrequired established.'
 ],tracker=dict(issue='HKS-203',installedCommit='bd8169f9b',progressCommentId='8c305ac1-1d34-4cdb-b9f4-3f2538e4ed5f'))
 save(out/'remaining-work.json',result);module('beverly_followup_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-beverly-original-acquisition-and-positive-finite-evidence-actionable-holds',list(dict.fromkeys(refs)),result);print(dict(completed=len(completed),newlyInstalled=0,state=result['state']),flush=True)
if __name__=='__main__':main()
