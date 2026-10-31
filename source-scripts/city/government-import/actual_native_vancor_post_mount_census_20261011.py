"""Exact named baseline/current native delta census; no acceptance."""
DELTA=['landsd/239465:0','landsd/75782:0','landsd/261717:0']
def exact_census(old,current):
 assert len(old)==len(set(old))==6639 and len(current)==len(set(current))==6642
 assert set(old)<=set(current)and set(current)-set(old)==set(DELTA)
 return True
