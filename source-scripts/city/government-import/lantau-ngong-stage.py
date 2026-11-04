"""Stage the footprint-specific Ngong Ping government source component for browser acceptance."""
import hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
LOCAL=HERE/'local/government-lantau-ngong-extract-20260921';STAGE=HERE/'accepted/government-lantau-ngong-component-20260921';DOC=ROOT/'docs/astra-city/government-import/government-lantau-ngong-extract-20260921'
read=lambda p:json.loads(Path(p).read_text())
save=lambda p,v:(p.parent.mkdir(parents=True,exist_ok=True),p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 proof=read(DOC/'extraction-proof.json');m=read(DOC/'metrics.json')['rows'][0];v=read(DOC/'validation.json')['results'][0]
 assert proof['targetCoverage']>.997 and proof['installedStationOverlapM2']==0 and proof['retainedTriangles']==16
 assert not m.get('error') and m['maxSamplerDelta']<.004 and m['missingTerrain']==0
 assert not v.get('error') and v['outcome']=='runtime-accepted-placement-unreviewed'
 catalogue=read(LOCAL/'catalogue.json');model=catalogue['models'][0];assert model['uid']==proof['uid'];src=LOCAL/model['asset'];dst=STAGE/model['asset'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);assert sha(dst)==model['sha256']
 save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']});save(STAGE/'source-forms.json',read(LOCAL/'source-forms.json'))
 dest='city/data/official-models/government-lantau-ngong-component-20260921/catalogue.json'
 save(STAGE/'plan.json',{'areas':[{'area':'Ngong Ping government source component','catalogue':str((STAGE/'catalogue.json').relative_to(ROOT)),'destination':dest}]})
 save(STAGE/'browser-config.json',{'browserUids':[model['uid']],'catalogueURL':dest,'doc':'docs/astra-city/government-import/government-lantau-ngong-component-20260921/','failureTestUids':[model['uid']],'fitBox':True,'stage':str(STAGE.relative_to(ROOT))+'/','terrain':[]})
 print(json.dumps({'uid':model['uid'],'stage':str(STAGE.relative_to(ROOT)),'sourceSHA256':model['sha256']}))
if __name__=='__main__':main()
