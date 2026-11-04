"""Preserve fresh raw identity and full detached-source context, no promotion."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,digest
BASE=ROOT/'docs/astra-city/government-import'
CURRENT='government-xl-yoho-eight-current-full-cell-preflight-20261009';SURFACE='government-xl-yoho-eight-detached-original-surface-context-20261009'
def main():
 spec=importlib.util.spec_from_file_location('yoho_current_surface_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 p=BASE/CURRENT;d=read(p/'raw-full-cell-proof.json');assert d['passed'] is False and set(d['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
 inp=read(p/'selection.json.gz');ctx=read(p/'context.json.gz')['rows'][0];paths=[Path(__file__),HERE/'xl-yoho-eight-current-full-cell-preflight-20261009.py',HERE/'routed_original_cell_identity.py',HERE/'government_georef_cell_identity.py',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',ROOT/inp['rows'][0]['candidate']['path']]
 paths.extend(ROOT/u for u in read(p/'input-refs.json')['inputHashes']);paths.extend(ROOT/'3d-viewer'/u for u in ctx['neighbourTileHashes'])
 (p/'README.md').write_text('''# Yoho Town Block8 fresh complete raw identity

Fresh unchanged original14792-face source and current city forms are bound to
manifest28c050db0aa70ab376e25b556a9c42ad3703a666d3aa9f9432cb82d2471b3ee7.
The full source and current target both cover the entire1m GeoRef cell. Ordinary
source graph, unchanged source pose, exact own identifiers and coverage/extent
guards remain intact. Raw identity fails only sourceExcessCoveredByUnrelatedFormsM2
and full-source-unrelated-overlap: the sole actual overlapping actor is the exact
current original-site podium231756. This checkpoint grants no related-role or
identity acceptance. A proposed separately reviewed source-specific OP/original
interface interpretation must preserve all raw overlaps/current actors and every
physical/runtime gate. No source, current form, placement or catalogue changed.
''')
 m.freeze(CURRENT,'fresh-complete-original-current-full-cell-raw-identity-v1',paths,{'uids':['landsd/146396:0'],'identityAccepted':False,'scriptFullAcceptancePassed':False,'rawIdentityReasons':d['reasons'],'sourceWholeCell':True,'targetWholeCell':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'sole-named-original-podium-overlap-role-unreviewed','nextStep':'Independently review a narrowly exact related-podium identity route; preserve both complete cells, raw overlaps and every other current actor. No physical or installed credit from identity.'})
 p=BASE/SURFACE;d=read(p/'diagnostic.json.gz');s=read(p/'summary.json');assert len(d['completeDetachedComponents'])==143
 for r in d['evidenceRefs']+d['primaryImages']+d['plots']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 (p/'README.md').write_text('''# Yoho Town Block8 detached original surface context

All143 detached source components are retained. Every unique original component
vertex was measured against the complete810-component source-connected tower
geometry. These are floating-point vertex witnesses, not continuous distance
certificates or replacement for the exact prior no-contact proof. Two-face parts
have vertex offsets0.000259–0.015m;34-face repeated projecting frames reach0.532m;
4/16-face source bay/panel parts reach1.122m. No mounting structure is invented.

All five2400x1800 scientific exports were independently inspected. They display
complete representative original components and exact nearby source triangles,
with a display-only axis reorder and documented crop. The original provider
hierarchy has one named root, one unnamed mesh and default material; no authored
component function labels exist. Repeated geometry may represent façade frames,
panels, bays or other equipment, but triangle count alone assigns no role.

First-party manufacturer project context and two source images are captured at
https://www.general-aircon.com/en/about-us/past-project/detail/yoho-town . It
documents2004 Yoho Town air-conditioning work. Both images were inspected, but
they are low-resolution project views without Tower8/component registration.
They cannot label all143 parts as air conditioners or certify attachments. The
manufacturer's approximate1400-unit statement differs from the developer's
2200-unit project description at
https://www.shkp.com/sites/assets/files/2019-01/E_AR_2002_03.pdf ; neither is used
for component identity or source acceptance. Full raw page/images are retained.

No physical/support/identity acceptance, source or terrain edits, suppression,
geometry generation, mounting assumptions, or installation occurred. Next work
is complete original source-bound façade/surface role and actual current support,
followed by independent physical, foreign, runtime, browser and publication gates.
''')
 paths=[Path(__file__),HERE/'xl-yoho-eight-detached-original-surface-context-20261009.py',*[ROOT/r['path'] for r in d['evidenceRefs']],BASE/'government-xl-yoho-eight-complete-original-component-graph-20261009/result.json']
 m.freeze(SURFACE,'every-detached-original-vertex-complete-attached-surface-and-primary-context-v1',paths,{'uids':['landsd/146396:0'],'identityAccepted':False,'scriptFullAcceptancePassed':False,'completeDetachedOriginalComponents':143,'maximumVertexOnlyDiagnosticDistanceM':s['maximumVertexDistanceM'],'primaryImages':2,'inspectedScientificExports':5,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'original-detached-facade-surface-role-and-current-support-not-certified-by-unregistered-primary-imagery','nextStep':'Preserve complete143-source-part inventory/exact no-contact graph; pursue source-bound full surface roles and current physical checks, rather than claiming all parts are air conditioners or editing/welding originals.'})
 print(json.dumps({'stages':[CURRENT,SURFACE],'publication':False}),flush=True)
if __name__=='__main__':main()
