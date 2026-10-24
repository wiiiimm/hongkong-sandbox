"""Bounded original LandsD imagery tiles for paired-source causal interpretation.
Raw provider images only; no image editing, texture application or map source changes.
"""
import math,urllib.request,json,time
from run import ROOT,read,save,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-op-paired-coverage-cause-20261009'
def main():
 rows=read(DOC/'causal-diagnostics.json.gz')['rows'];out=[];zoom=20;n=2**zoom
 for r in rows:
  lon=r['gps']['longitude'];lat=r['gps']['latitude'];x=(lon+180)/360*n;y=(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n;ix=int(x);iy=int(y);DIR=DOC/r['uid'].split('/')[1].replace(':','-')/'provider-imagery';DIR.mkdir(parents=True,exist_ok=True)
  tiles=[]
  # Two-by-two around the centre covers~70m and the complete20m sources.
  xs=[ix-1,ix] if x-ix<.5 else [ix,ix+1];ys=[iy-1,iy] if y-iy<.5 else [iy,iy+1]
  for tx in xs:
   for ty in ys:
    url=f'https://mapapi.geodata.gov.hk/gs/api/v1.0.0/xyz/imagery/WGS84/{zoom}/{tx}/{ty}.png';req=urllib.request.Request(url,headers={'User-Agent':'HK-Sandbox-bounded-source-research/1.0'})
    with urllib.request.urlopen(req,timeout=30) as res:raw=res.read();headers=dict(res.headers);assert res.status==200 and raw.startswith(b'\x89PNG')
    p=DIR/f'{zoom}-{tx}-{ty}.png';p.write_bytes(raw);item={'url':url,'path':str(p.relative_to(ROOT)),'sha256':digest(raw),'bytes':len(raw),'headers':{k:v for k,v in headers.items() if k.lower() in ['date','etag','last-modified','content-type']},'z':zoom,'x':tx,'y':ty,'copyright':'Aerial Photograph from Lands Department; © Government of Hong Kong SAR','qualification':'Original provider tile retained without alteration. Provider imagerydate is not asserted by HTTPdate; image cannot justify submetre survey precision or ownership.'};save(p.with_suffix('.receipt.json'),item);tiles.append(item);time.sleep(.2)
  out.append({'uid':r['uid'],'gps':r['gps'],'centrePixelInTile':[(x-ix)*256,(y-iy)*256],'centreTile':[zoom,ix,iy],'tiles':tiles,'providerDocs':'https://portal.csdi.gov.hk/csdi-webpage/apidoc/ImageryMapAPI','officialSiteView':'https://www.map.gov.hk/gm/map/s/wgs84/'+str(lat)+'/'+str(lon)+'?lg=en'})
 save(DOC/'primary-imagery-receipts.json',{'rows':out,'qualification':'Eight bounded original government imagery API tiles for actual-site visual interpretation only; no texture import, tracing or model/image alteration.'});print(json.dumps([{'uid':r['uid'],'tiles':len(r['tiles']),'centreTile':r['centreTile'],'pixel':r['centrePixelInTile']} for r in out]),flush=True)
if __name__=='__main__':main()
