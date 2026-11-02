"""Read ordinary/ZIP64 single-disk directories with bounded ETag-pinned ranges.

No archive allocation, payload download, larger transfer cap or source approval.
"""
import hashlib, io, struct, zipfile
MAX_DIRECTORY_BYTES=4*1024*1024


def metadata(tail,start,size):
    end=tail.rfind(b'PK\x05\x06'); assert end>=0 and end+22<=len(tail)
    _,disk,cd_disk,n_disk,total,cd_size,cd_offset,comment=struct.unpack('<4s4H2LH',tail[end:end+22])
    assert disk==cd_disk==0 and n_disk==total and end+22+comment==len(tail)
    directory_end=start+end; is64=total==65535 or cd_size==0xffffffff or cd_offset==0xffffffff
    if is64:
        assert end>=20
        sig,disk64,position,disks=struct.unpack('<4sLQL',tail[end-20:end])
        assert sig==b'PK\x06\x07' and disk64==0 and disks==1
        at=position-start; assert 0<=at and at+56<=end-20
        sig,length,_,_,disk64,cd_disk64,n_disk,total,cd_size,cd_offset=struct.unpack('<4sQ2H2L4Q',tail[at:at+56])
        assert sig==b'PK\x06\x06' and disk64==cd_disk64==0 and n_disk==total
        assert length>=44 and at+12+length==end-20
        directory_end=position
    assert start+len(tail)==size and 0<=cd_offset<directory_end<=size
    assert 0<cd_size<=MAX_DIRECTORY_BYTES and cd_offset+cd_size==directory_end
    assert 0<total<=cd_size//46
    return dict(zip64=is64,completeEntries=total,centralDirectoryBytes=cd_size,centralDirectoryOffset=cd_offset)


class TailFile(io.RawIOBase):
    """A read-only absolute file window; refuses reads of unrequested payload."""
    def __init__(self,raw,start,size):
        self.raw=raw;self.start=start;self.size=size;self.position=start
        assert start+len(raw)==size
    def seekable(self):return True
    def readable(self):return True
    def tell(self):return self.position
    def seek(self,offset,whence=0):
        target=offset if whence==0 else self.position+offset if whence==1 else self.size+offset if whence==2 else -1
        assert self.start<=target<=self.size,'Attempt to seek outside acquired ZIP directory window'
        self.position=target;return target
    def read(self,n=-1):
        n=self.size-self.position if n<0 else min(n,self.size-self.position)
        at=self.position-self.start;value=self.raw[at:at+n];self.position+=len(value);return value


def parse_window(raw,start,size,meta):
    with zipfile.ZipFile(TailFile(raw,start,size)) as archive:
        entries=sorted(archive.infolist(),key=lambda e:e.header_offset)
    assert len(entries)==meta['completeEntries'] and len({e.filename for e in entries})==len(entries)
    assert all(0<=e.header_offset<meta['centralDirectoryOffset'] for e in entries)
    return entries


def fetch(net,url):
    _,head=net.get(url,0,method='HEAD');etag=head.get('ETag');size=int(head['Content-Length']);assert etag
    tail,h=net.get(url,65536,'-65536',etag)
    span,total=h['Content-Range'].split()[1].split('/');start,end=map(int,span.split('-'))
    assert int(total)==size and end+1==size and end-start+1==len(tail)
    meta=metadata(tail,start,size)
    offset=meta['centralDirectoryOffset'];raw=tail
    if offset<start:
        length=start-offset;assert length<=MAX_DIRECTORY_BYTES
        prefix,ph=net.get(url,length,f'{offset}-{start-1}',etag)
        assert ph['Content-Range']==f'bytes {offset}-{start-1}/{size}' and len(prefix)==length
        raw=prefix+tail;start=offset
    entries=parse_window(raw,start,size,meta)
    _,after=net.get(url,0,method='HEAD');assert after.get('ETag')==etag and int(after['Content-Length'])==size
    directory=raw[offset-start:]
    check=dict(meta,directorySHA256=hashlib.sha256(directory).hexdigest())
    return entries,check,directory,dict(etag=etag,archiveBytes=size)
