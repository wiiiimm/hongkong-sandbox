"""Exact named baseline/current native delta census; no acceptance."""
DELTA=['landsd/95691:0','landsd/204145:0','landsd/204143:0']
def exact_census(old,current):
 assert len(old)==len(set(old))==6642 and len(current)==len(set(current))==6645
 assert set(old)<=set(current)and set(current)-set(old)==set(DELTA)
 return True
