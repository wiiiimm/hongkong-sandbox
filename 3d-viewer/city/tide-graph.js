// Display the original ±12 h tide window using its hourly prediction samples.
// Missing hours break the line; interpolated space is not an observed tide trace.
const HOUR=3600000;
const timestamp=value=>typeof value==='number'?value:Date.parse(value);
export function tidePlot(prediction){
 const now=timestamp(prediction?.time),lo=now-12*HOUR,hi=now+12*HOUR;
 if(!Number.isFinite(now)||!Array.isArray(prediction?.series))return null;
 const points=prediction.series.map(p=>({time:timestamp(p.time),height:p.heightHKPD})).filter(p=>Number.isFinite(p.time)).sort((a,b)=>a.time-b.time);
 const near=points.filter(p=>p.time>=lo-HOUR&&p.time<=hi+HOUR),valid=near.filter(p=>Number.isFinite(p.height));
 if(valid.length<2)return null;
 const min=Math.min(...valid.map(p=>p.height)),max=Math.max(...valid.map(p=>p.height)),range=Math.max(.2,max-min),bottom=min-range*.18,top=max+range*.18;
 const x=time=>6+(time-lo)/(hi-lo)*252,y=height=>64-(height-bottom)/(top-bottom)*54;
 let path='',previous=null;
 for(const p of near){if(!Number.isFinite(p.height)){previous=null;continue;}const join=previous&&p.time-previous.time<=HOUR*1.01;path+=`${join?'L':'M'}${x(p.time).toFixed(2)},${y(p.height).toFixed(2)} `;previous=p;}
 return {path:path.trim(),min,max,markerX:x(now),markerY:Number.isFinite(prediction.heightHKPD)?y(prediction.heightHKPD):null};
}
export function drawTideGraph(svg,prediction){
 const plot=tidePlot(prediction);svg.toggleAttribute('hidden',!plot);if(!plot){svg.replaceChildren();return;}
 const make=(tag,attrs,text)=>{const node=svg.ownerDocument.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))node.setAttribute(k,String(v));if(text!==undefined)node.textContent=text;return node;};
 const clip=make('clipPath',{id:'tide-plot-clip'});clip.append(make('rect',{x:6,y:4,width:252,height:65}));const defs=make('defs',{});defs.append(clip);
 const curve=make('path',{d:plot.path,fill:'none',stroke:'currentColor','stroke-width':1.8,'stroke-linejoin':'round','clip-path':'url(#tide-plot-clip)'});
 const children=[defs,curve,make('path',{d:'M132 5V67',fill:'none',stroke:'currentColor','stroke-width':1,opacity:.5})];
 if(plot.markerY!==null)children.push(make('circle',{cx:plot.markerX,cy:plot.markerY,r:2.7,fill:'currentColor'}));
 for(const [x,anchor,text] of [[6,'start','−12h'],[132,'middle','Now'],[258,'end','+12h']])children.push(make('text',{x,y:83,'text-anchor':anchor,'font-size':9,fill:'currentColor'},text));
 children.push(make('text',{x:258,y:11,'text-anchor':'end','font-size':9,fill:'currentColor'},`${plot.max.toFixed(2)} m HKPD`));svg.replaceChildren(...children);
 svg.setAttribute('aria-label',`24-hour astronomical tide prediction, ${plot.min.toFixed(2)} to ${plot.max.toFixed(2)} metres above Hong Kong Principal Datum.`);
}
