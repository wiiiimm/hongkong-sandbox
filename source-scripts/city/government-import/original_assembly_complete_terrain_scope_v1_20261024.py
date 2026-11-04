"""Extend complete source scopes with every real form in the private terrain domain.

Adds obligations, never removes a source/named neighbour or grants acceptance.
"""
import argparse,copy
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','model-scope','terrain-scope','inventory']:p.add_argument('--'+k,required=True)
 a=p.parse_args();assert all(n.startswith('government-xl-')and '/'not in n for n in [a.batch,a.model_scope,a.terrain_scope,a.inventory])
 base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
  path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 model=take(a.model_scope,'summary.json');terrain=take(a.terrain_scope,'scope.json');forms=take(a.terrain_scope,'form-obligations.json.gz');native=take(a.terrain_scope,'native-obligations.json.gz');inventory=take(a.inventory,'complete-bounds.json.gz')
 assert set(model['uids'])==set(terrain['uids']) and not native and not terrain['touchingNativeUids'] and terrain['positiveAreaTerrainOverlaps']==0
 manifest=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifest.read_bytes());assert sha==model['currentManifestSHA256']==pins[a.terrain_scope][str(manifest.relative_to(ROOT))]==pins[a.inventory][str(manifest.relative_to(ROOT))];refs.append(manifest)
 tiles={r['id']:r['url']for r in read(manifest)['tiles']};obligations={r['uid']:r for r in forms};assert len(obligations)==len(forms)
 full=[];hashes=copy.deepcopy(model['currentFormTileHashes'])
 for uid,form in sorted(obligations.items()):
  tile=ROOT/'3d-viewer'/tiles[form['tile']];key=str(tile.relative_to(ROOT));h=digest(tile.read_bytes());assert h==inventory['currentFormTileHashes'][key]
  assert next(f for f in read(tile)['buildings']if f['uid']==uid)==form
  refs.append(tile);hashes[key]=h;full.append(dict(building=form,tile=tiles[form['tile']],tileSHA256=h))
 rows=[]
 for row in model['rows']:
  old=take(a.model_scope,row['uid'].split('/')[1]+'-forms.json.gz');assert {r['building']['uid']for r in old}<=set(obligations)
  assert row['currentNativeActorsChecked']==len(inventory['rows']) and not row['nearbyNativeActors']
  save(out/(row['uid'].split('/')[1]+'-forms.json.gz'),full)
  rows.append(dict(**row,completeTerrainDomainForms=len(full),sourceTwoMetreFormsRetained=len(old)))
 result={**model,'rows':rows,'currentFormTileHashes':hashes,'completeTerrainDomainForms':len(full),'qualification':'Every prior complete source/four-world native scope remains; adds all exact current forms from the independently checked full terrain domain. Original two-metre count remains separately labelled; no source, terrain, collision or publication approval.'}
 save(out/'summary.json',result)
 module('complete_terrain_assembly_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-source-and-terrain-domain-obligations',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
