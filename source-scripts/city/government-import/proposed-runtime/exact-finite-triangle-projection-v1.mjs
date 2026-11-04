/** Filtered exact dyadic orientation of the actual Float32 drawn XZ triangle.
 * No negative barycentric tolerance; fallback performs exact BigInt arithmetic
 * only for numerically uncertain signs. Geometry/height/source bytes unchanged.
 */
const view=new DataView(new ArrayBuffer(8));
function dyadic(value){if(!Number.isFinite(value))throw new Error('Non-finite projection coordinate');view.setFloat64(0,value,false);const bits=view.getBigUint64(0,false),negative=(bits>>63n)!==0n,exponent=Number((bits>>52n)&2047n),fraction=bits&((1n<<52n)-1n);const n=exponent?fraction+(1n<<52n):fraction;return{n:negative?-n:n,e:exponent?exponent-1023-52:-1074};}
function exact(a,b,p){const values=[...a,...b,...p].map(dyadic),emin=Math.min(...values.filter(v=>v.n!==0n).map(v=>v.e),0),q=values.map(v=>v.n<<BigInt(v.e-emin)),[ax,az,bx,bz,px,pz]=q,d=(bx-ax)*(pz-az)-(bz-az)*(px-ax);return d<0n?-1:d>0n?1:0;}
export function orientationSign(a,b,p){const left=(b[0]-a[0])*(p[1]-a[1]),right=(b[1]-a[1])*(p[0]-a[0]),det=left-right,error=16*Number.EPSILON*(Math.abs(left)+Math.abs(right));return Math.abs(det)>error?(det<0?-1:1):exact(a,b,p);}
export function withinFiniteTriangleProjection(a,b,c,p){const direction=orientationSign(a,b,c);return direction!==0&&orientationSign(a,b,p)*direction>=0&&orientationSign(b,c,p)*direction>=0&&orientationSign(c,a,p)*direction>=0;}
