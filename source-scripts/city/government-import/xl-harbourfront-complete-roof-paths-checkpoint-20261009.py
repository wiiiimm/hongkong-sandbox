"""Freeze new complete original roof paths without physical/installation credit."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BATCH='government-xl-two-harbourfront-complete-original-roof-paths-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
def main():
 d=read(DOC/'diagnostic.json.gz');s=read(DOC/'summary.json');assert d['currentPhysicalAccepted'] is False and s['roofPaths']==355 and len(s['unresolvedFaces'])==7
 paths=[Path(__file__),HERE/'xl-harbourfront-complete-original-roof-paths-20261009.py',*[ROOT/r['path'] for r in d['evidenceRefs']],ROOT/'docs/astra-city/government-import/government-xl-two-harbourfront-attached-boundary-current-identity-20261009/result.json']
 for r in d['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 (DOC/'README.md').write_text('''# Two Harbourfront complete original cap-to-roof paths

New source-only diagnostic: all 355 affected original steep-wall faces now
have an exact original path to an upward roof through walls or authored cap
surfaces that are strictly clear in the historical continuous terrain context.
The two open cylinders connect through 243 exact positive-dimensional original
interfaces; 82 point contacts are retained without bridge credit. Every cylinder
face was compared with every other nondegenerate original face using unpadded
inclusive bounds and exact rational intersections. All 19,438 original faces
remain unchanged and accounted. The earlier wall-only failures remain visible.

348 faces meet geometric path plus direct/exact-coplanar exposure necessary
conditions. Seven original side triangles of the distinct 54-face low ancillary
component remain unresolved: 17716, 17736, 17738, 17739, 17846, 17850, 17851.
They have no actual above-ground witness in the historical context. An exact
roof path alone does not justify inventing a foundation or discarding exposure
requirements. The complete component has 14 open boundary edges and is not a
closed consistently wound solid, so closed-footing credit is unavailable.

Complete raw original world SHA b276304c... and historical serialized export
SHA cdceb228... differ by at most 1.4210854715202004e-14 metres. A Float32
packing explanation was tested and is false. The improved paths result from
explicit clear cap/roof geometry, not a precision repair. Historical per-face
ground contexts provide diagnostic classification only; they confer no current
physical credit. Source-specific complete roles and fresh current foundation,
terrain, foreign actor, runtime, browser, and publication gates remain required.

No source or terrain geometry edits, suppression, modelling, installation,
permanent rejection, or numeric threshold changes occurred.
''')
 spec=importlib.util.spec_from_file_location('harbourfront_paths_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'complete-original-cylinders-through-clear-caps-roof-paths-v1',paths,{'uids':['landsd/118230:0'],'identityAccepted':False,'scriptFullAcceptancePassed':False,'completeOriginalFaces':19438,'affectedOriginalWalls':355,'exactClearRoofPaths':355,'pathAndExposureNecessaryConditions':348,'unresolvedOriginalFaces':s['unresolvedFaces'],'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'seven-open-ancillary-side-faces-have-no-original-above-ground-witness-and-fresh-current-physical-required','nextStep':'Resolve the exact whole 54-face ancillary component source role, then independently rebind and validate all current physical, foreign, runtime and browser gates. Retain all original faces and all raw wall-only failures.'})
 print(json.dumps({'stage':BATCH,'exactRoofPaths':355,'unresolvedFaces':s['unresolvedFaces']}),flush=True)
if __name__=='__main__':main()
