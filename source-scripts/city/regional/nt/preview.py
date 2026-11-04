"""Generate a native SVG geographic QA overview from the actual NT export and DTM."""
import collections,html,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'docs/astra-city/regional/nt'
data=json.loads((ROOT/'3d-viewer/city/data/regional/nt.json').read_text());dem=json.loads((ROOT/'3d-viewer/city/data/terrain.json').read_text());g=dem['meta']['georef'];w=dem['w']
places=data['places'];x0=min(p['target'][0] for p in places)-2300;x1=max(p['target'][0] for p in places)+2600;z0=min(p['target'][2] for p in places)-2300;z1=max(p['target'][2] for p in places)+2300
scale=min(1170/(x1-x0),680/(z1-z0));W,H=1280,820
pos=lambda x,z:((x-x0)*scale+55,(z-z0)*scale+82)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="1280" height="820" fill="#ecf3f3"/>','<text x="40" y="34" fill="#173943" font-family="sans-serif" font-size="22">New Territories · sourced section arrivals and mapped surfaces</text>','<text x="40" y="57" fill="#45616a" font-family="sans-serif" font-size="13">Geographic QA overview · existing sampled DTM · section labels are browsing associations, not district boundaries</text>']
for row in range(0,dem['h'],6):
 start=None
 for col in range(0,w+6,6):
  land=col<w and dem['elev'][row*w+col]>0
  if land and start is None:start=col
  if not land and start is not None:
   a,b=pos(g['aE']*start+g['bE']-834500,816500-(g['aN']*row+g['bN']));c,d=pos(g['aE']*min(col,w)+g['bE']-834500,816500-(g['aN']*(row+6)+g['bN']))
   if c>30 and a<1250 and d>75 and b<770:svg.append(f'<rect x="{max(30,a):.1f}" y="{max(75,b):.1f}" width="{max(0,min(1250,c)-max(30,a)):.1f}" height="{max(0,min(770,d)-max(75,b)):.1f}" fill="#d1ddc9"/>')
   start=None
colours={'pier':'#b18b61','beach':'#d8b864','plaza':'#8b8492','pitch':'#488d83'}
for surface in data['surfaces']:
 points=' '.join(','.join(f'{v:.1f}' for v in pos(x,z)) for x,z in surface['rings'][0]);svg.append(f'<polygon points="{points}" fill="{colours[surface["kind"]]}" opacity=".85"/>')
seen=set()
for place in places:
 x,y=pos(place['target'][0],place['target'][2]);colour='#b35646' if place.get('aerialOnly') else '#176b69';title=html.escape(place['sectionId']+' '+place['title'])
 svg.append(f'<g><title>{title}</title><circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="{colour}" stroke="white" stroke-width="1.2"/>')
 if place['sectionId'] not in seen:
  svg.append(f'<text x="{x+6:.1f}" y="{y-5:.1f}" font-family="sans-serif" font-size="10" fill="#183942" stroke="white" stroke-width="2.5" paint-order="stroke">{place["sectionId"]}</text>');seen.add(place['sectionId'])
 svg.append('</g>')
svg+=['<rect x="30" y="777" width="1220" height="33" rx="6" fill="#ffffff"/>','<circle cx="47" cy="793" r="4" fill="#176b69"/><text x="58" y="797" font-family="sans-serif" font-size="12" fill="#183942">Checked walking arrival</text>','<circle cx="252" cy="793" r="4" fill="#b35646"/><text x="263" y="797" font-family="sans-serif" font-size="12" fill="#183942">Aerial only</text>','<text x="395" y="797" font-family="sans-serif" font-size="12" fill="#183942">Geometry: OpenStreetMap contributors · ODbL 1.0 | Terrain: existing Lands Department DTM</text>','</svg>']
(OUT/'overview.svg').write_text('\n'.join(svg)+'\n')
