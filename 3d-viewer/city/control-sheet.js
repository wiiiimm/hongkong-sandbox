/** Presentation only: keep the original control elements and their state alive.
 * The sheet is non-modal: the city and its mode dock remain available.
 */
export function createControlSheet({onExpand=()=>{},focusMap=()=>{},document:doc=globalThis.document,window:win=globalThis.window}={}){
 const sheet=doc.getElementById('explorer'),content=doc.getElementById('control-content'),handle=doc.getElementById('sheet-handle'),toggle=doc.getElementById('panel-toggle');
 const tabs=[...sheet.querySelectorAll('[data-panel]')],media=win.matchMedia('(max-width: 760px)'),viewport=win.visualViewport;
 let expanded=!media.matches,panel=tabs.find(t=>t.getAttribute('aria-selected')==='true')?.dataset.panel||'places',disposed=false,gesture=null,ignoreClick=false;
 const cleanups=[],scrollPositions=new Map();
 const listen=(target,type,handler,options)=>{target.addEventListener(type,handler,options);cleanups.push(()=>target.removeEventListener(type,handler,options));};
 function size(){
  const height=viewport?.height||win.innerHeight,inset=viewport?Math.max(0,win.innerHeight-height-viewport.offsetTop):0;
  doc.documentElement.style.setProperty('--control-viewport-height',`${height}px`);
  doc.documentElement.style.setProperty('--control-keyboard-inset',`${media.matches?inset:0}px`);
  doc.body.classList.toggle('control-keyboard',media.matches&&inset>120);
 }
 function render(){
  sheet.classList.toggle('open',expanded);sheet.dataset.panel=panel;sheet.dataset.expanded=String(expanded);
  sheet.hidden=!media.matches&&!expanded;content.hidden=!expanded;content.inert=!expanded;
  doc.body.classList.toggle('controls-expanded',expanded);doc.body.classList.toggle('controls-mobile',media.matches);
  handle.setAttribute('aria-expanded',String(expanded));toggle.setAttribute('aria-expanded',String(expanded));
  handle.setAttribute('aria-label',expanded?(media.matches?'Collapse city controls':'Close city controls'):'Expand city controls');
  toggle.setAttribute('aria-label',expanded?'Close city controls':'Open city controls');
  handle.querySelector('.sheet-action').textContent=expanded?(media.matches?'⌄':'×'):'⌃';
  for(const tab of tabs){const active=tab.dataset.panel===panel;tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1;doc.getElementById('panel-'+tab.dataset.panel).hidden=!active;}
 }
 function selectPanel(name,{expand=true,focus=false}={}){
  if(disposed||!tabs.some(t=>t.dataset.panel===name))return;
  if(name!==panel){scrollPositions.set(panel,content.scrollTop);panel=name;render();content.scrollTop=scrollPositions.get(panel)||0;}
  if(expand)open();else render();
  if(focus)tabs.find(t=>t.dataset.panel===panel).focus({preventScroll:true});
 }
 function open(name,{focusSearch=false}={}){
  if(disposed)return;if(name)selectPanel(name,{expand:false});
  const changed=!expanded;expanded=true;render();if(changed)onExpand();
  if(focusSearch){selectPanel('places',{expand:false});content.scrollTop=0;doc.getElementById('search').focus({preventScroll:true});}
 }
 function close({restoreFocus=true}={}){
  if(disposed)return;const inside=sheet.contains(doc.activeElement);expanded=false;render();
  if(restoreFocus&&inside)(media.matches?tabs.find(t=>t.dataset.panel===panel):toggle).focus({preventScroll:true});
  else if(inside&&!restoreFocus)focusMap();
 }
 function flip(){if(expanded)close();else open();}
 // Keep keyboard operations within controls out of the game's movement keys.
 // Native buttons, sliders and inputs still receive their default behaviour.
 listen(sheet,'keydown',event=>event.stopPropagation());
 listen(toggle,'click',flip);
 listen(handle,'click',()=>{if(ignoreClick){ignoreClick=false;return;}flip();});
 for(const tab of tabs){
  listen(tab,'click',()=>selectPanel(tab.dataset.panel));
  listen(tab,'keydown',event=>{
   let index=tabs.indexOf(tab);if(event.key==='ArrowRight')index=(index+1)%tabs.length;else if(event.key==='ArrowLeft')index=(index+tabs.length-1)%tabs.length;else if(event.key==='Home')index=0;else if(event.key==='End')index=tabs.length-1;else return;
   event.preventDefault();selectPanel(tabs[index].dataset.panel,{focus:true});
  });
 }
 // Escape closes controls before the game's own Escape action. Dialogs retain
 // their native Escape behaviour; no focus trap prevents interaction with map.
 listen(doc,'keydown',event=>{if(event.key!=='Escape'||!expanded||doc.querySelector('dialog[open]'))return;event.preventDefault();event.stopImmediatePropagation();close();},true);
 listen(handle,'pointerdown',event=>{if(!media.matches||gesture||event.button!==0)return;gesture={id:event.pointerId,y:event.clientY};ignoreClick=false;handle.setPointerCapture?.(event.pointerId);});
 listen(handle,'pointerup',event=>{if(gesture?.id!==event.pointerId)return;const dy=event.clientY-gesture.y;gesture=null;if(Math.abs(dy)>=36){ignoreClick=true;if(dy<0)open();else close();}});
 listen(handle,'pointercancel',event=>{if(gesture?.id===event.pointerId)gesture=null;});
 listen(media,'change',()=>{gesture=null;render();size();});
 if(viewport){listen(viewport,'resize',size);listen(viewport,'scroll',size);}listen(win,'resize',size);
 render();size();
 return {open,close,toggle:flip,selectPanel,get state(){return {expanded,panel,mobile:media.matches,disposed};},dispose(){if(disposed)return;disposed=true;gesture=null;for(const cleanup of cleanups)cleanup();doc.body.classList.remove('controls-expanded','controls-mobile','control-keyboard');doc.documentElement.style.removeProperty('--control-viewport-height');doc.documentElement.style.removeProperty('--control-keyboard-inset');}};
}
