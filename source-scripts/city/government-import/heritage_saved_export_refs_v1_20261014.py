"""Construct saved-export references using an actual filesystem Path root."""
def saved_export_refs(root,views,ref):
    return [ref(root/view[key])for view in views for key in ['cleanSolidImage','markedImage']]
