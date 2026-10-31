"""Approximate architect-plan registration for visual interpretation, never survey/acceptance."""
import json,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'docs/astra-city/government-import'
OUT=BASE/'government-xl-west-wing26195-plan-registration-diagnostic-v1-20261017'
PLAN=BASE/'government-xl-west-wing26195-architect-site-plan-v1-20261015/site-plan.jpg'
GEO=BASE/'government-xl-west-wing26195-missing-coverage-v1-20261017/missing-components.geojson'
# Two endpoints of the long western CGO hall wall; independent stepped corners below.
controls=[dict(world=[525.247,695.986],pixel=[369,888]),dict(world=[511.547,744.8],pixel=[369,1081])]
checks=[dict(world=[526.735,749.062],pixel=[432,1081]),dict(world=[553.917,780.164],pixel=[570,1178])]
def fit(points):
 rows=[];values=[]
 for p in points:
  x,y=p['world'];u,v=p['pixel'];rows.extend([[x,-y,1,0],[y,x,0,1]]);values.extend([u,v])
 return np.linalg.lstsq(np.array(rows),values,rcond=None)[0]
a,b,tx,ty=fit(controls)
def project(x):return np.asarray(x)@np.array([[a,b],[-b,a]])+np.array([tx,ty])
for p in checks:p['predictedPixel']=project([p['world']])[0].tolist();p['residualPixels']=float(np.linalg.norm(np.array(p['pixel'])-p['predictedPixel']))
OUT.mkdir(exist_ok=False)
fig,ax=plt.subplots(figsize=(12,14),dpi=160);ax.imshow(plt.imread(PLAN))
features=json.loads(GEO.read_text())['features']
for f in features:
 coords=f['geometry']['coordinates'][0];q=project(coords);ax.add_patch(Polygon(q,facecolor='#ff3040',edgecolor='#ae0000',alpha=.45))
 if f['properties']['areaM2']>1:ax.text(*q.mean(axis=0),str(f['properties']['component']),fontsize=9,color='#600000')
for p in controls:ax.plot(*p['pixel'],'bo')
for p in checks:
 ax.plot(*p['pixel'],'go');ax.plot(*p['predictedPixel'],'gx');ax.plot([p['pixel'][0],p['predictedPixel'][0]],[p['pixel'][1],p['predictedPixel'][1]],'g-')
ax.set_title('Approximate architect-plan registration — diagnostic only\nRed: uncovered source footprint; blue: controls; green: independent checks')
ax.set_xlim(250,1150);ax.set_ylim(1400,150);fig.tight_layout();fig.savefig(OUT/'registered-missing-footprint.png');plt.close(fig)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
(OUT/'registration.json').write_text(json.dumps(dict(method='Two-point orientation-preserving similarity fit; manual approximate pixels',controlPoints=controls,independentChecks=checks,transform=[a,b,tx,ty],pixelsPerMetre=float(np.hypot(a,b)),inputs=[ref(PLAN),ref(GEO),ref(Path(__file__))],surveyPrecisionClaimed=False,identityAccepted=False,installationApproved=False,sourceGeometryChanges=0),indent=2)+'\n')
print(json.dumps(dict(checks=checks,output=str(OUT.relative_to(ROOT)))))
