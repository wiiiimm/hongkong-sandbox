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
    otherMeshesRetainedAsOpaqueOccluders:true,sourceGeometryChanged:false};
  }finally{
   for(const[o,material]of saved)o.material=material;
   r.scene.background=background;
   for(const m of temporary)m.dispose();
   window.__portDraw(r.scene,r.camera);
  }
 };
}
