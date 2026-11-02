"""Retain exact FBX byte strings while making display text JSONB-compatible."""
import json

def jsonb_literals(value):
    if isinstance(value,list):return [jsonb_literals(v)for v in value]
    if isinstance(value,dict):
        byte_literal='rawBytesHex'in value and 'decodedUTF8'in value
        result={k:jsonb_literals(v)for k,v in value.items()if not(byte_literal and k=='decodedUTF8')}
        if byte_literal:
            decoded=bytes.fromhex(value['rawBytesHex']).decode('utf8',errors='replace')
            assert decoded==value['decodedUTF8']
            result['decodedUTF8Escaped']=json.dumps(decoded,ensure_ascii=True)[1:-1]
        return result
    if isinstance(value,str):assert '\0'not in value,'Unbound NUL text needs an exact original byte literal'
    return value
