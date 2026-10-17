"""Pure symbol-table regression; no importing owned numerical paths."""
from pathlib import Path
import builtins,symtable,unittest
HERE=Path(__file__).parent

def unbound_globals(path):
 table=symtable.symtable(path.read_text(),str(path),'exec');bound={s.get_name()for s in table.get_symbols()if s.is_assigned()or s.is_imported()or s.is_namespace()}|set(vars(builtins))|{'__file__','__name__','__package__','__spec__'};missing=set()
 def inspect(scope):
  for s in scope.get_symbols():
   if s.is_global()and s.is_referenced()and s.get_name()not in bound:missing.add(s.get_name())
  for child in scope.get_children():inspect(child)
 for child in table.get_children():inspect(child)
 return missing
class Tests(unittest.TestCase):
 def test_preserved_v1_History_NameError_detected(self):self.assertEqual(unbound_globals(HERE/'upton_certified6170_two_original_current_physical_v1_20261014.py'),{'HISTORY'})
 def test_v2_every_referenced_global_bound(self):self.assertEqual(unbound_globals(HERE/'upton_certified6170_two_original_current_physical_v2_20261014.py'),set())
if __name__=='__main__':unittest.main()
