"""Conservative, visibly estimated fallback heights; mapped dimensions always win.
Only the derived dataset changes. See height-rules.json and the coverage notes.
"""
import json,pathlib
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
from build_city import xy,coords,number
RULES=json.loads(pathlib.Path(__file__).with_name('height-rules.json').read_text())

def make_height_estimator(elements):
 rule=RULES['tai-o-small-village'];s,w,n,e=rule['bbox'];extent=Polygon([xy(w,s),xy(e,s),xy(e,n),xy(w,n)])
 streets=[];street_ids=[]
 for oid,el in elements.items():
  t=el.get('tags',{})
  if t.get('highway') and t.get('name:en',t.get('name','')) in rule['streets'] and el.get('geometry'):
   line=LineString(coords(el['geometry']))
   if line.intersects(extent):streets.append(line.buffer(rule['streetBuffer']));street_ids.append(oid)
 corridor=unary_union(streets).intersection(extent)
 if not streets:raise ValueError('Tai O height estimate requires its retained named street geometry')
 def estimate(tags,polygon,kind,minimum):
  if number(tags.get('height')):return number(tags['height']),None
  levels=number(tags.get('building:levels',tags.get('building:part:levels')))
  if levels:return levels*3.2,None
  # Elevated/partial buildings retain the previous neutral default, avoiding the
  # accidental loss of a form whose mapped minimum exceeds a low-rise estimate.
  simple=minimum==0 and not tags.get('building:part')
  if simple:
   for key in ['house-type','bungalow-type']:
    if kind in RULES[key]['types']:return RULES[key]['height'],key
   explicit_other_use=any(tags.get(k) not in (None,'no') for k in ['amenity','shop','office','tourism','leisure','historic','religion','industrial','craft','power','man_made','emergency','military'])
   current_use=tags.get('building:use')
   if kind in ('yes','residential') and current_use in (None,'residential') and not explicit_other_use and polygon.area<=rule['maximumFootprint'] and extent.covers(polygon.representative_point()) and corridor.intersection(polygon).area>=polygon.area*rule['minimumOverlap']:
    return rule['height'],'tai-o-small-village'
  return (9 if polygon.area>8000 else 6 if kind in ('service','shed','garage','garages') else 24),None
 return estimate,{'rules':RULES,'taiOStreetFeatures':sorted(street_ids),'policy':'All corrected forms remain heightSource=estimated. Tagged heights and level-derived heights always take precedence. No buildings or floors are invented.'}
