"""Merge overlapping verified groups; reject duplicated/stale per-source forms."""
def add_form(output,seen,record):
    uid=record['building']['uid']
    assert uid not in seen,'Ambiguous current source tile within one group'
    seen.add(uid)
    if uid in output:
        assert output[uid]==record,'Conflicting current group form or source tile'
    else:output[uid]=record
