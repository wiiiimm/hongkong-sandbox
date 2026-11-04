"""One exact Star native gzip container restoration; no source data changes."""
import gzip,hashlib
SOURCE='b90c8c210eb616c45b8068c0718ee6d34ab938f36b518564cf207c57c5b77104'
NATIVE='8aab8a53040a9a21227a307d7ca2c344a783fae8d9274b7c2c1e8317b7766f62'
GLB='7b5a937c0f92ffd24ba8717f4bd45eccaf97d7ba87059db92b15bb7070e3cd08'
def restore(data):
 h=lambda b:hashlib.sha256(b).hexdigest()
 assert len(data)==2262 and h(data)==SOURCE and data[:10]==bytes.fromhex('1f8b0800000000000203')
 original=gzip.decompress(data);assert len(original)==10440 and h(original)==GLB
 native=data[:9]+bytes([255])+data[10:]
 assert h(native)==NATIVE and native[:9]==data[:9]and native[10:]==data[10:]
 assert gzip.decompress(native)==original
 return native,{'sourceCompressedSHA256':SOURCE,'nativeCompressedSHA256':NATIVE,'sourceOSByte':3,'nativeOSByte':255,'changedByteOffsets':[9],'completeDeflateAndTrailerBytesIdentical':True,'completeDecodedGLBBytesIdentical':True,'decodedGLBSHA256':GLB,'decodedGLBBytes':10440,'nativeHashRelabelled':False,'sourceGeometryChanges':0,'sourcePoseChanges':0}
