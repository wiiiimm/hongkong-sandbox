"""Stage two government GLBs with unchanged mesh buffers and reviewed terrain-visible node placement."""
import hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
LOCAL=HERE/'local/government-lantau-visible-placement-20260921';STAGE=HERE/'accepted/government-lantau-visible-placement-20260921';DOC=ROOT/'docs/astra-city/government-import/government-lantau-visible-placement-20260921'
read=lambda p:json.loads(Path(p).read_text())
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');proof=read(DOC/'placement-proof.json');catalogue=read(LOCAL/'catalogue.json')
 assert all(not row.get('error') for row in metrics['rows']) and validation['loaderAccepted']==validation['checksPassed']==2 and not validation['exceptions']
 assert set(m['uid'] for m in catalogue['models'])=={'landsd/112959:0','landsd/182471:0'}
 for row in metrics['rows']:
  assert not row.get('error') and row['maxSamplerDelta']<.004 and row['missingTerrain']==0
 for row in proof['rows']:
  assert row['sourceVertexAndTriangleBuffersUnchanged'] and not row['sourceGeometryGenerated'] and not row['aiModellingCalls']
 for m in catalogue['models']:
  source=LOCAL/m['asset'];target=STAGE/m['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);assert sha(target)==m['sha256']
 save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':2,'catalogues':['catalogue.json']});save(STAGE/'source-forms.json',read(LOCAL/'source-forms.json'))
 dest='city/data/official-models/government-lantau-visible-placement-20260921/catalogue.json'
 save(STAGE/'plan.json',{'areas':[{'area':'Tai O and Kwun Yam Temple government sources','catalogue':str((STAGE/'catalogue.json').relative_to(ROOT)),'destination':dest}]})
 save(STAGE/'browser-config.json',{'browserUids':[m['uid'] for m in catalogue['models']],'catalogueURL':dest,'doc':'docs/astra-city/government-import/government-lantau-visible-placement-20260921/','failureTestUids':[m['uid'] for m in catalogue['models']],'fitBox':True,'stage':str(STAGE.relative_to(ROOT))+'/','terrain':[]})
 print(json.dumps({'models':len(catalogue['models']),'stage':str(STAGE.relative_to(ROOT))}))
if __name__=='__main__':main()
