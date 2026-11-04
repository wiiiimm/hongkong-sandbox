"""Persist completed current-neighbour work and the actual next installation gates."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-sung-fung-three-source-actionable-progress-v2-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];jobs={}
    names=['government-xl-next-repairs-sung-fung-three-source-actionable-progress-v1-20261024','government-xl-next-repairs-sung-fung-three-original-contact-census-v1-20261024','government-xl-next-repairs-sung-fung-wall-zero-upper-grade-interfaces-v1-20261024','government-xl-next-repairs-sung-fung-wall-zero-clear-cap-path-v1-20261024','government-xl-next-repairs-sung-fung-55-separate-facade-groups-v1-20261024','government-xl-next-repairs-sung-fung-55-separate-boundary-groups-v1-20261024','government-xl-next-repairs-sung-fung-55-finite-backing-groups-v1-20261024','government-xl-next-repairs-sung-fung-55-facade-source-views-v1-20261024','government-xl-next-repairs-sung-fung-three-original-attributes-v1-20261024','government-xl-next-repairs-sung-fung-three-current-model-only-scope-v2-20261024','government-xl-next-repairs-sung-fung-three-current-native-contacts-v1-20261024','government-xl-next-repairs-nam-fung-original-podium-replacement-support-v2-20261024','government-xl-next-repairs-sung-fung-three-current-basic-contacts-v1-20261024','government-xl-next-repairs-sung-fung-podium-identity-review-v1-20261024']
    summaries={}
    for name in names:
        receipt,pins=authenticate(base/name);jobs[name]=receipt['jobId'];refs.append(base/name/'result.json')
        path=base/name/'summary.json'
        if path.exists():assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);summaries[name]=read(path)
    result=dict(uids=['landsd/79098:0','landsd/45779:0','landsd/47160:0'],retainedNativeDependencyUid='landsd/79099:0',status='held-for-current-source-physical-and-support-resolution',heldForCompute=True,heldForHumanDecision=False,aiGeometryModellingRequired=False,permanentRejection=False,installationApproved=False,publication=False,newlyInstalled=0,fixedXL=dict(total=521,installed=339,unfinished=182),sourceGeometryChanges=0,sourcePoseChanges=0,productionMetadataChanges=0,evidence=jobs,
        completed=[
            'Completed exact current model-only scope: three sources,8distinct nearby current forms,all6863installed-native bounds considered. Existing native79099 overlaps proposed podium;79097 has strict complete-world bound separation.',
            'Captured all13061faces of current installed Nam Fung79099 with its actual current entry/form/asset and allfourcoordinate streams. Complete podium/native finite contacts:375positive non-area surface pairs original/left/balanced,397literal; no area contacts. Rawcontacts retained, not called collision-clear.',
            'Measured current-basic versus proposed-original support for Nam Fung in allfourworlds: currentbasic0/207strictcontacts; originalpodium137/207strictcontacts,70unresolved. No dependency updated or physical approval given.',
            'Completed9whole-source current-basic contact pairs before/after. Five unrelated pairs are zero positive contacts and zero projectedoverlap in allfourproposedworlds. All current co-import basic interactions retained in diagnostics rather than silently excluded.',
            'Approved bounded exact podium identity only: verified governmentroot/ObjectID/CSUID/currentroute/wholecell, completeunchangedtower+podium99.7057percenttargetcoverage and inspected originalassembly/lowterraces. Preserve allfourraw shape warnings and exactrequiredassemblySHA tuples. Physical gates remain.',
            'Completed upper-ground zero-gap interval proof for genuine sourcewallface0 in allfourworlds, plus exact positive-dimensional wall-only path[0,1,11593,11575]to clearoriginalcap. Diagnostic, no physical-root approval.',
            'ROOT has now inspected remaining facade atlas7/group55, close-ups15/55, complete three-source assembly and base diagnostic. All55detached groups remain intact. Their exploratory whole-facet/boundary/backing results do not create an independent installation gate.'
        ],remaining=[
            'Resolve actual Sung terrain-intersection/contact failures and podium three below-grade wall faces through existing bounded exterior-wall/whole-source foundation rules; retain raw negative measurements.',
            'Resolve actual Lee & Man canonical support failures and complete compound foundations. Positive original contact graph is evidence, not automatic support approval.',
            'Resolve retained Nam Fung70unresolved original-podium support probes, full compoundfoundation and source relationship before any atomic dependency replacement. Current fallback must remain until replacement is accepted.',
            'Qualify actual original-assembly contacts/current scene, then staged/live desktop/mobile/picking/collision/failurefallback checks and full521Neon readback before installation credit.'
        ],notIndependentHolds=[
            'Per-component structural rooting, certification of every repeated facade ornament, global watertightness and point-only decorative contacts are not independent viewer acceptance requirements. Do not spend further work proving facade mounts unless a specific canonical clearance/support/collision/runtime failure depends on them. Whole-source geometry and raw failures must still be retained.'
        ],nextActions=['Continue actual source/ground and support-failure resolution with complete source arrays and current neighbour bindings. Do not repeat recovered-source searches or five already-clear unrelated basic pairs unless inputs change.','Keep182unfinished sources in scope, continue other actionable originals as needed; do not turn a compute hold into corruption or permanent rejection.'],sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,scriptExternalAICalls=0,qualification='Completed evidence and bounded identity review only. No new models installed, no production terrain/catalogue/dependency changed, no geometry generated, and no global acceptance threshold relaxed.')
    save(out/'summary.json',result);module('sung_three_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'three-source-current-native-support-foreign-and-bounded-identity-progress',refs,result)

if __name__=='__main__':main()
