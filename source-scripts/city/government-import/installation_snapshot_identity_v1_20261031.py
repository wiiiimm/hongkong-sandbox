"""Keep distinct publication attempts from reseeding the same review snapshot."""
import hashlib
from run import jobs

def identity(ordered_parts,acceptance,transaction_batch):
    if not isinstance(transaction_batch,str)or not transaction_batch.startswith('government-xl-')or acceptance.get('transactionBatch')!=transaction_batch:
        raise ValueError('Installation snapshot requires its exact transactionBatch binding')
    return hashlib.sha256(jobs.encode([ordered_parts,acceptance]).encode()).hexdigest()[:16]
