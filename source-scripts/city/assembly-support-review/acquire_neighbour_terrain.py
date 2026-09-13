"""Fill the HKDI terrain rectangle with bounded neighbouring native source sheets."""
import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('a',ROOT/'source-scripts/city/landmark-acquisition/acquire.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);index=a.read(a.HERE/'index.json');a.HERE=HERE/'native-terrain-extra';network=a.Network(a.HERE/'neighbour-transfer-ledger.json',cap=20_000_000);caches=a.retained_caches();out=[]
for sheet in ['11-NE-25A','11-NE-25B','11-NE-25D']:
 attrs=next(f['attributes'] for f in index['features'] if f['attributes']['SHEETNO']==sheet);tile={'attributes':attrs,'uids':[]};a.acquire_tile(network,sheet,tile,{},caches,exact_members={});infos,_=a.parse_directory((a.HERE/'sources'/sheet/'zip-directory.bin').read_bytes());chosen={e.filename:{'headerOffset':e.header_offset,'crc32':e.CRC,'compressedBytes':e.compress_size,'decodedBytes':e.file_size} for e in infos if e.filename.startswith('TERRAIN') and e.filename.endswith(('.gltf','.bin'))};assert chosen;result=a.acquire_tile(network,sheet,tile,{},caches,exact_members=chosen);out.append(result);print(sheet,'terrain',bool(a.read(ROOT/result['manifest']).get('terrain')),flush=True)
(ROOT/'docs/astra-city/assembly-support-review/neighbour-terrain-acquisition.json').write_text(json.dumps({'parts':out,'receivedBytes':network.data['receivedBytes']},indent=2)+'\n')
