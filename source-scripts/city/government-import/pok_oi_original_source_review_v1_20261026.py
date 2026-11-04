"""Bind bounded original hospital/platform identity and architectural-role review."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from pok_oi_original_admission_v1_20261026 import MAIN, PODIUM, SOURCES, MAIN_WALLS, PODIUM_WALLS, COLUMNS, GRAPH, replay

BASE = ROOT / 'docs/astra-city/government-import'
CONFIG = BASE / 'government-xl-pok-oi-original-install-config-v1-20261026.json'


def main():
    cfg = read(CONFIG); out = BASE / cfg['review']; assert not out.exists()
    refs, pins = [Path(__file__), CONFIG], {}
    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]; refs.append(BASE/batch/'result.json')
        p = BASE/batch/filename
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p); return read(p)
    progress = take('government-xl-after-ying-hoi-pok-oi-current-progress-v1-20261026','remaining-work.json')
    actual = {r['path']:r['sha256'] for r in progress['imagesActuallyOpenedByRoot']}
    images, reports = [], []
    for width in [1280,390]:
        reportpath = BASE/cfg['browser']/str(width)/'staged-browser.json'
        report = take(cfg['browser'],str(width)+'/staged-browser.json')
        assert report['passed'] and not report['errors']
        reports.append(dict(path=str(reportpath.relative_to(ROOT)),sha256=digest(reportpath.read_bytes())))
        for v in report['views']:
            if 'time' not in v: continue
            p = reportpath.parent/v['file']; key = str(p.relative_to(ROOT))
            assert digest(p.read_bytes()) == actual[key]
            refs.append(p); images.append(dict(path=key,sha256=actual[key]))
    assert len(images)==8
    diagnostics = [r for r in progress['imagesActuallyOpenedByRoot'] if r not in images]
    for uid in ['213579','71329']:
        name = 'government-xl-after-ying-hoi-pok-oi-'+uid+'-identity-plots-v1-20261026'
        for file in ['whole-source-plan.png','whole-source-perspectives.png']:
            p = BASE/name/file
            if name not in pins:
                pins[name] = authenticate(BASE/name)[1]; refs.append(BASE/name/'result.json')
            assert digest(p.read_bytes()) == pins[name][str(p.relative_to(ROOT))]
            refs.append(p); diagnostics.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    summary = take(cfg['scope'],'summary.json'); forms={}
    for r in summary['rows']:
        for f in take(cfg['scope'],r['uid'].split('/')[1]+'-forms.json.gz'): forms[f['building']['uid']]=f['building']
    assert len(forms)==8
    primary = take('government-xl-after-ying-hoi-pok-oi-primary-records-v1-20261026','summary.json')
    assert primary['missingRequestedCSUIDs']==[] and primary['footprints']==3
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    proof = dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
    result = dict(uids=[MAIN,PODIUM], sourceSHA256ByUid=SOURCES, requiredOriginalAssembly=SOURCES,
                  identityAccepted=True, identityProof=proof, identityProofByUid={u:proof for u in SOURCES},
                  sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True,
                  visualAcceptance=True, originalSourceReviewAccepted=True,
                  completeFourWorldSourceClearance=True, completeFourWorldFoundations=True,
                  rawGroundClearancePassed=False, rawPodiumCapPassed=False, rawStrictMainOnPodiumPassed=False,
                  completeCurrentNeighbourChecks=8, supportByUid=GRAPH, runtimeAvailabilityDependenciesByUid=GRAPH,
                  physicalSupportByUid={}, retainedBasicSupportDependencies=[], retainedCurrentBasicSupportUids=[], retainedNativeEntries={},
                  acceptedGroundWallFacesByUid={MAIN:MAIN_WALLS,PODIUM:PODIUM_WALLS},
                  groundedIsolatedWallComponents=COLUMNS, belowGradeLowerWallStripFaces=[2699],
                  currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),
                  leaseResources=sorted('building:'+u for u in forms), terrainEdits=False,
                  sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False,
                  sourceEvidenceInterpretationUsedAI=True, installationApproved=False, publication=False,
                  imagesActuallyViewed=images, diagnosticImagesActuallyViewed=diagnostics, browserReports=reports,
                  review=dict(
                      identity='Exact original B223703400701063C0 and B223183393302062G0 graphs, selected government ObjectID/CSUID routes and full geographic-cell coverage bind the sources to named Pok Oi Hospital tower/platform components. Both current forms share way/375224148. Complete original plans/perspectives show tower envelope details and the broad original podium deck, covered paths, forecourt and columns extending beyond the narrower 2D footprints. Source target coverage is99.695%/99.316%. Accept these exact original extensions while preserving14.360m/44.872m extent and unrelated-projection warnings. No shape is trimmed, scaled, translated, renamed or assigned ownership over another source. Recorded top61.7/10.1 and actual original maxima79.9848/15.7388 remain distinct provenance facts; no height metadata is used to rescale the sources.',
                      ground='The complete established four-world foundation policy passes with zero faces wholly buried beyond its existing0.5m criterion and zero upward burial. Main20walls have exact clear-cap paths. Podium105of153negativewalls have clear-cap paths, including thin lower wall strip2699. Its3vertices are actually below the current sloping ground (-0.211..-0.765m); it is an original roughly2cm-tall lower wall seam connected to the larger exposed wall, not a roof/walking floor or a claimed exposed vertex. Retain this exact below-grade seam. The other48negativefacets are two original24facet column shells with exposed upper vertices and direct positive-dimensional terrain contacts inall4worlds. A freestanding grounded original column shell need not connect to an upward roof cap. Raw48cap and highestvertex/strictsupport failures remain false; no blanket wall exemption or new terrain tolerance is created.',
                      interfaces='All238transverse original tower/platform crossings perworld occur at their lower same-campus wall/deck junctions in the inspected full-locus diagram; they are accepted as authored original architectural assembly interfaces. No claim of zero interpenetration or structural certification. Retained care-home56488 keeps its whole current BASIC; the14source/BASIC intersections are original low entrance-canopy/walkway abutments visible in the before/after context, with only0.05236m2 footprint overlap. Other external BASIC pairs have zero positive finite contacts. Main57855 projected overlap is above its roof and has zero finite contacts. All other native bounds are separated across the full6968actor inventory.',
                      availability='Podium71329 waits for exact co-imported Main213579 SHA/CSUID to avoid its broad platform appearing through the old Main BASIC. This is a runtime availability edge, not physical support: the140strict Main-on-podium probes stillfail, and no reverse edge is introduced. Main is independently qualified against existing ground. Existing private mobile failed-download/retry and joint activation pass; guarded publication still requires exact catalogue preservation and fresh live checks.',
                      visual='ROOT actually opened all8private desktop/mobile day/night exports, corrected two-angle wall/ground context, care-home before/after contact context, all238pair-locus context and four full-source identity exports. Originalhospital silhouette/roof plant/platform/coveredpaths are readable. Night source is dark and retains original appearance without procedural windows. Staged images are no substitute for new live checks after publication.',
                      limits='Exact source pair and current immutable scene only. No acceptance transfers to other models, changed ground or source revisions. No geometry/terrain/placement edits, AI modelling or optimisation. Existing global retained BASIC support guards, all6968oldassets/entries and521fixedXLrows must pass after installation.'))
    refs.extend(replay(cfg,result))
    save(out/'ROOT-SOURCE-REVIEW.json',result); save(out/'ROOT-PHYSICAL-REVIEW.json',result)
    module('pok_oi_source_review_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        cfg['review'],'exact-original-hospital-platform-grounded-column-and-interface-review',list(dict.fromkeys(refs)),result)


if __name__=='__main__':
    main()
