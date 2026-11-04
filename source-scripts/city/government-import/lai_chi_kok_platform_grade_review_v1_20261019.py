"""Scoped source-authored platform grade interpretation for private V5 terrain."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-platform-grade-review-v1-20261019';DOC=BASE/BATCH
NAMES=['v5-identity-support-review','eight-foundations-v1','eight-foundations-v2','eight-runtime-v2','eight-neighbours-v2','platform-rim-compare-v3','vertical-edge-terrain-v2','vertical-context-v1','vertical-views-v1','runtime-buried-coverage-v4','buried-coverage-literal-v1','buried-coverage-explicitLeftF32-v1','buried-coverage-explicitBalancedF32-v1','contact-faces-v2']
def main():
    assert not DOC.exists();folders={n:BASE/('government-xl-lai-chi-kok-'+n+'-20261019')for n in NAMES};refs=[Path(__file__)];pins={}
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for d in folders.values():
            r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
            for e in r['evidenceRefs']:
                assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    found=[];coverage=[];edges=[]
    for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
        name='281463:0-'+mode+'.json';old=read(folders['eight-foundations-v1']/name);current=read(folders['eight-foundations-v2']/name)
        assert old['wholeWorldSHA256']==current['wholeWorldSHA256']and [r['faceId']for r in old['buriedFaces']]==[r['faceId']for r in current['buriedFaces']]
        assert current['foundation']['fullyBuriedTriangles']==128 and current['foundation']['fullyBuriedUpwardTriangles']==27
        key='runtime-buried-coverage-v4'if mode=='original'else 'buried-coverage-'+mode+'-v1';cov=read(folders[key]/'summary.json')
        assert cov['fullyHiddenFaces']==57 and cov['projectedVerticalBuriedFaces']==71 and cov['remainingBuriedFaces']==128 and cov['exposedFaces']==cov['exposedFragmentsAboveHalfMetre']==0
        if mode!='original':assert cov['wholeWorldSHA256']==current['wholeWorldSHA256']
        edge=read(folders['vertical-edge-terrain-v2']/(mode+'.json'));assert edge['summary']['faces']==71 and edge['summary']['maximumRise']<.001
        for r in edge['rows']:
            for interval in r['intervals']:
                if interval.get('missingOriginal')or interval.get('missingCandidate'):assert interval['missingOriginal']and interval['missingCandidate']and r['faceId']==30109
        assert edge['summary']['missingLength']<.001
        found.append(current);coverage.append(cov);edges.append(edge['summary'])
    rim=read(folders['platform-rim-compare-v3']/'comparison.json')['summary'];assert rim['lowRimChecks']==481 and rim['newlyFailingSamples']==0 and rim['terrainChangeRange'][1]<.001
    metrics=read(folders['eight-runtime-v2']/'metrics.json')['rows'];assert len(metrics)==8 and all(r['sourcePreserved']and r['maxSamplerDelta']==0 and r['missingTerrain']==0 for r in metrics)
    neighbours=read(folders['eight-neighbours-v2']/'summary.json');assert not neighbours['basicReasons']and not neighbours['unresolvedNatives']
    identity=read(folders['v5-identity-support-review']/'ROOT-IDENTITY-SUPPORT-REVIEW.json');assert identity['platformIdentityAccepted']and identity['sourceSpecificComponentSupportInterpretationAccepted']
    images=[folders['contact-faces-v2']/'contact-faces.png',*sorted(folders['vertical-views-v1'].glob('group-*.png'))];assert len(images)==5
    decision=dict(reviewer='Codex ROOT',uid='landsd/281463:0',sourceSHA256=identity['sourceSHA256'],originalGradeInterpretationAccepted=True,sourceSpecific=True,rawStrictFoundationPassed=False,currentFoundationEvidence=found,sourceOnlyHiddenCoverage=coverage,currentVerticalEdgeSummaries=edges,currentCanonicalRim=rim,inspectedSourceContextImages=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],observations=[
        'The same complete 37577-face source in all four coordinate modes retains exactly the same128 wholly buried facets. Fifty-seven nonvertical facets are fully hidden by higher original source surfaces, including all27 upward facets. The remaining71 are vertical lower platform walls already embedded in government source terrain; the previously inspected wall closeups place them along the stepped/curved platform perimeter.',
        'Continuous edge comparison against the original government TIN limits the candidate terrain rise to0.000135m along those71 walls. One0.000692m interval on face30109 lacks terrain in both original and candidate; retain that original export limitation explicitly, without claiming complete coverage or altering the model.',
        'Eight introduced rim failures were real retained-terrain conflicts and have been repaired using13original government ground faces. Current canonical replay has zero new failures among481samples and at most0.000258m terrain rise relative to source TIN. Remaining original low-rim gaps range approximately-5.321m to1.076m. Accept these as source-authored embedded lower boundaries/export limitations in this exact platform, not zero-gap certification or a new global tolerance.',
        'Current rendered terrain has no missing sample or sampler disagreement. All262affected forms and three installed native neighbours retain their accepted behaviour. Seven original companions keep their independently revalidated identical support domains and must be installed together with the platform.'
    ],qualification='Exact immutable platform, V5terrain, current renderer and eight-source assembly only. Raw rim/foundation warnings remain. Source, terrain or renderer changes require renewed evidence. Browser acceptance and guarded publication remain outstanding.',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,modelGeometryChanges=0,sourcePoseChanges=0,publicationApproved=False,installationApproved=False)
    save(DOC/'ROOT-GRADE-REVIEW.json',decision)
    module('platform_grade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-platform-grade-v5-review',list(dict.fromkeys(refs)),dict(uids=['landsd/281463:0'],originalGradeInterpretationAccepted=True,sourceSpecific=True,installationApproved=False))
    print('Exact-source platform grade interpretation accepted; browser/publication outstanding.',flush=True)
if __name__=='__main__':main()
