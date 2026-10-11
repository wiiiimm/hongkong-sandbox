"""Fresh exact two-original current physical input, no source edits."""
from run import ROOT,HERE,read,save,digest,NATIVE_RUN
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-two-original-physical-inputs-20261010'
def main():
 assert not DOC.exists();base=DOC.parent;rows=[]
 for batch in ['government-xl-tung-sing-current-full-cell-preflight-20261010','government-xl-lei-tung-current-full-cell-preflight-v2-20261010']:
  x=read(base/batch/'selection.json.gz');assert x['manifestSHA256']==digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes());row=x['rows'][0];row['triangles']=row['native']['model']['triangles'];rows.append(row)
 save(DOC/'selection.json.gz',{'rows':rows,'manifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),'nativeRun':NATIVE_RUN,'publication':False,'sourceGeometryChanges':0})
if __name__=='__main__':main()
