"""Trace inherited bridge ridge from the immutable archival DTM to city grid."""
import hashlib,json,pathlib,zipfile
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent
SOURCE=ROOT/'references/codex/hongkong-3d-model/data/hk-landsd-5m/Whole_HK_DTM_5m.zip'
if not SOURCE.exists():SOURCE=ROOT.parent/'hongkong-sandbox/references/codex/hongkong-3d-model/data/hk-landsd-5m/Whole_HK_DTM_5m.zip'
def audit():
 city=json.loads((ROOT/'3d-viewer/city/data/terrain.json').read_text());original=json.loads((ROOT/'3d-viewer/data/hk-dtm5m.json').read_text());g=city['meta']['georef'];qs=[]
 for x,z in [(-9800,-6770),(-9500,-6860),(-9250,-6940),(-9000,-7010),(-8750,-7090),(-8500,-7160),(-8250,-7240)]:
  i=round((x+834500-g['bE'])/70);j=round((816500-z-g['bN'])/-70);qs.append({'world':[x,z],'coarseColumn':i,'coarseRow':j,'coarseCityRaw':city['elev'][j*city['w']+i],'coarseOriginalRaw':original['elev'][j*city['w']+i]})
 with zipfile.ZipFile(SOURCE) as z:
  with z.open('Whole_HK_DTM_5m.asc') as f:
   header={}
   for _ in range(6):k,v=f.readline().decode().split();header[k]=float(v)
   E=header['xllcorner']+2.5;N=header['yllcorner']+(header['nrows']-.5)*5;rows={}
   need=set(r for q in qs for r in range(q['coarseRow']*14,(q['coarseRow']+1)*14))
   for row,line in enumerate(f):
    if row in need:rows[row]=np.fromstring(line.decode(),sep=' ',dtype=np.float32)
    if row>max(need):break
   for q in qs:
    i,j=q['coarseColumn'],q['coarseRow'];a=np.stack([rows[r][i*14:(i+1)*14] for r in range(j*14,(j+1)*14)]);a=np.where(a<=-100,0,a);mean=float(a.mean());q.update(native14x14Mean=mean,originalExpectedRoundedMean=int(round(mean)),sourceRawRange=[float(a.min()),float(a.max())],nativePositiveSamples=int((a>1).sum()))
    assert int(round(mean))==q['coarseOriginalRaw']==q['coarseCityRaw']
 report={'source':str(SOURCE),'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'sourceHeader':header,'inheritedGridSha256':hashlib.sha256((ROOT/'3d-viewer/data/hk-dtm5m.json').read_bytes()).hexdigest(),'cause':'The archived5m DTM contains elevated bridge surfaces. hk_dtm.py averages14x14 native samples, hk_build.py uses DTM>1m as land, build_city.py retains the resulting70m grid. NoB50Klandcover polygon creates this ridge; vegetation uses landcover separately.','pipeline':['3d-viewer/scripts/hk_dtm.py','3d-viewer/scripts/hk_build.py','source-scripts/city/build_city.py'],'samples':qs,'sourceChanged':False}
 (ROOT/'docs/astra-city/tsing-ma/terrain-source-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('All',len(qs),'source block means reproduce inherited bridge ridge.')
if __name__=='__main__':audit()
