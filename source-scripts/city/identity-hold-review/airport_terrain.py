"""Bounded source-terrain acquisition reusing the pinned selective ZIP downloader."""
import pathlib,json,sys,gzip,argparse
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/identity-hold-review'
sys.path.insert(0,str(ROOT/'source-scripts/city/landmark-acquisition'));import acquire as a;import terrain as t
parser=argparse.ArgumentParser();parser.add_argument('--sheet',choices=['9-NE-18B','9-NE-18C','9-NE-18D'],default='9-NE-18D');sheet=parser.parse_args().sheet
original=ROOT/'source-scripts/city/landmark-acquisition/sources'/sheet;infos,proof=a.parse_directory((original/'zip-directory.bin').read_bytes());members={i.filename:{'headerOffset':i.header_offset,'crc32':i.CRC,'compressedBytes':i.compress_size,'decodedBytes':i.file_size}for i in infos if i.filename.startswith('TERRAIN')and i.filename.endswith(('.gltf','.bin'))};assert len(members)==2
folder=HERE/('airport-terrain' if sheet=='9-NE-18D' else 'airport-terrain-'+sheet.lower());folder.mkdir(exist_ok=True);a.HERE=folder
pin={'sourceDirectorySHA256':a.sha((original/'zip-directory.bin').read_bytes()),'members':members,'capBytes':3000000,'uid':'landsd/314191:0','sourceDownload':str((original/'download.json').relative_to(ROOT))}
p=folder/'input.json'
if p.exists():assert a.read(p)==pin
else:a.write(p,pin)
official=folder/'official-selection.json.gz'
if not official.exists():official.write_bytes(gzip.compress(json.dumps({'datasetVersion':'Exact native terrain only; no building matches','features':[]}).encode(),mtime=0))
network=a.Network(folder/'transfer-ledger.json',cap=pin['capBytes']);download=a.read(original/'download.json');state=a.acquire_tile(network,sheet,{'attributes':download['indexAttributes'],'uids':[]},{},a.retained_caches(),exact_members=members);verified=t.verify_sheet(sheet);a.write(DOC/('airport-terrain-acquisition'+('' if sheet=='9-NE-18D' else '-'+sheet.lower())+'.json'),{'verification':verified,'pin':pin,'receivedBytes':network.data['receivedBytes'],'staged':True,'published':False});print(json.dumps(verified))
