// A depth-only separation for terrain coincident with an original model surface.
// Logarithmic fragment depth bypasses the material's fixed-function polygon offset.
// Positions, ray picking, collision and terrain sampling remain unchanged.
export function applyNativeTerrainDepthBias(material) {
 const previous=material.onBeforeCompile;
 material.onBeforeCompile=function(shader,renderer){
  previous.call(this,shader,renderer);
  const marker='#include <logdepthbuf_fragment>';
  if(!shader.fragmentShader.includes(marker))throw new Error('Native terrain depth shader contract changed');
  shader.fragmentShader=shader.fragmentShader.replace(marker,`${marker}
#if defined(USE_LOGDEPTHBUF) && defined(USE_LOGDEPTHBUF_EXT)
 if(vIsPerspective != 0.0) {
  // Preserve at least one depth-buffer step at distant viewpoints.
  gl_FragDepthEXT = max(gl_FragDepthEXT + 0.0000001, log2(vFragDepth + 0.005) * logDepthBufFC * 0.5);
 }
#endif`);
 };
 material.customProgramCacheKey=()=> 'native-terrain-log-depth-v1';
 return material;
}
