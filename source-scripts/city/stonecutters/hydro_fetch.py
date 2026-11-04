"""Reuse original retained map archives before requesting missing sheets."""
import importlib.util,json,pathlib,shutil,hashlib
from fetch import HERE,BOUNDS

def fetch():
    target=HERE/'hydro-sources';target.mkdir(exist_ok=True);reuse=[]
    index=json.loads((HERE/'hydro-index.json').read_text());request=HERE/'hydro-index.request.txt';original_request=request.read_bytes()
    for f in index['features']:
        a=f['attributes'];sheet=a['SHEETNO'];dest=target/(sheet+'.zip')
        if dest.exists():continue
        for metadata in HERE.parent.glob('*/hydro-sources/'+sheet+'-download.json'):
            if HERE in metadata.parents:continue
            old=json.loads(metadata.read_text());archive=metadata.with_name(sheet+'.zip')
            if old.get('attributes',{}).get('REVISIONDATE')!=a['REVISIONDATE'] or not archive.exists():continue
            assert hashlib.sha256(archive.read_bytes()).hexdigest()==old['archiveSha256']
            shutil.copyfile(archive,dest);shutil.copyfile(metadata,target/metadata.name)
            reuse.append({'sheet':sheet,'source':str(archive.relative_to(HERE.parents[2])),'sha256':old['archiveSha256']});break
    spec=importlib.util.spec_from_file_location('shared_hydro_fetch',HERE.parent/'tsing-ma/hydro_fetch.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.HERE=HERE;m.BOUNDS=BOUNDS;m.fetch()
    request.write_bytes(original_request)
    if reuse:(HERE/'hydro-reused-sources.json').write_text(json.dumps(reuse,indent=2)+'\n')
if __name__=='__main__':fetch()
