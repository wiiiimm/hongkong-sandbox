"""Retain the ordinary validated parent-edge return as an inset's terrain basis."""
import numpy as np
from resolve_pass_indexed_parent_clipping_v2 import validate_patch

def validated_template_faces(template, parent):
    # Validation is mandatory here as well as after the later source inset.
    validate_patch(template, parent)
    mesh=template['nativeMesh']
    vertices=np.asarray(mesh['position'],dtype=float).reshape(-1,3)
    faces=vertices[np.asarray(mesh['index']).reshape(-1,3)].copy()
    assert np.isfinite(faces).all() and len(faces)
    assert faces[:,:,1].min()>=1.2,'native-terrain-near-water-clamp'
    return faces
