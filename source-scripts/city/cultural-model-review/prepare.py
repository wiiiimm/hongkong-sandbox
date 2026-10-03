"""Copy five pinned native candidates for review; no publication or acceptance."""
import hashlib,json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent
UIDS=['landsd/168596:0','landsd/205817:0','landsd/279530:0','landsd/310908:0','landsd/283788:0']
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 pin=read(ROOT/'source-scripts/city/landmark-preflight/snapshot.json');assert pin['id']=='3887f2f23fbad306'
 source=ROOT/'source-scripts/city/landmark-preflight/snapshots'/pin['id'];assert sha(source/'catalogue.json')==pin['files']['catalogue.json']['sha256']
 cat=read(source/'catalogue.json');cat['models']=[m for m in cat['models'] if m['uid'] in UIDS];assert {m['uid']for m in cat['models']}==set(UIDS)
 cat['counts']={'packedModels':len(UIDS)};cat['area']='West Kowloon cultural landmarks — unapproved native candidate review'
 for m in cat['models']:
  m['proceduralWindows']=False
  m['facadeReview']='Opaque or screened cultural facade: suppress generic repeated office windows; retain native non-textured materials and authored openings. See cultural-model-review visual acceptance for per-part official sources.'
  asset=source/'assets'/m['asset'];assert sha(asset)==m['sha256'];shutil.copyfile(asset,HERE/'candidates'/m['asset'])
 save(HERE/'candidates/catalogue.json',cat);save(HERE/'candidates/catalogue-index.json',{'models':len(UIDS),'catalogues':['catalogue.json']})
 pre=read(ROOT/'docs/astra-city/landmark-preflight/report.json');parts=[p for p in pre['parts'] if p['uid'] in UIDS]
 save(HERE/'source-identities.json',{'snapshotId':pin['id'],'parts':[{'uid':p['uid'],'objectId':p['objectId'],'csuid':p['csuid'],'name':p['name'],'acquisitionEvidence':p['acquisitionEvidence']}for p in parts]})
 print(json.dumps({'candidates':len(UIDS),'compressedBytes':sum(m['bytes'] for m in cat['models']),'published':False}))
if __name__=='__main__':main()
