"""Audit both unchanged Festival Walk components against the joint candidate."""
import importlib.util
from run import ROOT,HERE,read,save,reservations
spec=importlib.util.spec_from_file_location('festival_pair_foundation',HERE/'xl-phase-one-foundation.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
DOC=ROOT/'docs/astra-city/government-import/government-xl-remaining-20260923/festival-pair-rescue-diagnostic-20261002'
def run():
    receipt=read(HERE/'local/sol-pilot-20261002/reservation.json');assert reservations.owns(receipt)
    reservations.heartbeat(receipt)
    rows=read(DOC/'selection.json.gz')['rows'];outputs=[]
    for row in rows:
        audit.UID=row['uid'];audit.DOC=DOC;audit.LOCAL=HERE/'local/government-xl-festival-pair-foundation-20261002'
        audit.SELECTION=DOC/('foundation-selection-'+row['uid'].split('/')[1].replace(':','-')+'.json.gz')
        audit.OUTPUT=DOC/('foundation-'+row['uid'].split('/')[1].replace(':','-')+'.json')
        save(audit.SELECTION,{'rows':[row]});audit.run();outputs.append(read(audit.OUTPUT))
    save(DOC/'foundation.json',{'rows':outputs,'aiCalls':0,'modelGeometryChanges':0,'publication':False})
if __name__=='__main__':run()
