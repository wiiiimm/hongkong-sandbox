"""Use the existing fenced publisher with every installed terrain-family verifier."""
import runpy
from pathlib import Path
from fuying_five_member_terrain_stage_v1_20261029 import complete_boundary_validators

if __name__=='__main__':
    with complete_boundary_validators():
        runpy.run_path(str(Path(__file__).resolve().parents[1]/'model-integration-20260909/publish.py'),run_name='__main__')
