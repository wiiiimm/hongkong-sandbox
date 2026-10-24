import assert from 'node:assert/strict';

// Clip the actual 3D face to four vertical half-spaces. Y is interpolated on
// original edges; vertical faces are retained rather than height-indexed away.
export function clipParentTriangle(face, bounds) {
  assert.equal(face.length, 3);
  assert(face.every(p => p.length === 3 && p.every(Number.isFinite)));
  const [x0, z0, x1, z1] = bounds;
  assert(x0 < x1 && z0 < z1);
  const planes = [[0,x0,1],[0,x1,-1],[2,z0,1],[2,z1,-1]];
  if (face.every(p => planes.every(([axis,bound,sign]) => sign*(p[axis]-bound)>=0))) return [face];
  let polygon = face;
  for (const [axis,bound,sign] of planes) {
    const output = [];
    for (let i=0; i<polygon.length; i++) {
      const a=polygon[i], b=polygon[(i+1)%polygon.length];
      const insideA=sign*(a[axis]-bound)>=0, insideB=sign*(b[axis]-bound)>=0;
      if (insideA) output.push(a);
      if (insideA!==insideB) {
        const t=(bound-a[axis])/(b[axis]-a[axis]);
        assert(t>=0 && t<=1);
        const p=a.map((v,j)=>v+(b[j]-v)*t);
        p[axis]=bound;
        output.push(p);
      }
    }
    polygon=output.filter((p,i)=>i===0 || p.some((v,j)=>v!==output[i-1][j]));
    if(polygon.length>1 && polygon[0].every((v,j)=>v===polygon.at(-1)[j]))polygon.pop();
    if(polygon.length<3)return [];
  }
  assert(polygon.every(p=>p.every(Number.isFinite)&&planes.every(([axis,bound,sign])=>sign*(p[axis]-bound)>=0)));
  return polygon.slice(1,-1).map((p,i)=>[polygon[0],p,polygon[i+2]]);
}
