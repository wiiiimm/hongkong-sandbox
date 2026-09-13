"""Conservative direct-original import policy; no architectural generation or visual-quality scoring."""
import math
POLICY='original-government-import-v1'

def reasons(row, metric, profile):
    found=[]
    if row['state']!='runtime-validated-awaiting-acceptance': return ['prior-validation-held']
    if metric.get('error'): return ['detailed-check-error']
    if not metric.get('sourcePreserved') or metric.get('sourceSHA256')!=row['sourceSHA256']: found.append('source-integrity')
    values=['minSurfaceGap','minLowGap','maxLowGap','maxSamplerDelta']
    if any(not isinstance(metric.get(k),(int,float)) or not math.isfinite(metric[k]) for k in values): return found+['incomplete-contact-check']
    if metric.get('missingTerrain') or not metric.get('lowRimChecks'): found.append('terrain-coverage')
    if metric['minSurfaceGap']<-.5: found.append('terrain-intersects-source-over-0.5m')
    if metric['maxLowGap']>1 or metric['minLowGap']>.1: found.append('ground-contact-unresolved')
    if metric['maxSamplerDelta']>.004: found.append('sampler-rendered-terrain-disagreement')
    if metric['identity']['overlap']<.98 or metric['identity']['centroidDistance']>1: found.append('strict-identity-fit')
    if any(metric['budget'][k]>profile[k] for k in ('triangles','geometryBytes','residentBytes')): found.append('mobile-runtime-budget')
    return found
