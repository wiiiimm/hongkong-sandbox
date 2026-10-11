"""Bounded Ting Kau source acquisition via the existing filtered range downloader."""
import argparse,importlib.util,json,pathlib,shutil
HERE=pathlib.Path(__file__).resolve().parent
BOUNDS=[825850,824200,826800,825550]
def fetch(folder='sources',prefixes=None,tiles=None,individual=False):
 spec=importlib.util.spec_from_file_location('shared_fetch',HERE.parent/'mui-wo-models/fetch.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 target=HERE if folder=='sources' else HERE/folder;target.mkdir(exist_ok=True,parents=True)
 index=HERE/('individual-index.json' if individual else 'index.json')
 if target!=HERE:shutil.copyfile(index,target/'index.json')
 data=json.loads(index.read_text());selected=tiles or [f['attributes']['SHEETNO'] for f in data['features']]
 m.fetch_tiles(here=target,tiles=selected,member_prefixes=prefixes or ['INFRASTRUCTURE/'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--folder',default='sources');p.add_argument('--prefix',action='append');p.add_argument('--tile',action='append');p.add_argument('--individual',action='store_true');a=p.parse_args();fetch(a.folder,a.prefix,a.tile,a.individual)
