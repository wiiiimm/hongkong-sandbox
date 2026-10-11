"""Freeze tested source-only interpretation, not current acceptance/publication."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from one_peking_installed_hullett_finite_silhouette_identity_20261010 import verify,OWN,FOREIGN,OWN_SHA
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-one-peking-installed-hullett-finite-silhouette-proposal-v1-20261010';DOC=BASE/BATCH
CONTEXT=BASE/'government-xl-one-peking-hullett-complete-original-boundary-context-v1-20261010';PRIMARY=BASE/'government-xl-one-peking-hullett-three-exact-original-primary-context-v2-20261010';VISUAL=BASE/'government-xl-one-peking-hullett-original-primary-and-complete-visuals-v1-20261010'
def main():
 assert not DOC.exists();context=read(CONTEXT/'diagnostic.json.gz');rows={r['uid']:r for r in context['sources']};primary=read(PRIMARY/'diagnostic.json.gz')
 own=ROOT/rows[OWN]['source']['path'];foreign=ROOT/rows[FOREIGN]['source']['path']
 proof=verify(decode_original_world_triangles(own.read_bytes()),decode_original_world_triangles(foreign.read_bytes()),[x['building'] for x in context['completeCurrentForms']],[r['freshPrimary'] for r in primary['rows']],[rows[FOREIGN]['entry']],OWN_SHA)
 save(DOC/'diagnostic.json.gz',dict(proof,historicalCurrentFormsManifestSHA256=context['capturedManifestSHA256'],currentManifestAcceptanceClaimed=False))
 refs=[Path(__file__),HERE/'one_peking_installed_hullett_finite_silhouette_identity_20261010.py',HERE/'test_one_peking_installed_hullett_finite_silhouette_identity_20261010.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',own,foreign,CONTEXT/'result.json',CONTEXT/'diagnostic.json.gz',PRIMARY/'result.json',PRIMARY/'diagnostic.json.gz',PRIMARY/'exact-three-source-primary.json',PRIMARY/'exact-three-source-primary.request.json',VISUAL/'result.json',VISUAL/'complete-three-original-and-foreign-silhouette-2880x1620.png',ROOT/rows[FOREIGN]['catalogue']['path']]
 s=importlib.util.spec_from_file_location('peking_silhouette_proposal_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'named-complete-already-installed-foreign-silhouette-under-unchanged-ordinary-limits-source-proposal-v1',refs,dict(uids=[OWN,FOREIGN],tests=26,testResult='26 actual-source and adverse tests passed2.583s before proposal freeze',identityAccepted=False,physicalAccepted=False,collisionExemption=False,publication=False,sourceGeometryChanges=0,currentManifestAcceptanceClaimed=False,rawCurrentBasicProxyForeignExcessM2=proof['rawCurrentBasicProxyForeignExcessM2'],currentCompleteInstalledOriginalForeignExcessM2=proof['currentCompleteInstalledOriginalForeignExcessM2'],currentAllForeignEffectiveExcessM2=proof['currentAllForeignEffectiveExcessM2'],providerAllForeignEffectiveExcessM2=proof['providerAllForeignEffectiveExcessM2'],ordinaryForeignLimitM2=1,remainingGates='Fresh immutable complete current manifest/tile/native/source/primary/request/Neon/raw full-cell replay adapter, then every independent original+literal source terrain/foundation/support/foreign collision/runtime/browser/publisher gate. No source ownership/support or collision exemption.'))
 print({k:proof[k] for k in ['rawCurrentBasicProxyForeignExcessM2','currentCompleteInstalledOriginalForeignExcessM2','currentAllForeignEffectiveExcessM2','providerAllForeignEffectiveExcessM2']},flush=True)
if __name__=='__main__':main()
