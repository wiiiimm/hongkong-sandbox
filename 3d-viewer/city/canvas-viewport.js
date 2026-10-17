/** CSS importance and render-pixel cost are independent of device/model budgets. */
export function canvasDimensions(width,height,dpr=1,{maxDpr=1.5,maxPixels=4000000}={}){
 width=Math.max(0,Number(width)||0);height=Math.max(0,Number(height)||0);
 const pixelRatio=Math.min(Math.max(.25,Number(dpr)||1),maxDpr,Math.sqrt(maxPixels/Math.max(1,width*height)));
 return {width,height,pixelRatio,active:width>0&&height>0,bufferWidth:Math.floor(width*pixelRatio),bufferHeight:Math.floor(height*pixelRatio)};
}
/** Coalesces container, zoom and DPR events without touching model caches. */
export function observeCanvasViewport(container,onChange){
 let frame=0,last='',media,intersects=true;
 const schedule=()=>{if(document.hidden){if(frame)cancelAnimationFrame(frame);update();}else if(!frame)frame=requestAnimationFrame(update);};
 const watchDpr=()=>{media?.removeEventListener('change',dprChanged);media=matchMedia(`(resolution: ${devicePixelRatio}dppx)`);media.addEventListener('change',dprChanged);};
 const dprChanged=()=>{watchDpr();schedule();};
 function update(){frame=0;const rect=container.getBoundingClientRect(),state=canvasDimensions(rect.width,rect.height,devicePixelRatio);state.active=state.active&&!document.hidden&&intersects&&getComputedStyle(container).visibility!=='hidden';const key=JSON.stringify(state);if(key!==last){last=key;onChange(state);}}
 const intersection=new IntersectionObserver(entries=>{intersects=entries[0].isIntersecting;schedule();});intersection.observe(container);
 const mutation=new MutationObserver(schedule);for(let el=container;el;el=el.parentElement)mutation.observe(el,{attributes:true,attributeFilter:['style','class','hidden']});document.addEventListener('visibilitychange',schedule);
 const observer=new ResizeObserver(schedule);observer.observe(container);watchDpr();addEventListener('resize',schedule);document.addEventListener('fullscreenchange',schedule);globalThis.visualViewport?.addEventListener('resize',schedule);schedule();
 return ()=>{observer.disconnect();intersection.disconnect();mutation.disconnect();document.removeEventListener('visibilitychange',schedule);cancelAnimationFrame(frame);media?.removeEventListener('change',dprChanged);removeEventListener('resize',schedule);document.removeEventListener('fullscreenchange',schedule);globalThis.visualViewport?.removeEventListener('resize',schedule);};
}
