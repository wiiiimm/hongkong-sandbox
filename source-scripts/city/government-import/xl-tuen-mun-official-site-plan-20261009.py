"""Preserve and render the official 2015 hospital site plan with verified TLS.

The host omits an intermediate certificate. Validate that public intermediate
against the system trust store, then include it in this one acquisition context.
No certificate verification or hostname checks are disabled.
"""
import gzip, ssl, subprocess, sys, urllib.request
from pathlib import Path
import pymupdf
from run import ROOT, HERE, save, digest
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request

DOC=ROOT/'docs/astra-city/government-import/government-xl-tuen-mun-official-site-plan-20261009'
URL='https://www.legco.gov.hk/yr14-15/english/panels/hs/papers/hs20150518cb2-1456-5-e.pdf'
ISSUER='https://www1.ecert.gov.hk/root/ecert_ssl_ca_3-17.crt'

def main():
 DOC.mkdir(exist_ok=True)
 p=DOC/'official-site-plan-20150518.pdf'
 assert not p.exists(), 'Keep completed acquisition immutable'
 raw,receipt=request(ISSUER,json_expected=False)
 pem=ssl.DER_cert_to_PEM_cert(raw)
 cert=DOC/'official-public-intermediate.pem';cert.write_text(pem)
 save(DOC/'official-public-intermediate.request.json',receipt)
 checked=subprocess.run(['openssl','verify','-CAfile','/etc/ssl/certs/ca-certificates.crt',str(cert)],check=True,capture_output=True,text=True)
 context=ssl.create_default_context();context.load_verify_locations(cafile=str(cert))
 assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED
 urllib.request.install_opener(urllib.request.build_opener(urllib.request.HTTPSHandler(context=context)))
 raw,receipt=request(URL,json_expected=False)
 decoded=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
 assert decoded.startswith(b'%PDF')
 p.write_bytes(decoded)
 save(DOC/'official-site-plan-20150518.request.json',{**receipt,'decodedSHA256':digest(decoded),'gzipDecoded':raw!=decoded,'tlsHostnameVerification':True,'tlsCertificateVerification':True,'missingIntermediateVerifiedAgainstSystemRoots':checked.stdout.strip(),'publicIntermediateSHA256':digest(cert.read_bytes())})
 pdf=pymupdf.open(p);assert len(pdf)==6
 pages=[dict(pageIndex=n,text=page.get_text()) for n,page in enumerate(pdf)]
 pdf[5].get_pixmap(matrix=pymupdf.Matrix(3,3)).save(DOC/'official-site-plan-page-6.png')
 save(DOC/'official-site-plan-page-text.json',dict(sourcePDFSHA256=digest(decoded),pages=pages))
 print(dict(pdfBytes=len(decoded),pages=len(pdf),renderedSitePlanPage=6),flush=True)

if __name__=='__main__':main()
