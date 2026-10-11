"""Fresh production replay, identity only; no source edits or physical credit."""
from run import ROOT,HERE,read,save
from tung_sing_current_bound_identity_20261010 import verify_files
INPUT=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-current-full-cell-preflight-20261010'
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-current-bound-identity-promotion-20261010'
def main():
 assert not DOC.exists();row=read(INPUT/'selection.json.gz')['rows'][0];context=read(INPUT/'context.json.gz')['rows'][0]
 proof=verify_files(row,context,HERE/'local'/DOC.name)
 save(DOC/'identity-proof.json.gz',proof);save(DOC/'selection.json.gz',read(INPUT/'selection.json.gz'));save(DOC/'context.json.gz',read(INPUT/'context.json.gz'));print({'passed':proof['passed'],'reasons':proof['reasons'],'physicalAccepted':proof['physicalAccepted']},flush=True)
if __name__=='__main__':main()
