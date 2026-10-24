"""Rebind the unchanged reviewed identity kernel to a fresh complete capture."""
import importlib.util
from run import ROOT,HERE
from tung_sing_adjacent_original_envelope_identity_20261010 import UID,RELATED,POLICY
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-nested-current-identity-inputs-20261010'
def adapter():
 s=importlib.util.spec_from_file_location('tung_sing_fresh_nested_adapter',HERE/'tung_sing_current_bound_identity_20261010.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.DOC=DOC
 return m
def verify_files(row,context,local):return adapter().verify_files(row,context,local)
def native_rows(connection):return adapter().native_rows(connection)
def verify_receipt(receipt):return adapter().verify_receipt(receipt)
