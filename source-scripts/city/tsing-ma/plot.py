"""CPU-only source model/shoreline inspection; does not modify rendered assets."""
import json,pathlib,numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/tsing-ma'
data=json.loads((HERE/'bridges-tsing-ma.json').read_text());water=json.loads((HERE/'hydro-tsing-ma.json').read_text());fig,(plan,elevation)=plt.subplots(2,1,figsize=(18,9),layout='constrained')
plan.set_facecolor('#d9e7d1')
for p in water['water']:
 for i,r in enumerate(p['rings']):plan.fill(np.array(r)[:,0],np.array(r)[:,1],color='#add3dd' if not i else '#d9e7d1',zorder=1)
for m in data['models']:
 t=np.array(m['modelGeometry']['position']).reshape(-1,3,3);c='#6d7885' if '/I' in m['id'] else '#d06d3a'
 plan.add_collection(PolyCollection(t[:,:,[0,2]],facecolors=c,edgecolors='none',alpha=.6,zorder=2));elevation.add_collection(PolyCollection(t[:,:,[0,1]],facecolors=c,edgecolors='none',alpha=.6))
plan.set_xlim(-10060,-7870);plan.set_ylim(-7410,-6610);plan.invert_yaxis();plan.set_aspect('equal');plan.set_title('Verified original LandsD bridge components + mapped land/water (plan)')
elevation.set_xlim(-10060,-7870);elevation.set_ylim(-5,220);elevation.set_aspect('equal');elevation.set_title('Original source geometry (east/height projection): four tower legs + two decks; no high cables in source');elevation.set_ylabel('Metres HKPD');elevation.set_xlabel('City easting / metres');elevation.axhline(.3,color='#448ca0',linewidth=.7)
for ax in [plan,elevation]:ax.ticklabel_format(useOffset=False)
fig.savefig(DOC/'source-bridge-plan-elevation-2700x1350.png',dpi=150)

# A distinct illustration preserves the source-only figure above.
c=json.loads((HERE/'cables-tsing-ma.json').read_text())
for part in c['parts']:
 p=np.array(part['path']);elevation.plot(p[:,0],p[:,1],color='#34475b',linewidth=1 if part['role']=='main-cable' else .35)
elevation.set_title('Same source components + separately labelled illustrative main cables/hangers (backstays unverified)')
fig.savefig(DOC/'bridge-with-illustrative-main-cables-2700x1350.png',dpi=150)
