"""A closed console must never roll back a completed model installation."""
import builtins,os,sys

def status(*values,**options):
    options.setdefault('flush',True)
    try:
        builtins.print(*values,**options)
        return True
    except BrokenPipeError:
        # Only a cosmetic stdout message is recoverable. File/log failures and
        # all publication/validation exceptions still propagate normally.
        if options.get('file') not in (None,sys.stdout):raise
        sink=os.open(os.devnull,os.O_WRONLY)
        try:os.dup2(sink,sys.stdout.fileno())
        finally:os.close(sink)
        return False
