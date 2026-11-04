"""Scoped source-authored platform grade interpretation for private V9 terrain."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-platform-grade-review-v2-20261019';DOC=BASE/BATCH
NAMES=['v5-identity-support-review','component-support-review-v2','eight-foundations-v1','eight-foundations-v4','eight-runtime-v4','eight-neighbours-v4','platform-rim-compare-v6','vertical-edge-terrain-v4','vertical-context-v1','vertical-views-v1','runtime-buried-coverage-v4','buried-coverage-literal-v1','buried-coverage-explicitLeftF32-v1','buried-coverage-explicitBalancedF32-v1','contact-faces-v2']
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
        name='281463:0-'+mode+'.json';old=read(folders['eight-foundations-v1']/name);current=read(folders['eight-foundations-v4']/name)
        assert old['wholeWorldSHA256']==current['wholeWorldSHA256']and {r['faceId']for r in current['buriedFaces']}<={r['faceId']for r in old['buriedFaces']}
        assert current['foundation']['fullyBuriedTriangles']==95 and current['foundation']['fullyBuriedUpwardTriangles']==25
        key='runtime-buried-coverage-v4'if mode=='original'else 'buried-coverage-'+mode+'-v1';cov=read(folders[key]/'summary.json')
        assert cov['fullyHiddenFaces']==57 and cov['projectedVerticalBuriedFaces']==71 and cov['remainingBuriedFaces']==128 and cov['exposedFaces']==cov['exposedFragmentsAboveHalfMetre']==0
        if mode!='original':assert cov['wholeWorldSHA256']==current['wholeWorldSHA256']
        edge=read(folders['vertical-edge-terrain-v4']/(mode+'.json'));assert edge['summary']['faces']==71 and edge['summary']['maximumRise']<.001
        for r in edge['rows']:
            for interval in r['intervals']:
                if interval.get('missingOriginal')or interval.get('missingCandidate'):assert interval.get('missingOriginal')and r['faceId']==30109
        assert edge['summary']['missingLength']<.001
        found.append(current);coverage.append(cov);edges.append(edge['summary'])
    rim=read(folders['platform-rim-compare-v6']/'comparison.json')['summary'];assert rim['lowRimChecks']==481 and rim['newlyFailingSamples']==0 and rim['terrainChangeRange'][1]<.001
    metrics=read(folders['eight-runtime-v4']/'metrics.json')['rows'];assert len(metrics)==8 and all(r['sourcePreserved']and r['maxSamplerDelta']==0 and r['missingTerrain']==0 for r in metrics)
    neighbours=read(folders['eight-neighbours-v4']/'summary.json');assert not neighbours['basicReasons']and not neighbours['unresolvedNatives']
    identity=read(folders['v5-identity-support-review']/'ROOT-IDENTITY-SUPPORT-REVIEW.json');assert identity['platformIdentityAccepted']and read(folders['component-support-review-v2']/'ROOT-SUPPORT-REVIEW.json')['sourceSpecificComponentSupportInterpretationAccepted']
    images=[folders['contact-faces-v2']/'contact-faces.png',*sorted(folders['vertical-views-v1'].glob('group-*.png'))];assert len(images)==5
    decision=dict(reviewer='Codex ROOT',uid='landsd/281463:0',sourceSHA256=identity['sourceSHA256'],originalGradeInterpretationAccepted=True,sourceSpecific=True,rawStrictFoundationPassed=False,currentFoundationEvidence=found,sourceOnlyHiddenCoverage=coverage,currentVerticalEdgeSummaries=edges,currentCanonicalRim=rim,inspectedSourceContextImages=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],observations=[
        'The complete37577-face source is unchanged in all four coordinate modes. Current95 buried faces (25upward) are a verified subset of the original128 reviewed faces. The old source-only occlusion proof remains valid for that subset: no new source face has been classified as an embedded boundary.',
        'All71 previously reviewed vertical wall edges have been compared against finalV9 terrain in all four coordinate modes. Maximum rise is0.000084625m. Only the original face30109 missing-source interval remains; candidate-only wall gaps introduced by the earlier inset have been repaired with unchanged source facets.',
        'Canonical replay retains481rim samples and zero new failures relative to original government terrain. Maximum rise is0.000211058m. Original lower-boundary warnings remain explicit; this is source-specific interpretation, not a tolerance change or zero-gap certification.',
        'All eight actual runtime sources retain geometry with no missing terrain samples or sampler disagreement. The262affected forms and three installed natives pass current checks. The seven companion support interpretations are independently refreshed against finalV9, including finite contact replay, current buried-face subsets and exposed-upper-surface checks.'
    ],qualification='Exact immutable platform, V9terrain, current captured geometry and eight-source assembly only. Raw rim/foundation warnings remain. Source, terrain or renderer changes require renewed evidence. Browser acceptance and guarded publication remain outstanding.',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,modelGeometryChanges=0,sourcePoseChanges=0,publicationApproved=False,installationApproved=False)
    save(DOC/'ROOT-GRADE-REVIEW.json',decision)
    module('platform_grade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-platform-grade-v9-review',list(dict.fromkeys(refs)),dict(uids=['landsd/281463:0'],originalGradeInterpretationAccepted=True,sourceSpecific=True,installationApproved=False))
    print('Exact-source platform grade interpretation accepted; browser/publication outstanding.',flush=True)
if __name__=='__main__':main()
