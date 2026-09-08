"""Create a private branch-bound worker environment from Vercel's pulled credentials."""
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from dotenv import dotenv_values
from db import CONFIG, ROOT, connection_parameters


def configure(source):
    values=dotenv_values(source)
    original=values.get('DATABASE_URL_UNPOOLED')
    if not original:raise ValueError('Pulled environment lacks DATABASE_URL_UNPOOLED')
    parsed=urlsplit(original)
    if parsed.scheme not in ('postgres','postgresql') or not parsed.username or not parsed.password:
        raise ValueError('Expected authenticated Postgres URL (values withheld)')
    # Credentials are inherited by the dedicated branch. Only use the explicitly pinned endpoint.
    url=urlunsplit((parsed.scheme,parsed.netloc.rsplit('@',1)[0]+'@'+CONFIG['host'],
                   '/'+CONFIG['database'],parsed.query,''))
    connection_parameters(url)
    output=ROOT/'.env.modelling'
    fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:f.write('MODELLING_DATABASE_URL='+json.dumps(url)+'\n')
    return {'branch':CONFIG['branch_name'],'file':str(output),'next':'Run db.py check before any jobs'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vercel-env',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(configure(a.vercel_env)))
