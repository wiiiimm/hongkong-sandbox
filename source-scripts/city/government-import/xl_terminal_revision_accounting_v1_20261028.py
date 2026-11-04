"""Read-only exact-revision XL goal accounting; never infer rejection from holds."""
from pathlib import Path
from run import ROOT,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
BASE=ROOT/'docs/astra-city/government-import'
def main():
 inventory_path=BASE/'government-xl-after-north-pair-unfinished-exact-source-inventory-v1-20261028';inventory,pins=authenticate(inventory_path)
 disposition_path=BASE/'government-xl-southside-current-source-gap-disposition-v1-20261028';disposition,_=authenticate(disposition_path)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==inventory['currentManifestSHA256'];rows=inventory['rows'];assert len(rows)==inventory['unfinished']==125 and len({r['sourceKey']for r in rows})==125
 bykey={r['sourceKey']:r for r in rows};terminal={}
 for decision in disposition['rows']:
  if not decision['inFixedXLScope']:continue
  row=bykey[decision['sourceKey']];assert row['uid']==decision['uid']and row['indexedSourceSHA256']==decision['sourceSHA256']
  assert not row['currentInstalled']and decision['disposition']=='not-installable-as-unchanged-current-source'
  assert decision['automaticRetryWithoutChangedEvidence']is False and decision['furtherUnchangedComputeCanInstall']is False
  assert not decision['originalSourceCorruption']and not decision['requiresAIProcessing']and not decision['requiresHumanDecision']
  terminal[decision['sourceKey']]=decision
 assert len(terminal)==3
 detailed=[]
 for row in rows:
  decision=terminal.get(row['sourceKey']);detailed.append(dict(sourceKey=row['sourceKey'],uid=row['uid'],sourceSHA256=row['indexedSourceSHA256'],goalDisposition='not-installable-exact-current-original-revision'if decision else'outstanding',terminalForExactRevision=bool(decision),decision=decision,rawNativeState=row['originalNativeState'],rawNativeHoldReason=row['originalNativeHoldReason']))
 installed=inventory['installed'];outstanding=len(rows)-len(terminal);assert installed+len(terminal)+outstanding==inventory['fixedXLTotal']==521
 out=BASE/'government-xl-terminal-revision-accounting-v1-20261028';ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 save(out/'summary.json',dict(currentManifest=ref(manifest),fixedInventory=ref(inventory_path/'result.json'),terminalDisposition=ref(disposition_path/'result.json'),fixedXLTotal=521,installed=installed,notInstalled=len(rows),notInstallableExactCurrentRevision=len(terminal),outstanding=outstanding,currentDetailedActors=inventory['currentNativeActors'],unmatchedUIDsPreserved=[r['sourceKey']for r in rows if r['uid']is None],rows=detailed,sourceGeometryChanges=0,publicFilesWritten=0,neonWrites=0,installationApproved=False,publication=False,qualification='Goal accounting only:396installed plus3existing exact-revision terminal dispositions plus122outstanding. Matches both full sourceKey and packed source SHA; no hold, failed script, UID absence or spatial flag becomes a rejection. Existing decision remains in authenticated Neon evidence. A changed provider revision/additional original support or separately authorised repair can trigger fresh review. Does not close the full XL goal or alter inventory/review rows.'))
 print(dict(installed=installed,notInstallableCurrentRevision=len(terminal),outstanding=outstanding,total=521,neonWrites=0))
if __name__=='__main__':main()
