from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic, needs_local_scope)
from .juno import chat
from .serialize_context import describe_variables
from .client_setup import setup

@magics_class
class Assistant(Magics):

    @line_magic
    @needs_local_scope
    def chat(self, line, local_ns=None):
        return chat(line, describe_variables(local_ns))


_loaded = False
def load_ipython_extension(ip, **kwargs):
    """Load the extension in IPython."""
    global _loaded
    if not _loaded:
        ip.register_magics(Assistant)
        setup()
        _loaded = True

def unload_ipython_extension(ip):
    global _loaded
    if _loaded:
        magic = ip.magics_manager.registry.pop('MatlabMagics')
        magic.Matlab.stop()
        _loaded = False