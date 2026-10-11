const codecPromises=new Map();

export function modelCodecSupported(codec){
 return codec==='none'||codec==='meshopt'||codec==='draco';
}

export async function loadModelCodec(codec,{loadDraco=()=>import('../vendor/DRACOLoader.js')}={}){
 if(!codec||codec==='none')return null;
 if(!modelCodecSupported(codec))throw new Error(`Unsupported model codec: ${codec}`);
 if(!codecPromises.has(codec))codecPromises.set(codec,(async()=>{
  if(codec==='meshopt'){
   const {MeshoptDecoder}=await import('../vendor/meshopt_decoder.module.js');
   if(typeof window==='object'&&typeof Worker==='function'&&typeof MeshoptDecoder.useWorkers==='function')MeshoptDecoder.useWorkers(1);
   await MeshoptDecoder.ready;
   return {codec,decoder:MeshoptDecoder};
  }
  const {DRACOLoader}=await loadDraco();
  const loader=new DRACOLoader();
  loader.setDecoderPath(new URL('../vendor/',import.meta.url).href);
  loader.setWorkerLimit(1);
  try{await loader._initDecoder();}
  catch(error){loader.dispose();throw error;}
  return {codec,loader};
 })());
 try{return await codecPromises.get(codec);}
 catch(error){codecPromises.delete(codec);throw error;}
}
