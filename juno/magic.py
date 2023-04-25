from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic, needs_local_scope)
from .juno import chat, debug, edit, feedback
from .serialize_context import variable_description
from .client_setup import setup

@magics_class
class Assistant(Magics):

    @line_magic
    @needs_local_scope
    def chat(self, line, local_ns=None):
        return chat(line, variable_description(local_ns))
    
    @line_magic
    @needs_local_scope
    def juno(self, line, local_ns=None):
        return chat(line, variable_description(local_ns))
    
    @line_magic
    @needs_local_scope
    def j(self, line, local_ns=None):
        return chat(line, variable_description(local_ns))

    @line_magic
    @needs_local_scope
    def edit(self, line, local_ns=None):
        return edit(line, variable_description(local_ns))

    @line_magic
    @needs_local_scope
    def debug(self, line, local_ns=None):
        return debug(line, variable_description(local_ns))
    
    @line_magic
    @needs_local_scope
    def feedback(self, line, local_ns=None):
        return feedback(line)

_loaded = False
def load_ipython_extension(ip, **kwargs):
    """Load the extension in IPython."""
    global _loaded
    if not _loaded:
        ip.register_magics(Assistant)
        setup()
        _loaded = True
    else:
        setup()

def unload_ipython_extension(ip):
    global _loaded
    if _loaded:
        _loaded = False