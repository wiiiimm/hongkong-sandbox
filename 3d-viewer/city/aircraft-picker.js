/** Presentation only. Aircraft loading and mode-entry cancellation stay in the app. */
export function createAircraftPicker({aircraft,onSelect,onQuickFly=()=>{},onOpen=()=>{},document:doc=globalThis.document}={}){
 const panel=doc.getElementById('flight-controls'),menu=doc.getElementById('aircraft-model'),trigger=doc.getElementById('fly-toggle'),closeButton=doc.getElementById('aircraft-close');
 const cleanups=[],items=new Map();let open=false,disposed=false,current=aircraft[0].id;
 const listen=(target,type,fn,capture=false)=>{target.addEventListener(type,fn,capture);cleanups.push(()=>target.removeEventListener(type,fn,capture));};
 const kind={prop:'Light aircraft','twin-prop':'Twin propeller','four-jet':'Four-engine jet','twin-jet':'Twin-engine jet',ufo:'Fictional aircraft'};
 for(const model of aircraft){
  const button=doc.createElement('button');button.type='button';button.dataset.aircraft=model.id;button.setAttribute('role','menuitemradio');button.tabIndex=-1;
  const icon=doc.createElement('span');icon.className='aircraft-symbol';icon.setAttribute('aria-hidden','true');icon.textContent=model.kind==='ufo'?'◉':'✈';
  const name=doc.createElement('span'),title=doc.createElement('b'),detail=doc.createElement('small');title.textContent=model.label;detail.textContent=`${kind[model.kind]} · ${model.approximate?'approx. ':''}${model.length.toFixed(1)} m`;name.append(title,detail);
  const check=doc.createElement('span');check.className='aircraft-check';check.setAttribute('aria-hidden','true');check.textContent='✓';button.append(icon,name,check);menu.append(button);items.set(model.id,button);
  listen(button,'click',()=>{close({restoreFocus:false});onSelect(model.id);});
 }
 function close({restoreFocus=true}={}){
  if(disposed||!open)return;open=false;panel.hidden=true;trigger.setAttribute('aria-expanded','false');doc.body.classList.remove('aircraft-picker-open');
  if(restoreFocus)trigger.focus({preventScroll:true});
 }
 function show({last=false}={}){
  if(disposed)return;onOpen();open=true;panel.hidden=false;trigger.setAttribute('aria-expanded','true');doc.body.classList.add('aircraft-picker-open');
  const item=last?[...items.values()].at(-1):items.get(current);item.focus({preventScroll:true});item.scrollIntoView({block:'nearest'});
 }
 function sync(state){
  current=items.has(state.id)?state.id:aircraft[0].id;
  for(const [id,button] of items)button.setAttribute('aria-checked',String(id===current));
  const name=aircraft.find(model=>model.id===current).label,loading=state.status==='loading',failed=state.status==='fallback';
  trigger.dataset.aircraftState=state.status;trigger.setAttribute('aria-label',`Choose aircraft: ${name}${loading?', loading':failed?', detailed model unavailable; retry in aircraft menu':''}`);
  trigger.title=`Choose aircraft · ${name} · 3 to fly`;doc.getElementById('aircraft-current').textContent=name;
 }
 listen(trigger,'click',()=>open?close():show());
 listen(trigger,'keydown',event=>{if(event.key!=='ArrowDown'&&event.key!=='ArrowUp')return;event.preventDefault();event.stopPropagation();show({last:event.key==='ArrowUp'});});
 listen(closeButton,'click',()=>close());
 listen(panel,'keydown',event=>{
  event.stopPropagation();
  if(event.key==='Tab'){close();return;}
  if(event.code==='Digit3'&&!event.repeat){event.preventDefault();close({restoreFocus:false});onQuickFly();return;}
  const rows=[...items.values()],index=rows.indexOf(doc.activeElement);let next;
  if(event.key==='ArrowDown')next=(index+1)%rows.length;else if(event.key==='ArrowUp')next=index<0?rows.length-1:(index+rows.length-1)%rows.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=rows.length-1;else return;
  event.preventDefault();rows[next].focus({preventScroll:true});rows[next].scrollIntoView({block:'nearest'});
 });
 listen(doc,'keydown',event=>{if(!open||event.key!=='Escape')return;event.preventDefault();event.stopImmediatePropagation();close();},true);
 listen(doc,'pointerdown',event=>{if(open&&!panel.contains(event.target)&&!trigger.contains(event.target))close({restoreFocus:false});},true);
 listen(doc,'focusin',event=>{if(open&&!panel.contains(event.target)&&!trigger.contains(event.target))close({restoreFocus:false});});
 sync({id:current,status:'loading'});
 return {open:show,close,sync,get state(){return {open,current,disposed};},dispose(){if(disposed)return;close({restoreFocus:false});disposed=true;for(const cleanup of cleanups)cleanup();}};
}
