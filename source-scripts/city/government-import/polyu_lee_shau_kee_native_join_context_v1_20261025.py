"""Summarise existing exact original library interfaces, without geometry edits or approval."""
from pathlib import Path
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-polyu-lee-shau-kee-native-join-context-v1-20261025'
NATIVE='government-xl-after-tvb-next-three-with-companions-native-contacts-v1-20261025'
IDENTITY='government-xl-polyu-lee-shau-kee-bounded-identity-panel-review-v1-20261025'
UIDS=['landsd/305600:0','landsd/257998:0'];LIB='landsd/305793:0'


def main():
 out=BASE/BATCH;assert not out.exists();pins={};refs=[Path(__file__)]
 def take(n,file):
  if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  p=BASE/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 identity=take(IDENTITY,'ROOT-IDENTITY-PANEL-CONTEXT.json');native=take(NATIVE,'summary.json')
 assert identity['identityAccepted']and identity['retainedLibraryPublicationHoldUnchanged']
 rows=[];plotrows=[]
 for uid in UIDS:
  expected=next(r for r in native['rows']if r['uid']==uid and r['nativeUid']==LIB)
  assert expected['sourceSHA256']==identity['sourceSHA256ByUid'][uid]
  for mode in ['original','literal','leftF32','balancedF32']:
   d=take(NATIVE,uid.split('/')[1]+'--305793:0--'+mode+'.json.gz')
   assert d['allPairsExamined']and d['sourceFacesOmitted']==0 and d['geometryChanges']==0
   contacts=d['contacts'];raw=next(r for r in expected['modes']if r['mode']==mode)
   assert len(contacts)==raw['finiteContactPairs']and not raw['areaContactPairs']
   points=np.asarray([[float(Fraction(v))for v in p]for c in contacts for p in c['exactPoints']]).reshape(-1,3)
   bounds=[points.min(0).tolist(),points.max(0).tolist()]if len(points)else None
   if bounds:assert bounds[0][1]>=12.1515 and bounds[1][1]<=15.7300
   rows.append(dict(uid=uid,mode=mode,rawContactMetrics=raw,contactWitnessBounds=bounds,sourceFacesWithContact=len({r['sourceFaceA']for r in contacts}),zeroAreaContactPairs=True))
   if mode=='leftF32':plotrows.append((uid,points))
 out.mkdir(parents=True)
 fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
 for uid,points in plotrows:
  if len(points):
   axes[0].scatter(points[:,0],-points[:,2],s=4,label=uid)
   axes[1].scatter(points[:,0],points[:,1],s=4,label=uid)
 axes[0].set(xlabel='Local easting (m)',ylabel='Local northing (m)',title='Exact original interface witnesses (float32 stream)');axes[0].axis('equal')
 axes[1].set(xlabel='Local easting (m)',ylabel='HKPD elevation (m)',title='All contacts remain in the original low campus interface',ylim=(8,22))
 for ax in axes:ax.legend();ax.grid(alpha=.2)
 figure=out/'exact-original-library-interface-witnesses.png';fig.savefig(figure,dpi=160);plt.close(fig)
 result=dict(uids=UIDS,sourceSHA256ByUid=identity['sourceSHA256ByUid'],retainedNativeUid=LIB,retainedNativeSHA256=expected['nativeSHA256'],rows=rows,rawAllFourWorldContactProofsRetained=True,nativeMetadataChanges=0,sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Existing exact finite original/native contacts are reported, including all float32 contacts. All witnesses lie at the low campus interface between12.1515and15.7300m HKPD; no area contacts were found. This does not assert zero interpenetration, approve a library hold, infer a main-to-library support, or edit a source.')
 save(out/'summary.json',result);refs.append(figure)
 module('polyu_join_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-library-interface-contact-context',refs,result)


if __name__=='__main__':main()
