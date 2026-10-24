"""Resolve only the coarse global-bottom warning with complete source evidence."""
import math

def resolve_global_bottom_warning(validation_row, metric, foundation_row):
    warning = 'sampled-terrain-above-model-bottom'
    concerns = list(validation_row.get('concerns', []))
    same_source = (validation_row.get('uid') == metric.get('uid') == foundation_row.get('uid')
                   and metric.get('sourceSHA256') == foundation_row.get('sourceSHA256')
                   and bool(metric.get('sourceSHA256')))
    numeric = all(isinstance(metric.get(k), (int, float)) and math.isfinite(metric[k])
                  for k in ('minSurfaceGap', 'minLowGap', 'maxLowGap', 'maxSamplerDelta'))
    full = foundation_row.get('foundation', {})
    complete = (full.get('triangles', 0) > 0
                and full.get('completeTerrainTriangles') == full.get('triangles')
                and full.get('fullyBuriedUpwardTriangles') == 0
                and full.get('fullyBuriedAreaFraction') == 0)
    passed = (same_source and numeric and complete and foundation_row.get('strictFoundationAccepted') is True
              and metric.get('sourcePreserved') is True and not metric.get('missingTerrain')
              and metric.get('lowRimChecks', 0) > 0 and metric['minSurfaceGap'] >= -.5
              and metric['minLowGap'] <= .1 and metric['maxLowGap'] <= 1
              and metric['maxSamplerDelta'] <= .004
              and validation_row.get('outcome') == 'runtime-accepted-placement-unreviewed')
    resolved = [warning] if passed and warning in concerns else []
    return {'uid': metric.get('uid'), 'sourceSHA256': metric.get('sourceSHA256'),
            'resolved': resolved, 'remaining': [c for c in concerns if c not in resolved],
            'policy': 'Global bottom versus remote footprint terrain is diagnostic only. Resolve only with same-source complete foundation and existing strict detailed contact checks. Other flags and all identity, neighbour, runtime and browser gates remain required.'}
