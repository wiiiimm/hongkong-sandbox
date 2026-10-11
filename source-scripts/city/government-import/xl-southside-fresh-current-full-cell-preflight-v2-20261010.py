"""Distinct fresh current full-cell capture after hospital publication."""
import importlib.util
from run import ROOT,HERE
def main():
 s=importlib.util.spec_from_file_location('southside_fresh_raw_v2',HERE/'xl-southside-current-full-cell-preflight-20261010.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.BATCH='government-xl-southside-fresh-current-full-cell-preflight-v2-20261010';m.DOC=ROOT/'docs/astra-city/government-import'/m.BATCH;m.LOCAL=HERE/'local'/m.BATCH;m.main()
if __name__=='__main__':main()
