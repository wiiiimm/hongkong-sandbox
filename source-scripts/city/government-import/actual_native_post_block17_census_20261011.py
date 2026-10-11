"""Exact fixed actual baseline plus the two independently loaded current deltas."""
def exact_post_block17_census(old_uids,current_uids):
 assert len(old_uids)==len(set(old_uids))==6637
 assert len(current_uids)==len(set(current_uids))==6639
 assert set(current_uids)-set(old_uids)=={'landsd/255438:0','landsd/256116:0'}
 assert not set(old_uids)-set(current_uids)
 return True
