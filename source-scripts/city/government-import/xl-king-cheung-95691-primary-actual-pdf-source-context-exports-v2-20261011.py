"""Render exact captured primary PDF pages and named text-located crop.
No source/map geometric registration, floor/grade or appendage ownership credit.
"""
import importlib.util,json,math
from pathlib import Path
import pymupdf
import numpy as np
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-king-cheung-95691-dc-exact-site-plan-primary-packet-v1-20261011'
OWNER_DATA=BASE/'government-xl-king-cheung-95691-ha-exact-owner-data-v1-20261011'
OWNER_PACKET=BASE/'government-xl-king-cheung-95691-ha-owner-bfa-plan-photo-packet-v1-20261011'
SOURCE_CONTEXT=BASE/'government-xl-king-cheung-95691-complete-original-extra-context-v1-20261011'
SOURCE=BASE/'government-xl-king-cheung-95691-untouched-original-recovery-v1-20261011'
BATCH='government-xl-king-cheung-95691-primary-actual-pdf-source-context-exports-v2-20261011';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(INPUT/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 packet=read(INPUT/'primary-packet.json');owner_packet=read(OWNER_PACKET/'primary-packet.json');assert len(packet['records'])==len(owner_packet['records'])==2 and all(r['downloadSucceeded']and r['status']==200 for r in packet['records']+owner_packet['records'])
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for p in [OWNER_PACKET/'result.json',OWNER_DATA/'result.json',SOURCE_CONTEXT/'result.json',SOURCE/'result.json']:
   r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 DOC.mkdir(parents=True);refs=[Path(__file__),INPUT/'result.json',INPUT/'primary-packet.json',OWNER_PACKET/'result.json',OWNER_PACKET/'primary-packet.json',OWNER_DATA/'result.json',OWNER_DATA/'named-owner-record.json',OWNER_DATA/'raw/owner-named-district-estates.json',SOURCE_CONTEXT/'result.json',SOURCE_CONTEXT/'diagnostic.json.gz',SOURCE/'result.json',SOURCE/'selection.json.gz',HERE/'exact_packed_world_geometry_20261009.py'];records=[]
 for source in packet['records']+owner_packet['records']:
  pdf_path=ROOT/source['body']['path'];assert digest(pdf_path.read_bytes())==source['body']['sha256'];refs.append(pdf_path)
  if pdf_path.suffix.lower()!='.pdf':continue
  pdf=pymupdf.open(pdf_path);assert 1<=len(pdf)<=10
  for i,page in enumerate(pdf):
   text=page.get_text();text_path=DOC/(pdf_path.stem+f'-page-{i+1}-text.txt');text_path.write_text(text)
   bounds=page.rect;width=3200 if 'layout-plan'in pdf_path.name else 1600;scale=width/bounds.width
   pix=page.get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False);out=DOC/(pdf_path.stem+f'-page-{i+1}-{pix.width}x{pix.height}.png');pix.save(out)
   record=dict(sourcePDF=ref(pdf_path),pageIndexZeroBased=i,pdfPageRectPoints=list(bounds),output=ref(out),dimensions=[pix.width,pix.height],actualPDFRendered=True,registrationClaimed=False,originalSourceMeshChanges=0)
   hits=page.search_for('King Cheung House')
   if hits:
    assert len(hits)==1;named=hits[0];crop=pymupdf.Rect(named.x0-180,named.y0-180,named.x1+180,named.y1+180)&bounds
    pix=page.get_pixmap(matrix=pymupdf.Matrix(2400/crop.width,2400/crop.width),clip=crop,alpha=False);out=DOC/(pdf_path.stem+f'-king-cheung-label-crop-{pix.width}x{pix.height}.png');pix.save(out)
    record['namedTextLocatedCrop']=dict(labelRectPoints=list(named),cropRectPoints=list(crop),output=ref(out),dimensions=[pix.width,pix.height],geometricSourceAssociationAccepted=False)
   if 'barrier-free'in pdf_path.name:
    extracted=[]
    for image_number,image in enumerate(page.get_images()):
     body=pdf.extract_image(image[0]);p=DOC/f'owner-bfa-page-{i+1}-image-{image_number}-xref-{image[0]}.{body["ext"]}';p.write_bytes(body['image']);extracted.append(dict(originalPDFXref=image[0],originalPixelDimensions=[body['width'],body['height']],output=ref(p),imageGeoregistrationAccepted=False))
    record['originalEmbeddedImages']=extracted
   records.append(record)
 owner_raw=json.loads((OWNER_DATA/'raw/owner-named-district-estates.json').read_text(encoding='utf-8'))
 named=[r for r in owner_raw if r['aplySysId']=='1418347800065'];assert len(named)==1 and named[0]['name']['zh-Hant']=='祥龍圍邨'and '景祥樓'in named[0]['blockName']['zh-Hant']
 save(DOC/'explicit-utf8-owner-record.json',dict(source=ref(OWNER_DATA/'raw/owner-named-district-estates.json'),encoding='UTF-8',uniqueNamedOwnerRecord=named[0],oldDerivedMojibakeReceiptPreserved=True))
 row=read(SOURCE/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
 world=decode_original_world_triangles(asset.read_bytes());prior=read(SOURCE_CONTEXT/'diagnostic.json.gz');assert world.shape==(18742,3,3)and digest(world.tobytes())==prior['completeOriginalWorldSHA256']
 groups=prior['completeTopology']['sharedEdgeConnectedComponents'];ids=sorted(set(f for i in [39,43,44]for f in groups[i]));assert len(ids)==104
 hk80=np.stack([world[:,:,0]+834500,816500-world[:,:,2]],axis=-1)
 save(DOC/'original-hk80-source-context.json.gz',dict(uids=[row['uid']],source=ref(asset),sourceWorldSHA256=digest(world.tobytes()),coordinateContract='HK80 E=originalViewerX+834500; N=816500-originalViewerZ; source decoder contract only, no image fitting or surveyed claim',selectedCompleteSourceParts=[dict(part=i,faces=groups[i],literalOriginalTriangles=world[groups[i]].tolist(),literalHK80ProjectedTriangles=hk80[groups[i]].tolist())for i in [39,43,44]],completeOriginalSourceFaces=18742,currentFormHistoricalContext=prior['currentForm'],noSourceGeometryChanges=True,planRegistrationAccepted=False,appendageOwnershipAccepted=False))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 fig,ax=plt.subplots(figsize=(12,9));ax.add_collection(PolyCollection(hk80,facecolors='#4f86cb',edgecolors='none',alpha=.1));ax.add_collection(PolyCollection(hk80[ids],facecolors='#c93e49',edgecolors='#833641',linewidths=.3,alpha=.8))
 for ring in prior['currentForm']['rings']:
  r=np.asarray(ring);ax.plot(r[:,0]+834500,816500-r[:,1],color='black',linewidth=1.3)
 ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('HK80 East(m)');ax.set_ylabel('HK80 North(m)');ax.ticklabel_format(useOffset=False,style='plain');ax.set_title('Complete original King Cheung18,742faces: red low parts39/43/44\nBlack current Tower outline; NO map fit, ownership or support acceptance')
 fig.savefig(DOC/'literal-original-hk80-source-projection-2400x1800.png',dpi=200);plt.close(fig)
 save(DOC/'exports.json',dict(uids=['landsd/95691:0'],records=records,rendererVersion=pymupdf.VersionBind,rendererModule=ref(Path(pymupdf.__file__))if Path(pymupdf.__file__).is_relative_to(ROOT)else dict(modulePath=str(Path(pymupdf.__file__)),sha256=digest(Path(pymupdf.__file__).read_bytes())),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,surveyedRegistrationClaimed=False,appendageOwnershipAccepted=False,currentAcceptance=False,installationApproved=False))
 s=importlib.util.spec_from_file_location('king_cheung_pdf_export_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'actual-captured-primary-pdf-page-and-label-crop-exports-no-registration-or-role-credit',refs,dict(uids=['landsd/95691:0'],exportedPages=len(records),currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(records),flush=True)
if __name__=='__main__':main()
