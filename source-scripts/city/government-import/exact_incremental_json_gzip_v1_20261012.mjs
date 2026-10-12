/** Serialization only: JSON.stringify semantics for plain renderer packets,
 * bounded UTF-8 fragments, atomic gzip output. No geometry or input changes. */
import assert from 'node:assert/strict';
import {createWriteStream,existsSync,renameSync} from 'node:fs';
import {Readable} from 'node:stream';
import {pipeline} from 'node:stream/promises';
import {createGzip} from 'node:zlib';

function prepared(value,key){
  if((typeof value==='object'&&value!==null)||typeof value==='bigint'){
    const fn=value.toJSON;
    if(typeof fn==='function')value=fn.call(value,key);
  }
  if(value!==null&&typeof value==='object'){
    // Intrinsic valueOf rejects spoofed tags instead of silently losing data.
    const tag=Object.prototype.toString.call(value);
    if(tag==='[object Number]')value=Number.prototype.valueOf.call(value);
    else if(tag==='[object String]')value=String.prototype.valueOf.call(value);
    else if(tag==='[object Boolean]')value=Boolean.prototype.valueOf.call(value);
    else if(tag==='[object BigInt]')value=BigInt.prototype.valueOf.call(value);
  }
  return value;
}
const omitted=value=>value===undefined||typeof value==='function'||typeof value==='symbol';
function* quoted(value){
  yield '"';let chunk='';
  for(let i=0;i<value.length;i++){
    const c=value.charCodeAt(i);let piece;
    if(c===34)piece='\\"';else if(c===92)piece='\\\\';
    else if(c===8)piece='\\b';else if(c===9)piece='\\t';
    else if(c===10)piece='\\n';else if(c===12)piece='\\f';else if(c===13)piece='\\r';
    else if(c<32)piece='\\u'+c.toString(16).padStart(4,'0');
    else if(c>=0xd800&&c<=0xdbff){
      const d=value.charCodeAt(i+1);
      if(d>=0xdc00&&d<=0xdfff){piece=value.slice(i,i+2);i++;}
      else piece='\\u'+c.toString(16).padStart(4,'0');
    }else if(c>=0xdc00&&c<=0xdfff)piece='\\u'+c.toString(16).padStart(4,'0');
    else piece=value[i];
    // Never divide a valid surrogate pair between UTF-8 fragments.
    if(chunk.length+piece.length>1024){yield chunk;chunk='';}
    chunk+=piece;
  }
  if(chunk)yield chunk;yield '"';
}
function* tokens(value,ancestors){
  if(value===null){yield 'null';return;}
  const type=typeof value;
  if(type==='string'){yield* quoted(value);return;}
  if(type==='number'){yield Number.isFinite(value)?JSON.stringify(value):'null';return;}
  if(type==='boolean'){yield value?'true':'false';return;}
  if(type==='bigint')throw new TypeError('Do not know how to serialize a BigInt');
  assert(type==='object','Value must be prepared before serialization');
  if(ancestors.has(value))throw new TypeError('Converting circular structure to JSON');
  if(!Array.isArray(value)&&![Object.prototype,null].includes(Object.getPrototypeOf(value)))throw new TypeError('Unsupported nonplain captured JSON container');
  ancestors.add(value);
  try{
    if(Array.isArray(value)){
      yield '[';const length=value.length;
      for(let i=0;i<length;i++){
        if(i)yield ',';
        const child=prepared(value[i],String(i));
        if(omitted(child))yield 'null';else yield* tokens(child,ancestors);
      }
      yield ']';
    }else{
      yield '{';let first=true;
      for(const key of Object.keys(value)){
        const child=prepared(value[key],key);if(omitted(child))continue;
        if(!first)yield ',';first=false;
        yield* quoted(key);yield ':';yield* tokens(child,ancestors);
      }
      yield '}';
    }
  }finally{ancestors.delete(value);}
}
export function* exactJsonUtf8Fragments(value,{maxFragmentBytes=65536}={}){
  assert(Number.isInteger(maxFragmentBytes)&&maxFragmentBytes>=16&&maxFragmentBytes<=1048576);
  const root=prepared(value,'');if(omitted(root))return;
  let chunk='',size=0;
  for(const token of tokens(root,new Set())){
    const tokenBytes=Buffer.byteLength(token);
    if(tokenBytes<=maxFragmentBytes){
      if(size+tokenBytes>maxFragmentBytes){yield Buffer.from(chunk,'utf8');chunk='';size=0;}
      chunk+=token;size+=tokenBytes;continue;
    }
    // tokens are bounded except primitive numeric output (at most 24 bytes).
    // Split only at Unicode code-point boundaries, even with tiny test budgets.
    for(let start=0;start<token.length;){
      let end=start,bytes=0;
      while(end<token.length){
        const cp=token.codePointAt(end),units=cp>0xffff?2:1;
        const n=Buffer.byteLength(token.slice(end,end+units));
        if(bytes+n>maxFragmentBytes)break;bytes+=n;end+=units;
      }
      assert(end>start);
      if(size+bytes>maxFragmentBytes){yield Buffer.from(chunk,'utf8');chunk='';size=0;}
      chunk+=token.slice(start,end);size+=bytes;start=end;
    }
  }
  if(chunk)yield Buffer.from(chunk,'utf8');
}
export async function writeExactJsonGzip(path,value,options={}){
  const target=path instanceof URL?path:new URL(path,'file://'+process.cwd()+'/');
  const partial=new URL(target.href+'.serialization-partial');
  assert(!existsSync(target)&&!existsSync(partial),'Never overwrite an output or failed serialization');
  let fragments=0,uncompressedBytes=0;
  function* counted(){for(const b of exactJsonUtf8Fragments(value,options)){fragments++;uncompressedBytes+=b.length;yield b;}}
  await pipeline(Readable.from(counted()),createGzip(),createWriteStream(partial,{flags:'wx'}));
  assert(fragments>0,'Undefined root has no JSON representation');
  assert(!existsSync(target),'Output appeared during serialization');renameSync(partial,target);
  return {fragments,uncompressedBytes};
}
