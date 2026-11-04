/** Browser-only diagnostic. Restore every material/background before returning. */
export function installSourcePixelWitness(){
 window.__portSourceVisibility=uid=>{
  const r=window.__port,d=r.stream.detailedModels.get(uid);
  if(!d?.active)return{visiblePixels:0,active:false};
  const target=new Set(d.meshes),saved=[],temporary=[],background=r.scene.background;
  try{
   r.scene.background=new r.THREE.Color(0x000000);
   r.scene.traverse(o=>{
    if(!o.isMesh)return;
    saved.push([o,o.material]);
    const mats=Array.isArray(o.material)?o.material:[o.material];
    const replaced=mats.map(old=>{
     const m=new r.THREE.MeshBasicMaterial({color:target.has(o)?0xff00ff:0x000000,side:old.side,toneMapped:false,fog:false});
     temporary.push(m);return m;
    });
    o.material=Array.isArray(o.material)?replaced:replaced[0];
   });
   window.__portDraw(r.scene,r.camera);
   const gl=r.renderer.getContext(),pixels=new Uint8Array(gl.drawingBufferWidth*gl.drawingBufferHeight*4);
   gl.readPixels(0,0,gl.drawingBufferWidth,gl.drawingBufferHeight,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
   let visiblePixels=0;
   for(let i=0;i<pixels.length;i+=4)if(pixels[i]>200&&pixels[i+1]<50&&pixels[i+2]>200)visiblePixels++;
   return{active:true,visiblePixels,bufferWidth:gl.drawingBufferWidth,bufferHeight:gl.drawingBufferHeight,
    otherMeshesRetainedAsOpaqueOccluders:true,sourceGeometryChanged:false,cameraSearch:window.__portVisibilityCameras?.[uid]??null};
  }finally{
   for(const[o,material]of saved)o.material=material;
   r.scene.background=background;
   for(const m of temporary)m.dispose();
   window.__portDraw(r.scene,r.camera);
  }
 };
 window.__portChooseVisibleCamera=uid=>{
  const r=window.__port,model=r.officialModels.models.get(uid),[a,b]=model.worldBounds;
  const originalCamera=r.camera.position.clone(),originalTarget=r.controls.target.clone(),originalDamping=r.controls.enableDamping;
  const centre=new r.THREE.Vector3(...a).add(new r.THREE.Vector3(...b)).multiplyScalar(.5),options=[];
  try{
   r.controls.enableDamping=false;
   for(const elevation of [.6,1.2])for(let angle=0;angle<360;angle+=45){
    const az=r.THREE.MathUtils.degToRad(angle),direction=new r.THREE.Vector3(Math.sin(az),elevation,Math.cos(az)).normalize();
    const right=new r.THREE.Vector3().crossVectors(new r.THREE.Vector3(0,1,0),direction).normalize(),up=new r.THREE.Vector3().crossVectors(direction,right);
    const tanV=Math.tan(r.THREE.MathUtils.degToRad(r.camera.fov/2)),tanH=tanV*r.camera.aspect;
    let distance=0;
    for(const x of [a[0],b[0]])for(const y of [a[1],b[1]])for(const z of [a[2],b[2]]){
     const offset=new r.THREE.Vector3(x,y,z).sub(centre);
     distance=Math.max(distance,offset.dot(direction)+Math.abs(offset.dot(right))/tanH,offset.dot(direction)+Math.abs(offset.dot(up))/tanV);
    }
    r.camera.position.copy(centre).addScaledVector(direction,distance*1.08);r.controls.target.copy(centre);r.controls.update();r.camera.updateMatrixWorld(true);
    const witness=window.__portSourceVisibility(uid);
    options.push({azimuth:angle,elevation,camera:r.camera.position.toArray(),visiblePixels:witness.visiblePixels});
   }
   options.sort((a,b)=>b.visiblePixels-a.visiblePixels);
   if(options[0].visiblePixels<32)throw Error('No unobstructed diagnostic source camera: '+uid);
   r.camera.position.fromArray(options[0].camera);r.controls.target.copy(centre);r.controls.update();r.camera.updateMatrixWorld(true);
   (window.__portVisibilityCameras??={})[uid]={selected:options[0],candidates:options,allOriginalGeometryRetained:true};
   return window.__portVisibilityCameras[uid];
  }catch(error){
   r.camera.position.copy(originalCamera);r.controls.target.copy(originalTarget);r.controls.enableDamping=originalDamping;r.controls.update();r.camera.updateMatrixWorld(true);throw error;
  }
 };
}
