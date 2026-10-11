"""Prove a terrain change leaves an elevated form's existing solid support unchanged."""
from shapely.geometry import Polygon

def unchanged_supports(inputs,checks,replaced):
    forms={r['building']['uid']:r for r in inputs['rows']};stats={r['uid']:r for r in checks['rows']};out=[]
    for row in checks['rows']:
        if row['uid'] in replaced or row['reasons']!=['increased-neighbour-ground-gap']:continue
        b=forms[row['uid']]['building'];foot=Polygon(b['rings'][0],b['rings'][1:]);matches=[]
        for uid,item in forms.items():
            if uid==b['uid'] or uid in replaced or item['existingNative'] or stats[uid]['reasons']:continue
            support=item['building']
            if support.get('modelGeometry') or support.get('structureType')=='Open-sided Structure':continue
            gap=b['base']+b.get('minimum',0)-support['base']-support['height']
            if abs(gap)>.1:continue
            polygon=Polygon(support['rings'][0],support['rings'][1:])
            if not polygon.buffer(.002).covers(foot) or polygon.intersection(foot).area/foot.area<.9999:continue
            matches.append({'supportUid':uid,'unchangedVerticalGap':gap,'footprintCoverage':polygon.intersection(foot).area/foot.area,'horizontalToleranceMetres':.002})
        if len(matches)==1:out.append({'uid':b['uid'],**matches[0],'reason':'Unchanged source-form roof supports the elevated source; source geometry stays fixed and supporting form passes terrain regression checks.'})
    return out
