"""Freeze primary plan observations; no source acceptance or geometry changes."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-inone-primary-layout-review-v2-20261022'
def main():
 local=HERE/'local/government-xl-inone-primary-plan-20261022'
 doc=ROOT/'docs/astra-city/government-import'/BATCH
 assert not doc.exists()
 provenance=read(local/'provenance.json')
 pdf=local/'official-brochure.pdf'
 assert digest(pdf.read_bytes())==provenance['sha256']
 pages=[local/f'page-{i}.png' for i in range(30,34)]
 review=dict(uids=["landsd/277890:0","landsd/277973:0"],source=provenance,reviewer='Codex ROOT',actuallyViewedPdfIndices=[30,31,32,33],relevantPdfIndex=32,printedPage=31,observations=[
 'The layout distinguishes Site A and Site B and shows residential towers and clubhouse areas around Ho Man Tin station structures.',
 'Station exits, ventilation structures and below-development station facilities are explicitly labelled; the site boundary excludes station and government accommodation.',
 'The layout is architectural context, not a georeferenced attribution of the 843.564 square metre overlap between original government sources 277890 and 277973.'
 ],nextAction='Match the government footprint outlines and flagged extension to the layout using independently identifiable station exits and tower locations; retain the original raw identity flags until that correspondence is established.',sourceIdentityApproved=False,installationApproved=False,geometryChanges=0,optimisation=False)
 doc.mkdir(parents=True)
 save(doc/'primary-layout-review.json',review)
 refs=[Path(__file__),pdf,local/'provenance.json',*pages]
 module('inone_primary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'primary-layout-source-context',refs,review)
 print('Primary layout review saved; no installation approval.')
if __name__=='__main__':main()
