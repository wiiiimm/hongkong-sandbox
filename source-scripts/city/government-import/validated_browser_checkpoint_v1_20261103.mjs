/** Persist already validated evidence only; a checkpoint is never a passing report. */
import {readFile,writeFile,mkdir,rename,realpath} from 'node:fs/promises';
import {resolve,relative,isAbsolute} from 'node:path';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export async function createCheckpoint({root,out,inputRefs,configPath,harnessPath}){
 root=resolve(root);out=resolve(out);
 const inside=p=>{const r=relative(root,resolve(p));assert(r&&!isAbsolute(r)&&r!=='..'&&!r.startsWith('../'));return resolve(p);};
 inside(out);assert(Array.isArray(inputRefs)&&inputRefs.length>0);
 const seen=new Set();
 for(const ref of inputRefs){assert(typeof ref.path==='string'&&/^[a-f0-9]{64}$/.test(ref.sha256));const p=inside(await realpath(inside(resolve(root,ref.path))));assert(!seen.has(p));seen.add(p);assert.equal(sha(await readFile(p)),ref.sha256,'Checkpoint input differs: '+ref.path);}
 const binding={inputRefs,configSHA256:sha(await readFile(inside(await realpath(inside(configPath))))),harnessSHA256:sha(await readFile(inside(await realpath(inside(harnessPath)))))};
 await mkdir(out,{recursive:true});inside(await realpath(out));const bindingBytes=Buffer.from(JSON.stringify(binding,null,2)+'\n');await writeFile(resolve(out,'checkpoint-inputs.json'),bindingBytes);
 const hashes=new Map();
 return async report=>{
  assert.deepEqual(report.errors,[]);
  const rows=[...(report.views||[]),...(report.retainedNativeOwnViews||[])].filter(r=>'time'in r),files=new Set(),images=[];
  for(const r of rows){assert(r.active&&r.visible&&r.fullyFramed&&r.fallbackFaces===0&&r.sourcePixelVisibility.visiblePixels>=32);assert(/^[a-f0-9]{64}$/.test(r.sourceSHA256));assert(typeof r.file==='string'&&!r.file.includes('/')&&!r.file.includes('\\'));assert(!files.has(r.file));files.add(r.file);const p=inside(await realpath(inside(resolve(out,r.file))));if(!hashes.has(r.file))hashes.set(r.file,sha(await readFile(p)));images.push({file:r.file,sha256:hashes.get(r.file)});}
  const {passed,...partialReport}=report;
  const checkpoint={partialEvidenceOnly:true,softwareReportComplete:false,installationApproved:false,visualAcceptance:false,
   inputBindingSHA256:sha(bindingBytes),validatedCaptureCount:rows.length,images,report:partialReport};
  const destination=resolve(out,'validated-browser-checkpoint.json'),temporary=destination+'.part';
  await writeFile(temporary,JSON.stringify(checkpoint,null,2)+'\n');await rename(temporary,destination);
 };
}
